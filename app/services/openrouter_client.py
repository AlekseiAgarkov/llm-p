from dataclasses import dataclass
from typing import Any, Dict, List, Literal

import httpx

from app.core.config import Settings
from app.core.errors import ExternalServiceError


@dataclass(frozen=True)
class OpenRouterMessage:
    role: Literal["user", "system"]
    content: str


class OpenRouterClient:
    def __init__(self, settings: Settings):
        self._base_url = settings.OPENROUTER_BASE_URL
        self._api_key = settings.OPENROUTER_API_KEY
        self._model = settings.OPENROUTER_MODEL
        self._site_url = settings.OPENROUTER_SITE_URL
        self._app_name = settings.OPENROUTER_APP_NAME

    async def get_model_response(self, messages: List[OpenRouterMessage]) -> str:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "HTTP-Referer": self._site_url,
            "X-Title": self._app_name,
            "Content-Type": "application/json",
        }

        payload: Dict[str, Any] = {
            "model": self._model,
            "messages": [m.__dict__ for m in messages],
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self._base_url}/chat/completions",
                headers=headers,
                json=payload,
            )

            if response.status_code != 200:
                raise ExternalServiceError(f"OpenRouter error: {response.status_code} - {response.text}")

            data = response.json()
            return data["choices"][0]["message"]["content"]
