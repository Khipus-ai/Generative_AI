"""
Utilidades compartidas para las demos Khipus AI.

Versión para Azure OpenAI / Microsoft Foundry Models v1 API.
Usa el SDK oficial `openai` contra endpoints con formato:

    https://<resource>.services.ai.azure.com/openai/v1
    https://<resource>.openai.azure.com/openai/v1

Nota profesional para la demo:
- No se expone cadena de pensamiento interna oculta.
- Se puede mostrar un "razonamiento visible" breve: una trazabilidad resumida,
  segura y presentable para audiencia.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Iterable, Optional
from urllib.parse import urlparse

from dotenv import load_dotenv
from openai import OpenAI


DEMO_SYSTEM_PROMPT = """
Eres un asistente técnico para un webinar llamado
"El nuevo rol del profesional Tech en la era de la IA Generativa".

Responde siempre en español, con tono profesional, claro e inspirador.
Prioriza criterio técnico, aplicabilidad real y buenas prácticas.
No inventes datos: cuando algo dependa del contexto, dilo explícitamente.

Regla importante de transparencia:
- No reveles razonamiento interno oculto ni cadena de pensamiento detallada.
- Cuando se solicite razonamiento visible, muestra una trazabilidad breve y segura,
  útil para explicar a una audiencia cómo orientaste la respuesta.
- Esa trazabilidad debe ser máximo 3 bullets, sin pasos privados extensos.
""".strip()


PROMPT_MODES = {
    "general": "Responde de forma clara, profesional y orientada a aprendizaje.",
    "ingenieria": "Enfoca la respuesta como arquitectura de solución: componentes, riesgos, validación y mantenimiento.",
    "negocio": "Conecta la respuesta con valor empresarial: productividad, ahorro, calidad, riesgo e impacto operativo.",
    "docencia": "Explica de forma didáctica, usando analogías y ejemplos simples sin perder precisión técnica.",
}


@dataclass(frozen=True)
class Settings:
    endpoint: str
    key: str
    deployment: str
    timeout_seconds: int = 60

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()

        missing = [name for name in ("AZURE_ENDPOINT", "AZURE_KEY", "AZURE_DEPLOYMENT") if not os.getenv(name)]
        if missing:
            joined = ", ".join(missing)
            raise RuntimeError(
                f"Faltan variables de entorno: {joined}. "
                "Crea un archivo .env tomando como base .env.example."
            )

        try:
            timeout = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "60"))
        except ValueError:
            timeout = 60

        endpoint = normalize_openai_v1_endpoint(os.environ["AZURE_ENDPOINT"].strip())

        return cls(
            endpoint=endpoint,
            key=os.environ["AZURE_KEY"].strip(),
            deployment=os.environ["AZURE_DEPLOYMENT"].strip(),
            timeout_seconds=timeout,
        )

    @property
    def endpoint_host(self) -> str:
        parsed = urlparse(self.endpoint)
        return parsed.netloc or self.endpoint


def normalize_openai_v1_endpoint(raw_endpoint: str) -> str:
    """
    Normaliza el endpoint para OpenAI SDK.

    Casos soportados:
    - https://recurso.services.ai.azure.com/openai/v1
    - https://recurso.openai.azure.com/openai/v1
    - https://recurso.services.ai.azure.com  -> agrega /openai/v1
    - https://recurso.openai.azure.com      -> agrega /openai/v1

    Casos rechazados:
    - .../models, porque ese formato pertenece al Azure AI Inference SDK.
    """
    endpoint = raw_endpoint.strip().strip('"').strip("'").rstrip("/")

    if not endpoint:
        raise RuntimeError("AZURE_ENDPOINT está vacío.")

    if endpoint.endswith("/models"):
        raise RuntimeError(
            "AZURE_ENDPOINT parece ser un endpoint del Azure AI Inference SDK (.../models). "
            "Para esta demo usa el endpoint OpenAI v1: "
            "https://<resource>.services.ai.azure.com/openai/v1"
        )

    if "/openai/v1" in endpoint:
        return endpoint.split("/openai/v1", maxsplit=1)[0] + "/openai/v1"

    parsed = urlparse(endpoint)
    host = parsed.netloc.lower()
    if host.endswith(".services.ai.azure.com") or host.endswith(".openai.azure.com"):
        return endpoint + "/openai/v1"

    return endpoint


def build_client(settings: Optional[Settings] = None) -> tuple[OpenAI, Settings]:
    settings = settings or Settings.from_env()
    client = OpenAI(
        api_key=settings.key,
        base_url=settings.endpoint,
        timeout=settings.timeout_seconds,
    )
    return client, settings


def build_messages(user_message: str, mode: str = "general", include_visible_reasoning: bool = True) -> list[dict[str, str]]:
    mode_instruction = PROMPT_MODES.get(mode, PROMPT_MODES["general"])

    if include_visible_reasoning:
        output_contract = """
Formato obligatorio de salida:
<razonamiento_visible>
- Primer criterio usado para orientar la respuesta.
- Segundo criterio usado para conectar con el contexto profesional.
- Tercer criterio, solo si aporta valor.
</razonamiento_visible>

<respuesta>
Tu respuesta final en Markdown claro y profesional.
</respuesta>

Restricciones:
- El bloque <razonamiento_visible> NO debe ser cadena de pensamiento interna.
- Debe ser una explicación breve, segura y presentable para una audiencia.
- No incluyas razonamiento oculto, dudas internas, deliberación privada ni pasos excesivos.
""".strip()
    else:
        output_contract = """
Formato de salida:
Responde directamente en Markdown claro y profesional.
No incluyas etiquetas XML.
No muestres razonamiento interno oculto.
""".strip()

    system_prompt = (
        f"{DEMO_SYSTEM_PROMPT}\n\n"
        f"Modo de respuesta: {mode_instruction}\n\n"
        f"{output_contract}"
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message.strip()},
    ]


def create_chat_stream(client: OpenAI, deployment: str, messages: list[dict[str, str]]) -> Iterable:
    """Crea un stream de Chat Completions usando OpenAI SDK."""
    return client.chat.completions.create(
        model=deployment,
        messages=messages,
        stream=True,
    )


def iter_response_text(stream: Iterable) -> Iterable[str]:
    """Extrae texto incremental de una respuesta streaming del OpenAI SDK."""
    for chunk in stream:
        if not getattr(chunk, "choices", None):
            continue
        delta = chunk.choices[0].delta
        content = getattr(delta, "content", None)
        if content:
            yield content


def split_visible_reasoning(raw_text: str) -> tuple[str, str]:
    """
    Separa una respuesta con etiquetas:
      <razonamiento_visible>...</razonamiento_visible>
      <respuesta>...</respuesta>

    Devuelve: (razonamiento_visible, respuesta_final)
    Si el modelo no respeta el formato, devuelve razonamiento vacío y texto completo como respuesta.
    """
    text = (raw_text or "").strip()

    reasoning_match = re.search(
        r"<razonamiento_visible>\s*([\s\S]*?)\s*</razonamiento_visible>",
        text,
        flags=re.IGNORECASE,
    )
    answer_match = re.search(
        r"<respuesta>\s*([\s\S]*?)\s*</respuesta>",
        text,
        flags=re.IGNORECASE,
    )

    reasoning = reasoning_match.group(1).strip() if reasoning_match else ""
    answer = answer_match.group(1).strip() if answer_match else ""

    if answer:
        return reasoning, answer

    # Fallback: elimina etiquetas sueltas si las hubiera.
    cleaned = re.sub(r"</?(razonamiento_visible|respuesta)>", "", text, flags=re.IGNORECASE).strip()
    return reasoning, cleaned
