# LaudoIA Pericial

MVP full-stack para cadastro de processos trabalhistas, upload de documentos técnicos, cadastro de quesitos, geração assistida de laudos periciais via OpenRouter, edição por seções e exportação em DOCX/PDF.

## Stack

- Frontend: React, Vite, TypeScript, TailwindCSS, Axios, React Hook Form, Zod
- Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL, Pydantic, `python-docx`, PyMuPDF, `python-multipart`, `httpx`
- Infra: Docker Compose

## Funcionalidades do MVP

- Cadastro e edição de processos judiciais
- Autenticação JWT
- Upload de PDF, DOCX, TXT e imagens com extração textual quando possível
- CRUD de quesitos por parte
- Geração de laudo pericial com IA via OpenRouter
- Editor de laudo por seções
- Exportação em DOCX e PDF
- Dashboard com visão geral dos processos
- Carteira de créditos por usuário
- Controle de consumo por uso de IA
- Compra de créditos via Mercado Pago Checkout

## Planos comerciais

Os creditos funcionam como uma media aproximada de capacidade, nao como uma garantia fixa de quantidade. Em modelos pagos, um laudo completo consome pelo menos 1 credito. Regeneracoes de secoes consomem pelo menos 0,25 credito. O consumo pode ser maior se o custo real do OpenRouter para um laudo muito grande superar o minimo comercial.

- Plano Essencial: R$ 25,00, 25 creditos, mais ou menos 25 laudos
- Plano Profissional: R$ 50,00, 100 creditos, mais ou menos 100 laudos
- Plano Escala: R$ 100,00, 500 creditos, mais ou menos 500 laudos

## Controle financeiro da IA

O saldo do usuario usa creditos internos da plataforma. O custo real do OpenRouter e registrado separadamente em USD e convertido para BRL com `USD_BRL_RATE`.

- `USD_BRL_RATE`: cotacao usada para converter custo OpenRouter de USD para BRL
- `CREDIT_VALUE_BRL`: valor comercial de 1 credito interno em BRL
- `PLATFORM_MARGIN_MULTIPLIER`: multiplicador usado quando o custo real ultrapassa o minimo comercial

Cada evento de uso registra custo OpenRouter em USD, custo convertido em BRL, receita estimada da plataforma em BRL, margem estimada em BRL e creditos debitados do usuario.

## Estrutura

```text
backend/
frontend/
docker-compose.yml
README.md
```

## Configuração

1. Copie os arquivos de ambiente:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

No Windows PowerShell:

```powershell
Copy-Item backend/.env.example backend/.env
Copy-Item frontend/.env.example frontend/.env
```

2. Edite `backend/.env` e configure sua chave do OpenRouter:

```env
OPENROUTER_API_KEY=coloque_sua_chave_aqui
OPENROUTER_DEFAULT_MODEL=openrouter/owl-alpha
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
APP_URL=http://localhost:3000
APP_NAME=LaudoIA Pericial
MERCADO_PAGO_ACCESS_TOKEN=coloque_seu_token_aqui
MERCADO_PAGO_WEBHOOK_URL=http://localhost:8000/api/v1/billing/webhooks/mercado-pago
```

3. Suba tudo com um único comando:

```bash
docker compose up --build
```

## Acessos locais

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Docs da API: http://localhost:8000/docs

## Deploy do backend no Google Cloud

O backend pode ser publicado no `Google Cloud Run` com `Cloud SQL for PostgreSQL`.

- Guia completo: `backend/DEPLOY_GOOGLE_CLOUD.md`
- Pipeline de build/deploy: `backend/cloudbuild.yaml`
- Script de apoio no Windows PowerShell: `backend/deploy-cloud-run.ps1`

## Deploy do frontend na Vercel

O frontend pode ser publicado na `Vercel`.

- Guia completo: `frontend/DEPLOY_VERCEL.md`
- Rewrite para SPA: `frontend/vercel.json`

## Fluxo sugerido

