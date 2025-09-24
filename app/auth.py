
"""
Módulo de autenticação (opcional)
"""
import os
import hashlib
from functools import wraps
from flask import request, jsonify, current_app
from flask_login import UserMixin

class User(UserMixin):
    """Classe básica de usuário para autenticação simples"""
    
    def __init__(self, user_id, username, password_hash):
        self.id = user_id
        self.username = username
        self.password_hash = password_hash
    
    @staticmethod
    def get(user_id):
        """Recupera usuário por ID (implementação básica)"""
        # Em produção, isso viria de um banco de dados
        users = {
            '1': User('1', 'admin', hash_password('admin123'))
        }
        return users.get(user_id)
    
    @staticmethod
    def authenticate(username, password):
        """Autentica usuário"""
        # Em produção, isso viria de um banco de dados
        if username == 'admin' and verify_password('admin123', hash_password('admin123')):
            return User('1', 'admin', hash_password('admin123'))
        return None

def hash_password(password):
    """Hash da senha usando SHA-256 (em produção, use bcrypt)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verifica senha"""
    return hash_password(password) == password_hash

def auth_required(f):
    """
    Decorator para rotas que requerem autenticação
    Só é aplicado se ENABLE_AUTH estiver True
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Se autenticação não estiver habilitada, pular verificação
        if not current_app.config.get('ENABLE_AUTH', False):
            return f(*args, **kwargs)
        
        # Verificar token de autenticação básica
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Token de autenticação necessário'}), 401
        
        try:
            # Implementação básica - em produção, use JWT ou similar
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            
            # Verificar se token é válido (implementação simplificada)
            expected_token = os.getenv('API_TOKEN', 'default-token')
            if token != expected_token:
                return jsonify({'error': 'Token inválido'}), 401
                
        except Exception as e:
            current_app.logger.warning(f'Auth error: {e}')
            return jsonify({'error': 'Erro de autenticação'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def generate_api_token():
    """Gera token de API simples"""
    import secrets
    return secrets.token_urlsafe(32)
