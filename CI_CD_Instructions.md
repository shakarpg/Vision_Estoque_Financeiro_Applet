# Guia de Configuração de CI/CD com Google Cloud Build

Este guia detalha como configurar um pipeline de Integração Contínua e Entrega Contínua (CI/CD) para o projeto `Vision_Estoque_Financeiro_Applet` utilizando o Google Cloud Build. O pipeline automatizará o processo de build da imagem Docker, push para o Google Artifact Registry e deploy no Google Cloud Run a cada commit no repositório.

## 1. Pré-requisitos

Antes de iniciar, certifique-se de que você possui:

*   Uma conta Google Cloud com um projeto ativo.
*   O `gcloud CLI` instalado e configurado em sua máquina local.
*   As seguintes APIs habilitadas no seu projeto Google Cloud:
    *   **Cloud Build API**
    *   **Cloud Run API**
    *   **Artifact Registry API**
    *   **Cloud Storage API**
    *   **Vertex AI API** (para a API Gemini)

    Você pode habilitá-las através do console do Google Cloud ou via `gcloud CLI`:
    ```bash
    gcloud services enable cloudbuild.googleapis.com \
                           run.googleapis.com \
                           artifactregistry.googleapis.com \
                           storage.googleapis.com \
                           aiplatform.googleapis.com
    ```

*   Permissões adequadas para a conta de serviço do Cloud Build (geralmente `[PROJECT_NUMBER]@cloudbuild.gserviceaccount.com`). As permissões mínimas necessárias incluem:
    *   `Cloud Run Admin`
    *   `Artifact Registry Writer`
    *   `Storage Object Admin`
    *   `Service Account User` (para a conta de serviço do Cloud Run)
    *   `Vertex AI User`

## 2. Configuração do Projeto

### 2.1. Criar o Bucket do Google Cloud Storage (GCS)

O aplicativo utiliza um bucket do GCS para armazenar as imagens. Crie um bucket com um nome exclusivo (substitua `[PROJECT_ID]` pelo ID do seu projeto):

```bash
gsutil mb gs://[PROJECT_ID]-vision-estoque-uploads
```

### 2.2. Criar o Repositório no Artifact Registry

O Google Cloud Build fará o push da imagem Docker para o Artifact Registry. Crie um repositório Docker na região desejada (ex: `us-central1`):

```bash
gcloud artifacts repositories create cloud-run-source-deploy \
    --repository-format=docker \
    --location=us-central1 \
    --description="Docker repository for Cloud Run deployments"
```

### 2.3. Ajustar o `cloudbuild.yaml` (Opcional)

O arquivo `cloudbuild.yaml` foi gerado com configurações padrão. Você pode precisar ajustá-lo para sua região ou variáveis de ambiente específicas. O arquivo está localizado na raiz do seu repositório clonado:

```yaml
# Conteúdo do cloudbuild.yaml
steps:
  # Build da imagem Docker
  - name: 'gcr.io/cloud-builders/docker'
    id: 'Build Docker Image'
    args: ['build', '-t', 'gcr.io/${PROJECT_ID}/vision-estoque-financeiro-applet:${COMMIT_SHA}', '.']
    dir: 'Vision_Estoque_Financeiro_Applet'

  # Push da imagem para o Google Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    id: 'Push Docker Image'
    args: ['push', 'gcr.io/${PROJECT_ID}/vision-estoque-financeiro-applet:${COMMIT_SHA}']

  # Deploy da imagem para o Google Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    id: 'Deploy to Cloud Run'
    args:
      - 'run'
      - 'deploy'
      - 'vision-estoque-financeiro-applet'
      - '--image'
      - 'gcr.io/${PROJECT_ID}/vision-estoque-financeiro-applet:${COMMIT_SHA}'
      - '--region'
      - 'us-central1' # Altere para a sua região preferida
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated' # Ajuste conforme a necessidade de autenticação
      - '--set-env-vars'
      - 'GCP_PROJECT_ID=${PROJECT_ID},GCP_LOCATION=us-central1,GEMINI_MODEL_ID=gemini-pro-vision,GCS_BUCKET_NAME=${PROJECT_ID}-vision-estoque-uploads' # Ajuste as variáveis de ambiente
    env:
      - 'CLOUDSDK_CORE_PROJECT=${PROJECT_ID}'
      - 'CLOUDSDK_COMPUTE_REGION=us-central1' # Altere para a sua região preferida

images:
  - 'gcr.io/${PROJECT_ID}/vision-estoque-financeiro-applet:${COMMIT_SHA}'
```

