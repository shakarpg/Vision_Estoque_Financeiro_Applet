import os
import io
import json
from flask import Flask, request, jsonify
from google.cloud import aiplatform
# from google.cloud import storage # Se for usar Cloud Storage
# from google.cloud import firestore # Se for usar Firestore
from dotenv import load_dotenv

# Carrega variáveis de ambiente se estiver rodando localmente (opcional)
load_dotenv()

app = Flask(__name__)

# --- Configurações do Projeto GCP e Gemini ---
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION", "us-central1") # ou a região onde seu modelo Gemini está disponível
# O nome do modelo Gemini que você deseja usar (Flash 2.5 Pro)
# Para Flash 2.5 Pro, você pode usar "gemini-1.5-flash-001" ou o mais recente disponível
MODEL_ID = os.getenv("GEMINI_MODEL_ID", "gemini-1.5-flash-001") 

# Inicializa o cliente do Vertex AI (para interagir com o Gemini)
aiplatform.init(project=PROJECT_ID, location=LOCATION)
model = aiplatform.GenerativeModel(MODEL_ID)

# --- Endpoint principal para upload de imagem ---
@app.route('/upload-invoice', methods=['POST'])
def upload_invoice():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({"error": "No selected image"}), 400

    if image_file:
        try:
            # Lê a imagem como bytes
            image_bytes = image_file.read()

            # --- Chamar a API do Gemini para análise ---
            # O prompt é crucial para a qualidade da extração.
            # Adapte este prompt conforme os documentos que você espera.
            prompt = """
            Analise esta imagem que pode ser uma nota fiscal, etiqueta de produto ou documento de estoque.
            Extraia as seguintes informações em formato JSON, se presentes e identificáveis:
            {
              "tipo_documento": "Nota Fiscal" ou "Etiqueta de Produto" ou "Relatório de Contagem" ou "Desconhecido",
              "numero_documento": "<numero_da_nota_fiscal_ou_referencia>",
              "data_emissao": "<DD/MM/AAAA>",
              "fornecedor": "<nome_do_fornecedor>",
              "cnpj_fornecedor": "<CNPJ>",
              "itens": [
                {
                  "codigo_produto": "<codigo>",
                  "descricao": "<descricao_do_item>",
                  "quantidade": <quantidade_numerica>,
                  "unidade": "<unidade_medida>",
                  "valor_unitario": <valor_numerico>,
                  "valor_total_item": <valor_numerico>
                }
              ],
              "valor_total_documento": <valor_numerico>,
              "observacoes_adicionais": "<texto_livre_de_observacoes_ou_discrepancias>"
            }
            Se a informação não for encontrada, deixe o campo como `null` ou array vazio para "itens".
            Se for uma etiqueta, preencha apenas o que for relevante.
            Certifique-se de que a saída seja um JSON válido.
            """

            # Cria um objeto Part com a imagem
            image_part = {
                "inline_data": {
                    "mime_type": image_file.mimetype,
                    "data": io.BytesIO(image_bytes).read().hex() # Gemini espera base64 ou hex para inline_data
                }
            }

            # Envia o prompt e a imagem para o Gemini
            response = model.generate_content([prompt, image_part])

            # Pega a resposta de texto do Gemini
            gemini_output_text = response.text

            try:
                # Tenta parsear a saída do Gemini como JSON
                extracted_data = json.loads(gemini_output_text)
            except json.JSONDecodeError:
                # Se o Gemini não retornar JSON válido, retorna o texto bruto e um aviso
                return jsonify({
                    "message": "Gemini processed image, but output was not valid JSON.",
                    "gemini_raw_output": gemini_output_text,
                    "prompt_used": prompt
                }), 200

            # --- Aqui você pode integrar com outros serviços ---
            # Ex: Salvar em Cloud Storage (a imagem original e/ou o JSON extraído)
            # Ex: Salvar em Firestore/Cloud SQL
            # Ex: Enviar uma notificação para o Google Chat ou e-mail com os dados extraídos

            # Exemplo de como enviar para o financeiro (substitua com sua lógica real)
            notification_message = f"""
            **Relatório Vision Estoque-Financeiro**
            Tipo de Documento: {extracted_data.get("tipo_documento", "N/A")}
            Número: {extracted_data.get("numero_documento", "N/A")}
            Data: {extracted_data.get("data_emissao", "N/A")}
            Fornecedor: {extracted_data.get("fornecedor", "N/A")}
            Valor Total: R$ {extracted_data.get("valor_total_documento", "0.00")}

            **Itens:**
            """
            for item in extracted_data.get("itens", []):
                notification_message += (
                    f"- {item.get('descricao', 'N/A')} ({item.get('codigo_produto', 'N/A')}) "
                    f"Qtd: {item.get('quantidade', 'N/A')} {item.get('unidade', '')} "
                    f"Total: R$ {item.get('valor_total_item', '0.00')}\n"
                )
            notification_message += f"\nObservações: {extracted_data.get('observacoes_adicionais', 'Nenhuma')}"

            print(notification_message) # Para fins de log no Cloud Run

            return jsonify({
                "message": "Image processed successfully and data extracted.",
                "extracted_data": extracted_data,
                "notification_sent_summary": notification_message # Simula a notificação
            }), 200

        except Exception as e:
            app.logger.error(f"Error processing request: {e}", exc_info=True)
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    # Para rodar localmente: FLASK_ENV=development GCP_PROJECT_ID=your-project-id python main.py
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))