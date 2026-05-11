import logging
import base64
from dataclasses import dataclass
from decimal import Decimal

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

FREE_MODEL_CANDIDATES = [
    "openrouter/free",
    "openrouter/owl-alpha",
    "minimax/minimax-m2.5:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "qwen/qwen3-coder:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "inclusionai/ling-2.6-1t:free",
]


@dataclass
class AITextResult:
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    reasoning_tokens: int
    cached_tokens: int
    cost_credit: Decimal
    raw_response: dict
    user_tag: str | None = None


class OpenRouterGenerationError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _build_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.APP_URL,
        "X-Title": settings.APP_NAME,
    }


def _extract_openrouter_error_message(response: httpx.Response) -> str:
    try:
        data = response.json()
        message = data.get("error", {}).get("message")
        if isinstance(message, str) and message.strip():
            return message.strip()
    except Exception:
        pass
    return "Falha ao gerar texto com OpenRouter."


def _is_free_model(model: str) -> bool:
    return model in {"openrouter/free", "openrouter/owl-alpha"} or model.endswith(":free")


def _build_model_attempts(selected_model: str) -> list[str]:
    if not _is_free_model(selected_model):
        return [selected_model]

    attempts = [selected_model]
    for candidate in FREE_MODEL_CANDIDATES:
        if candidate not in attempts:
            attempts.append(candidate)
    return attempts[: max(1, settings.OPENROUTER_FREE_MODEL_MAX_ATTEMPTS)]


async def generate_text(
    system_prompt: str,
    user_prompt: str,
    model: str | None = None,
    temperature: float = 0.2,
    user_tag: str | None = None,
) -> AITextResult:
    if not settings.OPENROUTER_API_KEY:
        raise OpenRouterGenerationError("OPENROUTER_API_KEY nao configurada.", status_code=400)

    selected_model = model or settings.OPENROUTER_DEFAULT_MODEL
    headers = _build_headers()
    attempts = _build_model_attempts(selected_model)
    last_rate_limit_message = ""
    last_not_found_message = ""

    for attempt_model in attempts:
        payload = {
            "model": attempt_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }
        if user_tag:
            payload["user"] = user_tag

        logger.info("Solicitando texto ao OpenRouter com model=%s", attempt_model)

        try:
            async with httpx.AsyncClient(timeout=settings.OPENROUTER_REQUEST_TIMEOUT_SECONDS) as client:
                response = await client.post(
                    f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                )
        except httpx.TimeoutException as exc:
            raise OpenRouterGenerationError(
                "A requisicao para o OpenRouter demorou demais. Tente novamente em instantes.",
                status_code=504,
            ) from exc
        except httpx.HTTPError as exc:
            raise OpenRouterGenerationError(
                "Nao foi possivel conectar ao OpenRouter no momento. Tente novamente em instantes.",
                status_code=502,
            ) from exc

        if response.status_code >= 400:
            logger.error("Erro OpenRouter status=%s body=%s", response.status_code, response.text[:800])
            upstream_message = _extract_openrouter_error_message(response)
            lowered = upstream_message.lower()

            if _is_free_model(attempt_model) and (
                "temporarily rate-limited upstream" in lowered
                or "rate-limited" in lowered
                or response.status_code == 429
            ):
                last_rate_limit_message = upstream_message
                continue

            if _is_free_model(attempt_model) and response.status_code == 404:
                last_not_found_message = upstream_message
                continue

            if response.status_code == 404:
                raise OpenRouterGenerationError(
                    f"Modelo nao encontrado no OpenRouter: {attempt_model}. Escolha outro modelo.",
                    status_code=400,
                )

            if response.status_code == 429:
                raise OpenRouterGenerationError(
                    "O OpenRouter atingiu limite temporario para este modelo. Tente novamente em instantes.",
                    status_code=429,
                )

            detail = f"Erro OpenRouter: {upstream_message}"
            raise OpenRouterGenerationError(detail, status_code=400 if response.status_code < 500 else 502)

        data = response.json()
        try:
            usage = data.get("usage", {}) or {}
            return AITextResult(
                content=data["choices"][0]["message"]["content"].strip(),
                model=data.get("model", attempt_model),
                prompt_tokens=int(usage.get("prompt_tokens") or 0),
                completion_tokens=int(usage.get("completion_tokens") or 0),
                reasoning_tokens=int(usage.get("reasoning_tokens") or 0),
                cached_tokens=int(usage.get("cached_tokens") or 0),
                cost_credit=Decimal(str(usage.get("cost") or 0)),
                raw_response=data,
                user_tag=user_tag,
            )
        except (KeyError, IndexError, TypeError) as exc:
            logger.exception("Resposta inesperada do OpenRouter")
            raise OpenRouterGenerationError("Resposta invalida do OpenRouter.", status_code=502) from exc

    if _is_free_model(selected_model):
        raise OpenRouterGenerationError(
            "Os modelos gratuitos do OpenRouter estao indisponiveis ou limitados neste momento. "
            "Tente novamente em alguns instantes ou selecione um modelo pago.",
            status_code=429,
        )

    if last_not_found_message:
        raise OpenRouterGenerationError(f"Erro OpenRouter: {last_not_found_message}", status_code=400)

    if last_rate_limit_message:
        raise OpenRouterGenerationError(f"Erro OpenRouter: {last_rate_limit_message}", status_code=429)

    raise OpenRouterGenerationError("Falha ao gerar texto com OpenRouter.", status_code=502)


async def transcribe_image_checklist(
    image_bytes: bytes,
    mime_type: str,
    filename: str,
) -> str:
    if not settings.OPENROUTER_API_KEY:
        return "[Imagem anexada, mas OPENROUTER_API_KEY nao configurada para OCR.]"

    prompt = (
        "Extraia e transcreva integralmente o conteudo visivel desta imagem de checklist pericial em portugues. "
        "Mantenha a ordem visual das secoes. Para cada campo preenchido, informe o rotulo e o valor. "
        "Para perguntas com alternativas, radios, checkboxes e menus, liste todas as opcoes visiveis, "
        "inclusive as nao selecionadas, usando exatamente o formato '[x]' para marcado e '[ ]' para desmarcado. "
        "Se houver campos condicionais, preserve o titulo da secao e as opcoes exibidas. "
        "Nao resuma, nao interprete juridicamente e nao omita opcoes. "
        f"Arquivo: {filename}."
    )
    payload = {
        "model": settings.OPENROUTER_VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('ascii')}"
                        },
                    },
                ],
            }
        ],
        "temperature": 0,
    }

    try:
        async with httpx.AsyncClient(timeout=max(45, settings.OPENROUTER_REQUEST_TIMEOUT_SECONDS)) as client:
            response = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers=_build_headers(),
                json=payload,
            )
    except httpx.TimeoutException:
        return "[Imagem anexada, mas o OCR por IA excedeu o tempo limite.]"
    except httpx.HTTPError:
        return "[Imagem anexada, mas houve falha de conexao ao extrair o checklist.]"

    if response.status_code >= 400:
        logger.error("Erro OCR OpenRouter status=%s body=%s", response.status_code, response.text[:800])
        return f"[Imagem anexada, mas o OCR por IA falhou: {_extract_openrouter_error_message(response)}]"

    try:
        data = response.json()
        content = data["choices"][0]["message"]["content"].strip()
        return content or "[Imagem anexada, mas sem texto identificado no OCR por IA.]"
    except (KeyError, IndexError, TypeError, ValueError):
        logger.exception("Resposta inesperada do OpenRouter no OCR de imagem")
        return "[Imagem anexada, mas a resposta de OCR veio em formato invalido.]"
