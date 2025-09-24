
FROM python:3.9-slim-buster

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    libmagic1 \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p logs uploads && \
    chown -R app:app /app

# Mudar para usuário não-root
USER app

# Expor porta
EXPOSE 8080

# Configurar variáveis de ambiente
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Comando para iniciar a aplicação
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "main:app"]
