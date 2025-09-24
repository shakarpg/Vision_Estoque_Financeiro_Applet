
"""
Ponto de entrada principal da aplicação
"""
import os
from app import create_app
from app.config import config

# Determinar ambiente
config_name = os.getenv('FLASK_ENV', 'development')
if config_name not in config:
    config_name = 'default'

# Criar aplicação
app = create_app(config_name)

# Validar configurações obrigatórias
try:
    app.config['validate_required_config']()
except ValueError as e:
    app.logger.error(f'Configuration error: {e}')
    raise

if __name__ == '__main__':
    # Configurações para execução local
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    host = '127.0.0.1' if debug_mode else '0.0.0.0'
    port = int(os.getenv('PORT', 8080))
    
    app.logger.info(f'Starting Vision Estoque Financeiro on {host}:{port}')
    app.run(debug=debug_mode, host=host, port=port)
