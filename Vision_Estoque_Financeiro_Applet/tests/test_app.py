import pytest
from unittest.mock import patch, MagicMock
import os

# Importar a aplicação Flask do arquivo principal
# É necessário ajustar o path para que o import funcione corretamente
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Vision_Estoque_Financeiro_Applet.ai_studio_code import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_upload_invoice_no_file(client):
    """Testa o endpoint /upload-invoice sem fornecer um arquivo."""
    response = client.post("/upload-invoice")
    assert response.status_code == 400
    assert "No image file provided" in response.json["error"]

@patch("Vision_Estoque_Financeiro_Applet.ai_studio_code.storage.Client")
@patch("Vision_Estoque_Financeiro_Applet.ai_studio_code.vertexai.preview.generative_models.GenerativeModel")
def test_upload_invoice_empty_file(mock_generative_model, mock_storage_client, client):
    """Testa o endpoint /upload-invoice com um arquivo vazio."""
    # Mock do GCS e Gemini para evitar chamadas externas
    mock_storage_client.return_value.bucket.return_value.blob.return_value.upload_from_string.return_value = None
    mock_generative_model.return_value.generate_content.return_value.text = '{"tipo_documento": "Desconhecido"}'

    data = {"image": (io.BytesIO(b""), "empty.jpg")}
    response = client.post("/upload-invoice", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert "No selected image" in response.json["error"]

# Adicione mais testes aqui para cobrir outras funcionalidades
# Por exemplo, um teste para um upload bem-sucedido (mockando GCS e Gemini)
# e um teste para o caso de Gemini retornar JSON inválido.

