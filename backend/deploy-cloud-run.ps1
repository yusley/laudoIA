param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,

    [Parameter(Mandatory = $true)]
    [string]$Region,

    [Parameter(Mandatory = $true)]
    [string]$ServiceName,

    [Parameter(Mandatory = $true)]
    [string]$CloudSqlInstance,

    [Parameter(Mandatory = $true)]
    [string]$AppUrl,

    [Parameter(Mandatory = $true)]
    [string]$BackendUrl,

    [Parameter(Mandatory = $true)]
    [string]$CorsOrigins,

    [Parameter(Mandatory = $true)]
    [string]$SecretKey,

    [Parameter(Mandatory = $true)]
    [string]$AdminEmails,

    [Parameter(Mandatory = $true)]
    [string]$DatabaseUrl,

    [string]$MercadoPagoAccessToken = "",
    [string]$MercadoPagoWebhookUrl = "",
    [string]$OpenRouterApiKey = "",
    [string]$OpenRouterDefaultModel = "openrouter/owl-alpha",
    [string]$OpenRouterVisionModel = "openai/gpt-4o-mini",
    [string]$OpenRouterBaseUrl = "https://openrouter.ai/api/v1",
    [string]$OpenRouterRequestTimeoutSeconds = "25",
    [string]$OpenRouterFreeModelMaxAttempts = "1",
    [string]$UsdBrlRate = "5.20",
    [string]$CreditValueBrl = "1.00",
    [string]$PlatformMarginMultiplier = "1.35",
    [string]$ImageName = "laudoia-backend"
)

$imageUri = "gcr.io/$ProjectId/$ImageName"

gcloud builds submit `
  --project $ProjectId `
  --config backend/cloudbuild.yaml `
  --substitutions "_IMAGE_URI=$imageUri,_SERVICE_NAME=$ServiceName,_REGION=$Region,_CLOUDSQL_INSTANCE=$CloudSqlInstance,_APP_URL=$AppUrl,_BACKEND_URL=$BackendUrl,_CORS_ORIGINS=$CorsOrigins,_SECRET_KEY=$SecretKey,_ADMIN_EMAILS=$AdminEmails,_DATABASE_URL=$DatabaseUrl,_MERCADO_PAGO_ACCESS_TOKEN=$MercadoPagoAccessToken,_MERCADO_PAGO_WEBHOOK_URL=$MercadoPagoWebhookUrl,_OPENROUTER_API_KEY=$OpenRouterApiKey,_OPENROUTER_DEFAULT_MODEL=$OpenRouterDefaultModel,_OPENROUTER_VISION_MODEL=$OpenRouterVisionModel,_OPENROUTER_BASE_URL=$OpenRouterBaseUrl,_OPENROUTER_REQUEST_TIMEOUT_SECONDS=$OpenRouterRequestTimeoutSeconds,_OPENROUTER_FREE_MODEL_MAX_ATTEMPTS=$OpenRouterFreeModelMaxAttempts,_USD_BRL_RATE=$UsdBrlRate,_CREDIT_VALUE_BRL=$CreditValueBrl,_PLATFORM_MARGIN_MULTIPLIER=$PlatformMarginMultiplier" `
  .
