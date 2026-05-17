from circuitbreaker import circuit, CircuitBreakerError
import logging
from app.config import settings
import anthropic

logger = logging.getLogger(__name__)

# Initialize client here or pass it in
anthropic_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

@circuit(failure_threshold=5, recovery_timeout=60, expected_exception=Exception)
async def call_anthropic_with_circuit_breaker(**kwargs):
    """Wrap all Anthropic API calls through this function.
    After 5 failures, circuit opens for 60 seconds.
    On CircuitBreakerError: route to Ollama fallback.
    """
    return await anthropic_client.messages.create(**kwargs)

async def call_ollama(**fallback_kwargs):
    """Fallback implementation for Ollama"""
    # This requires an actual Ollama client implementation
    # e.g., using httpx to POST to settings.OLLAMA_BASE_URL
    import httpx
    logger.info("Using Ollama fallback")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.OLLAMA_BASE_URL}/api/chat",
            json=fallback_kwargs,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()

async def call_llm_with_fallback(primary_kwargs: dict, fallback_kwargs: dict):
    try:
        return await call_anthropic_with_circuit_breaker(**primary_kwargs)
    except CircuitBreakerError:
        logger.warning('Anthropic circuit open; routing to Ollama fallback')
        return await call_ollama(**fallback_kwargs)
    except Exception as e:
        logger.error(f'Anthropic call failed (circuit may still be closed): {e}')
        raise