1. Criar conta e autenticar.
2. Cadastrar um processo.
3. Anexar NR-15, NR-16, FISPQ/FDS, prova emprestada, quesitos e fotos.
4. Cadastrar os quesitos das partes e do juízo.
5. Gerar o laudo com o modelo desejado.
6. Revisar seção por seção.
7. Exportar em DOCX ou PDF.

## OpenRouter

O backend usa uma interface compatível com OpenAI, apontando para o OpenRouter em `app/services/ai_service.py`.

Modelos já preparados no frontend:

- Gratuitos:
- `openrouter/free`
- `openrouter/owl-alpha`
- `minimax/minimax-m2.5:free`
- `qwen/qwen3-next-80b-a3b-instruct:free`
- `qwen/qwen3-coder:free`
- `meta-llama/llama-3.3-70b-instruct:free`
- `inclusionai/ling-2.6-1t:free`
- Pagos:
- `openai/gpt-4o-mini`
- `openai/gpt-4.1-mini`
- `anthropic/claude-3.5-sonnet`
- `google/gemini-2.0-flash`
- `deepseek/deepseek-chat`

Para criar a chave:

1. Acesse https://openrouter.ai/
2. Gere sua API key no painel.
3. Salve a chave apenas no arquivo `.env`.

## Exemplo de payload de geração

`POST /api/v1/processes/{id}/reports/generate`

```json
{
  "model": "openai/gpt-4o-mini",
  "temperature": 0.2,
  "extra_instructions": "Use linguagem mais técnica e responda todos os quesitos."
}
```

## Exemplo de orientação da IA

System prompt base usado no backend:

```text
Voce e um perito judicial especialista em Engenharia de Seguranca do Trabalho e Higiene Ocupacional, com atuacao na Justica do Trabalho.

Elabore um laudo tecnico pericial completo, formal, tecnico, imparcial e estruturado, com base nos documentos fornecidos, nos quesitos apresentados, nas Normas Regulamentadoras NR-15 e NR-16 e nos modelos de laudos anexados.

Regras:
- Nao invente dados ausentes.
- Quando faltar informacao, declare a limitacao tecnica.
- Diferencie avaliacao qualitativa e quantitativa.
- Responda todos os quesitos individualmente.
- Use linguagem pericial formal.
- Fundamente a analise com base normativa.
```

## Observações do MVP

- OCR de imagens ainda não foi implementado; imagens ficam registradas com metadados básicos.
- A exportação PDF está pronta em formato simples e pode evoluir para layout mais refinado.
- A regeneração de seção usa o contexto completo do processo para manter coerência.
- O backend salva texto extraído do documento no banco para reutilização no prompt.

## Endpoints principais

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/processes`
- `POST /api/v1/processes`
- `GET /api/v1/processes/{id}`
- `PUT /api/v1/processes/{id}`
- `DELETE /api/v1/processes/{id}`
- `POST /api/v1/processes/{id}/documents`
- `GET /api/v1/processes/{id}/documents`
- `GET /api/v1/documents/{id}`
- `DELETE /api/v1/documents/{id}`
- `POST /api/v1/processes/{id}/questions`
- `GET /api/v1/processes/{id}/questions`
- `PUT /api/v1/questions/{id}`
- `DELETE /api/v1/questions/{id}`
- `POST /api/v1/processes/{id}/reports/generate`
- `GET /api/v1/processes/{id}/reports`
- `GET /api/v1/reports/{id}`
- `PUT /api/v1/reports/{id}`
- `POST /api/v1/reports/{id}/sections/{section_id}/regenerate`
- `GET /api/v1/reports/{id}/export/docx`
- `GET /api/v1/reports/{id}/export/pdf`
- `GET /api/v1/billing/wallet`
- `GET /api/v1/billing/packages`
- `POST /api/v1/billing/checkout`
- `GET /api/v1/billing/payments`
- `GET /api/v1/billing/usage`
- `POST /api/v1/billing/webhooks/mercado-pago`
