
"""
Rotas principais da aplicação
"""
import os
import io
import json
import tempfile
from flask import Blueprint, request, jsonify, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
from google.cloud import storage
from app.security import validate_file, sanitize_prompt
from app.auth import auth_required

# Criar blueprint
main_bp = Blueprint('main', __name__)

# Rate limiter específico para upload
limiter = Limiter(key_func=get_remote_address)

# Inicializar clientes (será feito no primeiro uso)
storage_client = None
model = None

def init_gcp_clients():
    """Inicializa os clientes do GCP de forma lazy"""
    global storage_client, model
    
    if storage_client is None:
        storage_client = storage.Client()
    
    if model is None:
        vertexai.init(
            project=current_app.config['GCP_PROJECT_ID'], 
            location=current_app.config['GCP_LOCATION']
        )
        model = GenerativeModel(current_app.config['GEMINI_MODEL_ID'])

@main_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'Vision Estoque Financeiro',
        'version': '2.0.0'
    }), 200

@main_bp.route('/upload-invoice', methods=['POST'])
@limiter.limit("10 per minute")
@auth_required
def upload_invoice():
    """
    Endpoint principal para upload e análise de documentos fiscais
    Rate limited para 10 uploads por minuto por IP
    """
    try:
        # Validar se arquivo foi enviado
        if 'image' not in request.files:
            current_app.logger.warning('Upload attempt without image file')
            return jsonify({'error': 'Nenhum arquivo de imagem fornecido'}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            current_app.logger.warning('Upload attempt with empty filename')
            return jsonify({'error': 'Nenhuma imagem selecionada'}), 400

        # Validar arquivo
        validation_result = validate_file(image_file)
        if not validation_result['valid']:
            current_app.logger.warning(f'File validation failed: {validation_result["error"]}')
            return jsonify({'error': validation_result['error']}), 400

        # Inicializar clientes GCP
        init_gcp_clients()

        # Processar arquivo de forma segura
        secure_name = secure_filename(image_file.filename)
        
        # Usar arquivo temporário para processamento
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'_{secure_name}') as temp_file:
            image_file.save(temp_file.name)
            
            # Upload para GCS
            bucket_name = current_app.config['GCS_BUCKET_NAME']
            bucket = storage_client.bucket(bucket_name)
            blob_name = f"invoices/{secure_name}"
            blob = bucket.blob(blob_name)
            
            with open(temp_file.name, 'rb') as f:
                blob.upload_from_file(f, content_type=image_file.mimetype)
            
            gcs_uri = f"gs://{bucket_name}/{blob_name}"
            
            # Limpar arquivo temporário
            os.unlink(temp_file.name)

        # Preparar prompt sanitizado
        base_prompt = """
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
              "valor_unitario": <valor_numerica>,
              "valor_total_item": <valor_numerica>
            }
          ],
          "valor_total_documento": <valor_numerica>,
          "observacoes_adicionais": "<texto_livre_de_observacoes_ou_discrepancias>"
        }
        Se a informação não for encontrada, deixe o campo como `null` ou array vazio para "itens".
        Se for uma etiqueta, preencha apenas o que for relevante.
        Certifique-se de que a saída seja um JSON válido.
        """
        
        sanitized_prompt = sanitize_prompt(base_prompt)

        # Chamar Gemini AI
        image_part = Part.from_uri(gcs_uri, mime_type=image_file.mimetype)
        response = model.generate_content([sanitized_prompt, image_part])
        
        gemini_output_text = response.text

        try:
            # Tentar parsear como JSON
            extracted_data = json.loads(gemini_output_text)
            
            # Validar estrutura básica do JSON retornado
            if not isinstance(extracted_data, dict):
                raise ValueError("Resposta não é um objeto JSON válido")
                
        except (json.JSONDecodeError, ValueError) as e:
            current_app.logger.warning(f'Gemini returned invalid JSON: {e}')
            return jsonify({
                'message': 'Imagem processada, mas a saída não foi um JSON válido.',
                'gemini_raw_output': gemini_output_text[:500],  # Limitar tamanho da resposta
                'error': 'Formato de resposta inválido'
            }), 200

        # Gerar relatório de notificação
        notification_message = generate_notification_message(extracted_data)
        
        current_app.logger.info(f'Successfully processed document: {secure_name}')
        
        return jsonify({
            'message': 'Imagem processada com sucesso e dados extraídos.',
            'extracted_data': extracted_data,
            'notification_summary': notification_message
        }), 200

    except Exception as e:
        current_app.logger.error(f'Error processing upload: {str(e)}', exc_info=True)
        return jsonify({'error': 'Erro interno do servidor'}), 500

def generate_notification_message(extracted_data):
    """Gera mensagem de notificação formatada"""
    try:
        message = f"""
**Relatório Vision Estoque-Financeiro**
Tipo de Documento: {extracted_data.get("tipo_documento", "N/A")}
Número: {extracted_data.get("numero_documento", "N/A")}
Data: {extracted_data.get("data_emissao", "N/A")}
Fornecedor: {extracted_data.get("fornecedor", "N/A")}
Valor Total: R$ {extracted_data.get("valor_total_documento", "0.00")}

**Itens:**
"""
        for item in extracted_data.get("itens", []):
            message += (
                f"- {item.get('descricao', 'N/A')} ({item.get('codigo_produto', 'N/A')}) "
                f"Qtd: {item.get('quantidade', 'N/A')} {item.get('unidade', '')} "
                f"Total: R$ {item.get('valor_total_item', '0.00')}\n"
            )
        
        message += f"\nObservações: {extracted_data.get('observacoes_adicionais', 'Nenhuma')}"
        return message
        
    except Exception as e:
        current_app.logger.error(f'Error generating notification: {e}')
        return "Erro ao gerar relatório de notificação"

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Endpoint de login (se autenticação estiver habilitada)"""
    if not current_app.config['ENABLE_AUTH']:
        return jsonify({'message': 'Autenticação não está habilitada'}), 200
    
    if request.method == 'POST':
        # Implementar lógica de login aqui
        return jsonify({'message': 'Login não implementado ainda'}), 501
    
    return jsonify({'message': 'Página de login'}), 200
