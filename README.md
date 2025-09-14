# Vision_Estoque_Financeiro_Applet
![image](vision.png)
## Descrição (Português - pt-br)

Este applet, desenvolvido no Google AI Studio e implantado via Cloud Run, tem como missão principal otimizar a comunicação e a integração de dados entre os departamentos de Estoque e Financeiro. Utilizando o poder do Gemini Flash 2.5 Pro para compreensão de imagem, o "Vision Estoque-Financeiro" transforma o processo de registro e validação de informações, minimizando erros e acelerando a tomada de decisões.

O problema de comunicação entre estoque e financeiro muitas vezes surge de processos manuais, digitação de dados e a falta de uma fonte única e visual da verdade. Nosso applet aborda isso permitindo que funcionários do estoque capturem informações visuais de forma rápida e eficiente, que são então processadas e estruturadas para o departamento financeiro.

## Problema Resolvido

A comunicação ineficiente entre estoque e financeiro pode levar a:
*   **Erros de Lançamento:** Digitação incorreta de códigos, quantidades ou valores.
*   **Atrasos:** Demora na conciliação de notas fiscais com entradas de estoque.
*   **Discrepâncias:** Dificuldade em identificar a causa de diferenças entre estoque físico e contábil.
*   **Falta de Evidência Visual:** Dificuldade em auditar ou verificar transações sem registros fotográficos.

## Funcionalidades Principais

*   **Entrada de Dados Simplificada:** Capture fotos de documentos de estoque (notas fiscais, etiquetas, relatórios de contagem) diretamente pelo applet.
*   **Compreensão de Imagem Multimodal (Gemini Flash 2.5 Pro):**
    *   **Extração de Texto (OCR):** Identifica e extrai texto de documentos (números de NF, fornecedores, valores, descrições).
    *   **Leitura de Códigos:** Reconhece códigos de barras e QR codes para identificação de produtos.
    *   **Reconhecimento de Elementos:** Potencial para identificar tipos de itens ou embalagens.
*   **Geração de Resumos Estruturados:** Transforma as informações visuais em resumos textuais claros e formatados, ideais para o departamento financeiro.
*   **Integração Flexível (Conceitual):** A saída estruturada pode ser enviada para sistemas de chat internos, e-mails ou outros sistemas (ERP) via APIs.
*   **Histórico e Auditoria:** Mantém um registro visual e textual das transações para referência futura e auditoria.

## Como Funciona

1.  **Captura da Imagem:** Um funcionário do estoque utiliza o applet para tirar uma foto de um documento (ex: nota fiscal de entrada de mercadoria, etiqueta de produto com código de barras, relatório de contagem).
2.  **Processamento Gemini:** A imagem é enviada para a API do Google Gemini Flash 2.5 Pro.
3.  **Extração de Informações:** O Gemini analisa a imagem, extraindo dados relevantes como número da nota fiscal, fornecedor, itens, quantidades, valores e códigos de produtos.
4.  **Geração de Resumo:** O applet compila as informações extraídas em um resumo legível e padronizado.
5.  **Comunicação:** O resumo é apresentado ao usuário para confirmação e, em seguida, enviado automaticamente para o canal de comunicação preferido do departamento financeiro.

## Benefícios

*   **Redução de Erros:** Minimiza erros de digitação e interpretação humana.
*   **Agilidade Operacional:** Acelera o registro de entradas/saídas e a conciliação financeira.
*   **Transparência e Evidência:** Fornece um registro visual auditável das transações.
*   **Otimização de Tempo:** Libera o tempo dos funcionários para tarefas de maior valor agregado.
*   **Melhora na Colaboração:** Facilita uma comunicação mais clara e precisa entre equipes.

## Tecnologias Utilizadas

*   **Google AI Studio:** Ambiente de desenvolvimento para prototipagem e teste do modelo Gemini.
*   **Gemini Flash 2.5 Pro API:** Para capacidades multimodais de compreensão de imagem em tempo real.
*   **Cloud Run:** Para implantação escalável, serverless e de baixo custo do backend do applet.
*   **Frontend (Conceitual):** Uma interface web ou móvel leve para interação do usuário (ex: HTML/CSS/JavaScript).

---

