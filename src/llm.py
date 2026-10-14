"""LLM client. Works with any OpenAI-compatible endpoint.

Defaults to Google Gemini (free tier) via its OpenAI-compatible API.
Switch providers by changing LLM_BASE_URL and LLM_MODEL, e.g. Groq:
  LLM_BASE_URL=https://api.groq.com/openai/v1
  LLM_MODEL=llama-3.3-70b-versatile
"""
import os

from .config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL


class LLMError(Exception):
    pass


class LLMClient:
    def __init__(self, api_key: str = LLM_API_KEY, base_url: str = LLM_BASE_URL, model: str = LLM_MODEL):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self._client = None

    @property
    def client(self):
        if not self.api_key:
            raise LLMError("LLM_API_KEY is not set. Add it as an environment variable or Space secret.")
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=280, max_retries=3)
        return self._client

    def chat(self, messages: list[dict], temperature: float = 0.2) -> str:
        try:
            extra = {}
            effort = os.getenv("LLM_REASONING_EFFORT", "")
            if effort:
                extra["reasoning_effort"] = effort  # less "thinking" = faster answers
            resp = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=temperature, **extra
            )
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(f"LLM request failed: {e}")
        text = (resp.choices[0].message.content or "").strip()
        if not text:
            raise LLMError("The LLM returned an empty response. Try again.")
        return text
