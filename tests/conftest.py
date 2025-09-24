
"""
Configurações globais para testes
"""
import pytest
import os
import tempfile

@pytest.fixture(scope='session')
def temp_dir():
    """Diretório temporário para testes"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture(autouse=True)
def setup_test_env():
    """Configurar variáveis de ambiente para testes"""
    os.environ['GCP_PROJECT_ID'] = 'test-project'
    os.environ['GCS_BUCKET_NAME'] = 'test-bucket'
    os.environ['SECRET_KEY'] = 'test-secret-key'
    os.environ['ENABLE_AUTH'] = 'false'
    yield
    # Cleanup não necessário pois pytest limpa automaticamente
