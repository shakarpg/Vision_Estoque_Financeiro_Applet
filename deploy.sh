#!/bin/bash

# Script de Deploy para Google Cloud Run
# Vision Estoque Financeiro - Aplicação com Correções de Segurança

set -e

# Configurações do projeto
PROJECT_ID="vision-estoque-financeiro"
REGION="us-central1"
SERVICE_NAME="vision-estoque"
IMAGE_NAME="vision-estoque"
TAG="v$(date +%Y%m%d-%H%M%S)"
FULL_IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/cloud-run-source-deploy/${IMAGE_NAME}:${TAG}"

echo "🚀 Iniciando deploy da aplicação Vision Estoque Financeiro"
echo "📋 Configurações:"
echo "   - Projeto: ${PROJECT_ID}"
echo "   - Região: ${REGION}"
echo "   - Serviço: ${SERVICE_NAME}"
echo "   - Imagem: ${FULL_IMAGE_URL}"
echo ""

# Verificar se está autenticado
echo "🔐 Verificando autenticação..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Não há conta ativa. Execute: gcloud auth login"
    exit 1
fi

# Configurar projeto
echo "⚙️  Configurando projeto..."
gcloud config set project ${PROJECT_ID}

# Habilitar APIs necessárias
echo "🔧 Habilitando APIs necessárias..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Criar repositório no Artifact Registry se não existir
echo "📦 Configurando Artifact Registry..."
gcloud artifacts repositories create cloud-run-source-deploy \
    --repository-format=docker \
    --location=${REGION} \
    --description="Repository for Cloud Run deployments" \
    2>/dev/null || echo "Repositório já existe"

# Configurar autenticação do Docker
echo "🔑 Configurando autenticação do Docker..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Fazer build da imagem usando Cloud Build
echo "🏗️  Fazendo build da imagem..."
gcloud builds submit --tag ${FULL_IMAGE_URL} --project=${PROJECT_ID}

# Deploy no Cloud Run
echo "🚀 Fazendo deploy no Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${FULL_IMAGE_URL} \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --timeout 300 \
    --concurrency 80 \
    --set-env-vars "FLASK_ENV=production,PYTHONPATH=/app" \
    --set-env-vars "GCP_PROJECT_ID=${PROJECT_ID}" \
    --set-env-vars "GCS_BUCKET_NAME=${PROJECT_ID}-uploads" \
    --set-env-vars "SECRET_KEY=$(openssl rand -base64 32)" \
    --set-env-vars "ENABLE_AUTH=false" \
    --set-env-vars "ALLOWED_ORIGINS=*" \
    --project=${PROJECT_ID}

# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format="value(status.url)")

# Teste de saúde
echo "🏥 Testando endpoint de saúde..."
sleep 10
if curl -f "${SERVICE_URL}/health" > /dev/null 2>&1; then
    echo "✅ Aplicação está funcionando corretamente!"
else
    echo "⚠️  Aviso: Teste de saúde falhou. Verifique os logs."
fi

echo ""
echo "🎉 Deploy concluído com sucesso!"
echo "📍 URL da aplicação: ${SERVICE_URL}"
echo "🔍 Para visualizar logs: gcloud run logs tail ${SERVICE_NAME} --region=${REGION}"
echo "📊 Para monitorar: https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}"
echo ""
echo "⚙️  Próximos passos recomendados:"
echo "   1. Configurar domínio customizado (opcional)"
echo "   2. Configurar Secret Manager para variáveis sensíveis"
echo "   3. Configurar monitoramento e alertas"
echo "   4. Configurar backup do bucket GCS"
echo "   5. Revisar configurações de IAM"
echo ""
echo "🔐 Para habilitar autenticação, defina:"
echo "   - ENABLE_AUTH=true"
echo "   - API_TOKEN=<seu-token-seguro>"
