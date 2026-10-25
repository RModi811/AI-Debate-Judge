
import logging
import time

import httpx

from app.config import MODEL_CONFIG


logger = logging.getLogger(__name__)


class OllamaError(RuntimeError):
    """Raised when the local Ollama service cannot produce a usable response."""


async def generate(prompt: str, *, num_predict: int | None = None) -> str:
    """Generate a bounded JSON response and log request timing without logging prompt text."""

    url = MODEL_CONFIG["base_url"].rstrip("/") + "/api/generate"
    model = MODEL_CONFIG["model"]

    request_prompt = prompt
    if model.lower().startswith("qwen3") and MODEL_CONFIG.get("disable_thinking", True):
        request_prompt = prompt.rstrip() + "\n\n/no_think"

    output_limit = num_predict or MODEL_CONFIG.get("num_predict", 2048)

    options = {
        "temperature": MODEL_CONFIG.get("temperature", 0.0),
        "num_predict": output_limit,
    }

    if "num_ctx" in MODEL_CONFIG:
        options["num_ctx"] = MODEL_CONFIG["num_ctx"]

    payload = {
        "model": model,
        "prompt": request_prompt,
        "stream": False,
        "format": "json",
        "think": False if MODEL_CONFIG.get("disable_thinking", True) else True,
        "options": options,
    }

    timeout = MODEL_CONFIG.get("timeout_seconds", 180)
    started = time.perf_counter()

    logger.info(
        "OLLAMA START model=%s prompt_chars=%d num_predict=%s timeout_seconds=%s",
        model,
        len(request_prompt),
        output_limit,
        timeout,
    )

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            text = data.get("response", "").strip()

            if not text:
                raise OllamaError(
                    "Ollama returned an empty response. Check the model output and "
                    "Ollama server logs; no result was passed to the JSON parser."
                )

            elapsed = time.perf_counter() - started
            logger.info(
                "OLLAMA SUCCESS elapsed_seconds=%.2f response_chars=%d",
                elapsed,
                len(text),
            )
            return text

    except OllamaError:
        elapsed = time.perf_counter() - started
        logger.error("OLLAMA FAILURE elapsed_seconds=%.2f error=empty_or_invalid_response", elapsed)
        raise

    except httpx.TimeoutException as exc:
        elapsed = time.perf_counter() - started
        logger.error(
            "OLLAMA TIMEOUT elapsed_seconds=%.2f configured_timeout_seconds=%s",
            elapsed,
            timeout,
        )
        raise OllamaError(
            f"Ollama timed out after {timeout} seconds. "
            "The request used bounded JSON output; inspect the request timing logs "
            "before increasing the timeout."
        ) from exc

    except httpx.HTTPStatusError as exc:
        elapsed = time.perf_counter() - started
        detail = exc.response.text[:500]
        logger.error(
            "OLLAMA HTTP ERROR elapsed_seconds=%.2f status=%s detail=%s",
            elapsed,
            exc.response.status_code,
            detail,
        )
        raise OllamaError(
            f"Ollama returned HTTP {exc.response.status_code}: {detail}"
        ) from exc

    except Exception as exc:
        elapsed = time.perf_counter() - started
        logger.exception(
            "OLLAMA REQUEST ERROR elapsed_seconds=%.2f",
            elapsed,
        )
        raise OllamaError(f"Local Ollama request failed: {exc}") from exc
