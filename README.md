
# Vision Estoque Financeiro Applet

Aplicação Flask segura para análise automatizada de documentos fiscais usando Google Gemini AI.

## 🔒 Recursos de Segurança

Esta versão implementa múltiplas camadas de segurança:

### Validação de Arquivos
- ✅ Verificação de extensões permitidas
- ✅ Validação de tipos MIME
- ✅ Verificação de magic numbers
- ✅ Limite de tamanho de arquivo (16MB)
- ✅ Sanitização de nomes de arquivo

### Segurança da Aplicação
- ✅ Headers de segurança (CSP, HSTS, X-Frame-Options)
- ✅ Rate limiting (10 uploads/minuto por IP)
- ✅ CORS configurado adequadamente
- ✅ Autenticação opcional por token
- ✅ Sanitização de prompts para IA
- ✅ Logging de segurança

### Configuração Segura
- ✅ Debug mode desabilitado em produção
- ✅ Binding seguro (127.0.0.1 em dev, 0.0.0.0 em prod)
- ✅ Variáveis de ambiente para configurações sensíveis
- ✅ Usuário não-root no container Docker

## 🚀 Instalação e Configuração

### 1. Clonar o repositório
```bash
git clone https://github.com/shakarpg/Vision_Estoque_Financeiro_Applet.git
cd Vision_Estoque_Financeiro_Applet
```

### 2. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Editar .env com suas configurações
```

### 3. Instalar dependências
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 4. Executar a aplicação

#### Desenvolvimento
```bash
export FLASK_ENV=development
python main.py
```

#### Produção com Docker
```bash
docker-compose up -d
```

## 📋 Configurações Obrigatórias

As seguintes variáveis de ambiente são obrigatórias:

- `GCP_PROJECT_ID`: ID do projeto Google Cloud
- `GCS_BUCKET_NAME`: Nome do bucket do Google Cloud Storage
- `SECRET_KEY`: Chave secreta para sessões Flask

## 🔧 Configurações Opcionais

- `ENABLE_AUTH=true`: Habilita autenticação por token
- `API_TOKEN`: Token para autenticação (se habilitada)
- `ALLOWED_ORIGINS`: Origens permitidas para CORS
- `MAX_FILE_SIZE`: Tamanho máximo de arquivo em bytes
- `REDIS_URL`: URL do Redis para rate limiting

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar testes de segurança
pytest tests/test_security.py -v

# Executar com coverage
pytest --cov=app tests/
```

## 📊 Monitoramento

### Health Check
```bash
curl http://localhost:8080/health
```

### Logs
Os logs são salvos em `logs/vision_app.log` com rotação automática.

## 🔐 Autenticação (Opcional)

Para habilitar autenticação:

1. Definir `ENABLE_AUTH=true` no `.env`
2. Definir `API_TOKEN` com um token seguro
3. Incluir header `Authorization: Bearer <token>` nas requisições

## 📡 API Endpoints

### POST /upload-invoice
Upload e análise de documento fiscal.

**Headers:**
- `Content-Type: multipart/form-data`
- `Authorization: Bearer <token>` (se autenticação habilitada)

**Body:**
- `image`: Arquivo de imagem (PNG, JPG, PDF, etc.)

**Response:**
```json
{
  "message": "Imagem processada com sucesso e dados extraídos.",
  "extracted_data": {
    "tipo_documento": "Nota Fiscal",
    "numero_documento": "123456",
    "data_emissao": "01/01/2024",
    "fornecedor": "Empresa XYZ",
    "itens": [...],
    "valor_total_documento": 1000.00
  }
}
```

### GET /health
Verificação de saúde da aplicação.

## 🐳 Docker

### Build da imagem
```bash
docker build -t vision-estoque-financeiro .
```

### Executar container
```bash
docker run -p 8080:8080 --env-file .env vision-estoque-financeiro
```

## 🔄 CI/CD

A aplicação está preparada para deploy em:
- Google Cloud Run
- Kubernetes
- Heroku
- AWS ECS

## 📝 Changelog de Segurança

### Versão 2.0.0 - Hardening de Segurança

#### Vulnerabilidades Corrigidas:
1. **Debug Mode**: Desabilitado em produção
2. **Validação de Upload**: Implementada validação completa
3. **Autenticação**: Sistema opcional implementado
4. **Exposição de Dados**: Logs sanitizados
5. **Network Binding**: Configuração segura por ambiente
6. **Headers de Segurança**: Implementados via Flask-Talisman
7. **Rate Limiting**: Implementado com Flask-Limiter
8. **CORS**: Configurado adequadamente
9. **Injeção de Prompt**: Sanitização implementada

#### Melhorias Estruturais:
- Arquitetura modular com blueprints
- Sistema de configuração robusto
- Tratamento de erros abrangente
- Logging estruturado
- Testes automatizados
- Containerização segura

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## ⚠️ Avisos de Segurança

- Sempre use HTTPS em produção
- Mantenha as dependências atualizadas
- Configure adequadamente as variáveis de ambiente
- Monitore os logs regularmente
- Implemente backup dos dados importantes

## 📞 Suporte

Para questões de segurança, entre em contato através de issues no GitHub ou email do mantenedor.
