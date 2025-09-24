
"""
Módulo de segurança para validação de arquivos e sanitização
"""
import os
import re
import magic
from flask import current_app
from werkzeug.utils import secure_filename

# Tipos MIME permitidos
ALLOWED_MIME_TYPES = {
    'image/jpeg',
    'image/jpg', 
    'image/png',
    'image/gif',
    'image/tiff',
    'image/bmp',
    'application/pdf'
}

# Extensões permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'tiff', 'bmp'}

# Tamanho máximo de arquivo (16MB)
MAX_FILE_SIZE = 16 * 1024 * 1024

def validate_file(file):
    """
    Valida arquivo enviado verificando:
    - Extensão do arquivo
    - Tipo MIME
    - Tamanho do arquivo
    - Conteúdo do arquivo (magic numbers)
    """
    try:
        # Verificar se arquivo existe
        if not file or not file.filename:
            return {'valid': False, 'error': 'Arquivo não fornecido'}
        
        # Verificar extensão
        filename = secure_filename(file.filename.lower())
        if not filename or '.' not in filename:
            return {'valid': False, 'error': 'Nome de arquivo inválido'}
        
        extension = filename.rsplit('.', 1)[1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            return {'valid': False, 'error': f'Extensão não permitida. Permitidas: {", ".join(ALLOWED_EXTENSIONS)}'}
        
        # Verificar tamanho do arquivo
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset para o início
        
        if file_size > MAX_FILE_SIZE:
            return {'valid': False, 'error': f'Arquivo muito grande. Máximo: {MAX_FILE_SIZE // (1024*1024)}MB'}
        
        if file_size == 0:
            return {'valid': False, 'error': 'Arquivo vazio'}
        
        # Verificar tipo MIME usando python-magic
        file_content = file.read(1024)  # Ler apenas os primeiros 1024 bytes
        file.seek(0)  # Reset para o início
        
        try:
            mime_type = magic.from_buffer(file_content, mime=True)
            if mime_type not in ALLOWED_MIME_TYPES:
                return {'valid': False, 'error': f'Tipo de arquivo não permitido: {mime_type}'}
        except Exception as e:
            current_app.logger.warning(f'Could not determine MIME type: {e}')
            # Continuar sem verificação MIME se magic falhar
        
        return {'valid': True, 'filename': filename, 'size': file_size}
        
    except Exception as e:
        current_app.logger.error(f'File validation error: {e}')
        return {'valid': False, 'error': 'Erro na validação do arquivo'}

def sanitize_prompt(prompt):
    """
    Sanitiza prompt para prevenir injeção de prompt
    Remove ou escapa caracteres potencialmente perigosos
    """
    if not prompt:
        return ""
    
    # Remover caracteres de controle
    prompt = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', prompt)
    
    # Remover sequências que podem ser usadas para injeção
    dangerous_patterns = [
        r'ignore\s+previous\s+instructions',
        r'forget\s+everything',
        r'new\s+instructions',
        r'system\s*:',
        r'assistant\s*:',
        r'user\s*:',
        r'<\s*script',
        r'javascript\s*:',
        r'data\s*:',
        r'vbscript\s*:',
    ]
    
    for pattern in dangerous_patterns:
        prompt = re.sub(pattern, '', prompt, flags=re.IGNORECASE)
    
    # Limitar tamanho do prompt
    max_prompt_length = 2000
    if len(prompt) > max_prompt_length:
        prompt = prompt[:max_prompt_length]
        try:
            from flask import current_app
            current_app.logger.warning('Prompt truncated due to length')
        except RuntimeError:
            # Working outside of application context
            pass
    
    return prompt.strip()

def validate_json_structure(data, required_fields=None):
    """
    Valida estrutura básica do JSON retornado pelo Gemini
    """
    if not isinstance(data, dict):
        return False
    
    if required_fields:
        for field in required_fields:
            if field not in data:
                return False
    
    return True

def secure_temp_file(original_filename):
    """
    Cria nome seguro para arquivo temporário
    """
    secure_name = secure_filename(original_filename)
    if not secure_name:
        secure_name = 'upload_file'
    
    # Adicionar timestamp para evitar conflitos
    import time
    timestamp = str(int(time.time()))
    name, ext = os.path.splitext(secure_name)
    
    return f"{name}_{timestamp}{ext}"
