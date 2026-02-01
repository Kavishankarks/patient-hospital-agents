from __future__ import annotations
from typing import Any
import json
import re
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.core.logging import get_logger
from app.utils.json_schema import schema_from_model

logger = get_logger(__name__)

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None

class OpenAIClient:
    def __init__(self) -> None:
        if OpenAI is None:
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def _require(self) -> None:
        if self.client is None:
            raise RuntimeError('OpenAI client not available. Install openai and set OPENAI_API_KEY.')

    def generate_json(self, schema: type[BaseModel], prompt: str, input_data: str, model: str | None = None) -> BaseModel:
        self._require()
        model_name = model or settings.OPENAI_MODEL_REASONING or settings.OPENAI_MODEL_TEXT
        messages = [
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': input_data},
        ]
        try:
            response = self.client.responses.create(
                model=model_name,
                input=messages,
                response_format={"type": "json_schema", "json_schema": schema.model_json_schema()},
            )
            content = response.output_text
        except TypeError:
            schema_hint = schema_from_model(schema)
            response = self.client.responses.create(
                model=model_name,
                input=[
                    {'role': 'system', 'content': f"{prompt}\nReturn ONLY valid JSON matching this schema:\n{schema_hint}"},
                    {'role': 'user', 'content': input_data},
                ],
            )
            content = response.output_text
        try:
            return schema.model_validate_json(_extract_json_text(content))
        except ValidationError:
            # retry once with strict fix
            try:
                fix = self.client.responses.create(
                    model=model_name,
                    input=[
                        {'role': 'system', 'content': 'Fix to valid JSON only for the provided schema.'},
                        {'role': 'user', 'content': content},
                    ],
                    response_format={"type": "json_schema", "json_schema": schema.model_json_schema()},
                )
                return schema.model_validate_json(_extract_json_text(fix.output_text))
            except TypeError:
                schema_hint = schema_from_model(schema)
                fix = self.client.responses.create(
                    model=model_name,
                    input=[
                        {'role': 'system', 'content': f"Fix to valid JSON only for the provided schema:\n{schema_hint}"},
                        {'role': 'user', 'content': content},
                    ],
                )
                try:
                    return schema.model_validate_json(_extract_json_text(fix.output_text))
                except ValidationError:
                    return schema.model_validate({})

    def generate_text(self, prompt: str, input_data: str, model: str | None = None) -> str:
        self._require()
        model_name = model or settings.OPENAI_MODEL_TEXT
        response = self.client.responses.create(
            model=model_name,
            input=[{'role': 'system', 'content': prompt}, {'role': 'user', 'content': input_data}],
        )
        return response.output_text

    def transcribe_audio(self, file_path: str) -> str:
        self._require()
        with open(file_path, 'rb') as f:
            resp = self.client.audio.transcriptions.create(
                model=settings.OPENAI_MODEL_STT,
                file=f,
            )
        return resp.text

    def tts(self, text: str, voice: str, output_path: str) -> str:
        self._require()
        resp = self.client.audio.speech.create(
            model=settings.OPENAI_MODEL_TTS,
            voice=voice,
            input=text,
        )
        with open(output_path, 'wb') as f:
            f.write(resp.read())
        return output_path


def _extract_json_text(text: str) -> str:
    # Attempt to find a JSON object/array inside the model response.
    match = re.search(r'({.*}|\[.*\])', text, flags=re.DOTALL)
    if match:
        return match.group(1)
    return text
