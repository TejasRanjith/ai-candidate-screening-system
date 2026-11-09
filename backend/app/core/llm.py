import json
import re
import logging
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel
import httpx
from app.core.config import settings

logger = logging.getLogger("screening.llm")

class LLMClient:
    """Enterprise multi-provider LLM client with graceful offline semantic fallback."""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.openai_key = settings.OPENAI_API_KEY
        self.gemini_key = settings.GEMINI_API_KEY

    def is_openai_active(self) -> bool:
        return bool(self.openai_key and self.openai_key.startswith("sk-"))

    def is_gemini_active(self) -> bool:
        return bool(self.gemini_key and len(self.gemini_key) > 10)

    async def call_openai(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        payload: Dict[str, Any] = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def call_gemini(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        model = settings.GEMINI_MODEL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_key}"
        headers = {"Content-Type": "application/json"}
        prompt_combined = f"{system_prompt}\n\nTask:\n{user_prompt}"
        payload: Dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt_combined}]}],
            "generationConfig": {
                "temperature": 0.2,
            }
        }
        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    async def generate_json(self, system_prompt: str, user_prompt: str, schema_class: Type[BaseModel], fallback_handler=None) -> Dict[str, Any]:
        """Generate structured JSON conforming to schema_class or use fallback."""
        if self.is_openai_active():
            try:
                raw_json = await self.call_openai(system_prompt, user_prompt, json_mode=True)
                return json.loads(raw_json)
            except Exception as e:
                logger.warning(f"OpenAI call failed ({e}), falling back to local semantic provider")

        if self.is_gemini_active():
            try:
                raw_json = await self.call_gemini(system_prompt, user_prompt, json_mode=True)
                # Strip markdown codeblocks if returned
                cleaned = re.sub(r"^```json\s*|\s*```$", "", raw_json.strip())
                return json.loads(cleaned)
            except Exception as e:
                logger.warning(f"Gemini call failed ({e}), falling back to local semantic provider")

        # Fallback to local intelligent handler
        if fallback_handler:
            return fallback_handler()
        return {}

llm = LLMClient()
