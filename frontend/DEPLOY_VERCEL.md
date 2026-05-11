# Deploy do Frontend na Vercel

Este frontend usa `Vite` e `React Router`, entao a publicacao na Vercel e simples.

## O que ja esta pronto

- Build command: `npm run build`
- Output directory: `dist`
- Variavel principal: `VITE_API_URL`
- Rewrite para SPA: `frontend/vercel.json`

## Antes de publicar

Tenha em maos a URL publica do backend no Cloud Run, por exemplo:

```text
https://laudoia-backend-xxxxx-uc.a.run.app/api/v1
```

Tambem atualize o backend para liberar o dominio do frontend em `CORS_ORIGINS`.

## Deploy pelo painel da Vercel

1. Acesse a Vercel e clique em `Add New Project`.
2. Importe este repositorio.
3. Na configuracao do projeto, use:

- Framework Preset: `Vite`
- Root Directory: `frontend`
- Build Command: `npm run build`
- Output Directory: `dist`

4. Em `Environment Variables`, crie:

```text
VITE_API_URL=https://laudoia-backend-xxxxx-uc.a.run.app/api/v1
```

5. Clique em `Deploy`.

## Depois do deploy

Pegue a URL publica da Vercel, por exemplo:

```text
https://seu-frontend.vercel.app
```

E ajuste o backend no Cloud Run para algo assim:

```text
APP_URL=https://seu-frontend.vercel.app
CORS_ORIGINS=https://seu-frontend.vercel.app
```

Se voce usar dominio proprio, inclua esse dominio tambem em `CORS_ORIGINS`.

## Verificacao

- Abra a home do frontend publicado
- Teste login
- Teste listagem de processos
- Recarregue uma rota interna para confirmar que o rewrite da SPA funcionou
