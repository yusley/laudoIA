# Deploy do Backend no Google Cloud

Este backend esta pronto para subir no `Cloud Run` com `Cloud SQL for PostgreSQL`.

## O que foi preparado no projeto

- O container agora respeita a porta do ambiente com `PORT`.
- O CORS agora vem de `CORS_ORIGINS`, permitindo frontend publicado.
- Existe um pipeline simples em `backend/cloudbuild.yaml`.
- Existe um atalho PowerShell em `backend/deploy-cloud-run.ps1`.

## Arquitetura recomendada

- `Cloud Run` para a API FastAPI
- `Cloud SQL for PostgreSQL` para o banco
- `Artifact Registry` ou Container Registry para a imagem

Observacao importante:

- O backend nao depende de disco persistente para os uploads atuais. Ele processa o arquivo em memoria e persiste no banco os metadados e o texto extraido. Isso funciona no Cloud Run.

## Variaveis que voce precisa definir

Minimas:

- `APP_URL`: URL publica do frontend
- `BACKEND_URL`: URL publica do backend no Cloud Run
- `CORS_ORIGINS`: lista separada por virgula com as origens permitidas do frontend
- `SECRET_KEY`: chave forte do JWT
- `ADMIN_EMAILS`: e-mails admin separados por virgula
- `DATABASE_URL`: conexao SQLAlchemy usando o socket do Cloud SQL
- `OPENROUTER_API_KEY`: chave da IA, se for usar a geracao

Exemplo de `DATABASE_URL` para Cloud SQL:

```text
postgresql+psycopg2://postgres:SUA_SENHA@/laudoia?host=/cloudsql/SEU_PROJETO:REGIAO:INSTANCIA
```

Exemplo de `CORS_ORIGINS`:

```text
https://seu-frontend.web.app,https://www.seu-dominio.com
```

## Passo a passo

1. Instale o Google Cloud CLI:

```powershell
winget install Google.CloudSDK
```

2. Faça login e selecione o projeto:

```powershell
gcloud auth login
gcloud config set project SEU_PROJECT_ID
```

3. Ative as APIs necessarias:

```powershell
gcloud services enable run.googleapis.com sqladmin.googleapis.com cloudbuild.googleapis.com
```

4. Crie a instancia Postgres no Cloud SQL e o banco `laudoia`.

5. Monte a `DATABASE_URL` no formato:

```text
postgresql+psycopg2://USUARIO:SENHA@/laudoia?host=/cloudsql/PROJECT:REGION:INSTANCE
```

6. Rode o deploy:

```powershell
.\backend\deploy-cloud-run.ps1 `
  -ProjectId "SEU_PROJECT_ID" `
  -Region "southamerica-east1" `
  -ServiceName "laudoia-backend" `
  -CloudSqlInstance "SEU_PROJECT_ID:southamerica-east1:laudoia-db" `
  -AppUrl "https://seu-frontend.web.app" `
  -BackendUrl "https://laudoia-backend-xxxxx-uc.a.run.app" `
  -CorsOrigins "https://seu-frontend.web.app" `
  -SecretKey "troque-por-uma-chave-forte" `
  -AdminEmails "admin@seudominio.com" `
  -DatabaseUrl "postgresql+psycopg2://postgres:SENHA@/laudoia?host=/cloudsql/SEU_PROJECT_ID:southamerica-east1:laudoia-db" `
  -OpenRouterApiKey "SUA_CHAVE"
```

## Verificacao apos deploy

- Abra `${BACKEND_URL}/health`
- Abra `${BACKEND_URL}/docs`
- Teste login e upload pelo frontend publicado
- Confirme se o webhook do Mercado Pago aponta para a URL publica do backend

## Limites e proximos passos

- Hoje as variaveis sensiveis vao por `--set-env-vars`. Em ambiente de producao, o ideal e mover segredos para `Secret Manager`.
- Se no futuro voce quiser armazenar arquivos originais, o caminho recomendado e `Cloud Storage`.
