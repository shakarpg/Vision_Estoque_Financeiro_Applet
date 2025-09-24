
"""
Vision Estoque Financeiro Applet
Aplicação Flask segura para análise de documentos fiscais com Google Gemini AI
"""
import os
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_talisman import Talisman
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler

def create_app(config_name=None):
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações de segurança
    app.config.from_object('app.config.Config')
    
    # Configurar logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/vision_app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Vision Estoque Financeiro startup')
    
    # Inicializar extensões de segurança
    init_security_extensions(app)
    
    # Registrar blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Registrar error handlers
    register_error_handlers(app)
    
    return app

def init_security_extensions(app):
    """Inicializa todas as extensões de segurança"""
    
    # Rate Limiting
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    limiter.init_app(app)
    
    # CORS configurado de forma segura
    CORS(app, 
         origins=os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(','),
         methods=['GET', 'POST'],
         allow_headers=['Content-Type', 'Authorization'])
    
    # Headers de segurança com Talisman
    csp = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",
        'style-src': "'self' 'unsafe-inline'",
        'img-src': "'self' data: https:",
        'connect-src': "'self'",
        'font-src': "'self'",
        'object-src': "'none'",
        'media-src': "'self'",
        'frame-src': "'none'",
    }
    
    Talisman(app, 
             force_https=os.getenv('FLASK_ENV') == 'production',
             strict_transport_security=True,
             content_security_policy=csp)
    
    # Autenticação (se habilitada)
    if os.getenv('ENABLE_AUTH', 'false').lower() == 'true':
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = 'main.login'
        login_manager.login_message = 'Por favor, faça login para acessar esta página.'
        
        @login_manager.user_loader
        def load_user(user_id):
            from app.auth import User
            return User.get(user_id)

def register_error_handlers(app):
    """Registra handlers para erros comuns"""
    
    @app.errorhandler(400)
    def bad_request(error):
        app.logger.warning(f'Bad request: {error}')
        return {'error': 'Requisição inválida'}, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        app.logger.warning(f'Unauthorized access: {error}')
        return {'error': 'Acesso não autorizado'}, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        app.logger.warning(f'Forbidden access: {error}')
        return {'error': 'Acesso proibido'}, 403
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Recurso não encontrado'}, 404
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        app.logger.warning(f'File too large: {error}')
        return {'error': 'Arquivo muito grande'}, 413
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        app.logger.warning(f'Rate limit exceeded: {error}')
        return {'error': 'Muitas requisições. Tente novamente mais tarde.'}, 429
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal server error: {error}')
        return {'error': 'Erro interno do servidor'}, 500