**Pontos de atenção no `cloudbuild.yaml`:**

*   **`region`**: Certifique-se de que a região (`us-central1` no exemplo) corresponde à região onde você deseja implantar seu serviço Cloud Run e onde criou o repositório Artifact Registry.
*   **`--allow-unauthenticated`**: Se você deseja que seu serviço Cloud Run seja acessível publicamente sem autenticação, mantenha esta flag. Caso contrário, remova-a e configure a autenticação de acordo com suas necessidades de segurança.
*   **`--set-env-vars`**: Ajuste as variáveis de ambiente conforme necessário. `GCP_PROJECT_ID`, `GCP_LOCATION`, `GEMINI_MODEL_ID` e `GCS_BUCKET_NAME` são essenciais para o funcionamento do aplicativo.

## 3. Configurar o Trigger do Cloud Build

Um trigger do Cloud Build monitora seu repositório e inicia automaticamente o pipeline de CI/CD quando ocorrem eventos específicos (por exemplo, um push para o branch `main`).

1.  **Navegue até o Cloud Build no Console do GCP**:
    Vá para [Cloud Build](https://console.cloud.google.com/cloudbuild/triggers) no seu projeto GCP.

2.  **Crie um novo Trigger**:
    *   Clique em **

    **Criar Trigger**.
    *   **Nome**: Dê um nome descritivo ao seu trigger (ex: `vision-estoque-financeiro-applet-ci-cd`).
    *   **Região**: Selecione a região onde o trigger será executado (ex: `global` ou a mesma região do seu Cloud Run).
    *   **Evento**: Selecione `Push para um branch`.
    *   **Repositório de Origem**: Conecte seu repositório GitHub (`shakarpg/Vision_Estoque_Financeiro_Applet`). Se ainda não estiver conectado, siga as instruções para autenticar o GitHub.
    *   **Branch**: Defina o padrão do branch que irá disparar o build (ex: `^main$` para o branch `main`).
    *   **Configuração do Build**: Selecione `Arquivo de configuração do Cloud Build`.
    *   **Local do Arquivo de Configuração do Cloud Build**: Insira `cloudbuild.yaml` (assumindo que você salvou o arquivo na raiz do seu repositório).
    *   **Variáveis de Substituição (Opcional)**: Você pode adicionar variáveis de substituição personalizadas aqui, se necessário.

3.  **Crie o Trigger**.

## 4. Testando o Pipeline de CI/CD

Após configurar o trigger, qualquer push para o branch `main` do seu repositório GitHub irá automaticamente iniciar um build no Google Cloud Build. Você pode verificar o status do build na seção [Histórico do Cloud Build](https://console.cloud.google.com/cloudbuild/builds) no console do GCP.

Se o build for bem-sucedido, a nova versão da sua aplicação será implantada no Google Cloud Run, e você poderá acessá-la através da URL do serviço Cloud Run.

## 5. Próximos Passos e Considerações de Segurança

*   **Secrets Manager**: Para gerenciar credenciais sensíveis (como chaves de API) de forma mais segura, considere integrar o Google Secret Manager. Você pode referenciar secrets no seu `cloudbuild.yaml` e no seu serviço Cloud Run.
*   **Testes Automatizados**: Adicione etapas de testes automatizados ao seu `cloudbuild.yaml` para garantir a qualidade do código antes do deploy. Por exemplo, você pode adicionar uma etapa para executar os testes localizados no diretório `tests/`.
*   **Ambientes**: Para projetos maiores, considere configurar diferentes triggers para diferentes branches (ex: `develop` para um ambiente de staging, `main` para produção).
*   **Monitoramento**: Configure alertas e monitoramento para seu serviço Cloud Run para ser notificado sobre quaisquer problemas após o deploy.

Este guia fornece uma base para um pipeline de CI/CD robusto. Adapte-o às necessidades específicas do seu projeto e às melhores práticas de segurança da sua organização.
