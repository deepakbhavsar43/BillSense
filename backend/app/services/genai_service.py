import json
from typing import Any

from google import genai
from google.genai import errors, types

from app.core.config import settings


class GenAIService:
    def __init__(self, provider: str, api_key: str, model: str) -> None:
        self.provider = provider
        self.api_key = api_key
        self.model = model

    def _validate_provider(self) -> None:
        if self.provider != "gemini":
            raise NotImplementedError(
                f"Provider '{self.provider}' is not supported. Set GENAI_PROVIDER=gemini."
            )

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set.")

    async def _generate_content(
        self,
        contents: str | list[Any],
        *,
        response_json_schema: dict[str, Any] | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> str:
        self._validate_provider()

        config_kwargs: dict[str, Any] = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        if system_prompt:
            config_kwargs["system_instruction"] = system_prompt
        if response_json_schema is not None:
            config_kwargs["response_mime_type"] = "application/json"
            config_kwargs["response_json_schema"] = response_json_schema

        try:
            async with genai.Client(api_key=self.api_key).aio as client:
                response = await client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=types.GenerateContentConfig(**config_kwargs),
                )
        except errors.APIError as exc:
            raise RuntimeError(f"Gemini API error ({exc.code}): {exc.message}") from exc

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text

    @staticmethod
    def _parse_json_response(text: str) -> dict[str, Any]:
        normalized = text.strip()
        if normalized.startswith("```"):
            lines = normalized.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            normalized = "\n".join(lines).strip()
            if normalized.lower().startswith("json\n"):
                normalized = normalized[5:].strip()

        if "{" in normalized and "}" in normalized:
            start = normalized.find("{")
            end = normalized.rfind("}")
            if start < end:
                normalized = normalized[start : end + 1]

        return json.loads(normalized)

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> str:
        return await self._generate_content(
            prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def generate_json(
        self,
        prompt: str,
        response_json_schema: dict[str, Any],
        system_prompt: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 2048,
    ) -> dict[str, Any]:
        text = await self._generate_content(
            prompt,
            response_json_schema=response_json_schema,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        try:
            return self._parse_json_response(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Gemini returned malformed JSON while extracting bill data. "
                "Please retry with a clearer image or reduced text density."
            ) from exc

    async def generate_from_image(
        self,
        image_bytes: bytes,
        mime_type: str,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        contents = [
            prompt,
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
        ]
        return await self._generate_content(
            contents,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )


genai_service = GenAIService(
    provider=settings.genai_provider,
    api_key=settings.gemini_api_key,
    model=settings.gemini_model,
)
