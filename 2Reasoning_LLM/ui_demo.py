"""
Demo 2: Interfaz web Flask para presentar Azure AI en un webinar.

Ejecutar:
  python ui_demo.py

Luego abrir:
  http://127.0.0.1:5000
"""

from __future__ import annotations

import os
from typing import Generator

from flask import Flask, Response, jsonify, render_template, request
from openai import APIConnectionError, APIError, AuthenticationError, BadRequestError, OpenAIError, RateLimitError

from common import build_client, build_messages, create_chat_stream, iter_response_text

app = Flask(__name__)
client, settings = build_client()


def explain_openai_error(exc: OpenAIError) -> str:
    if isinstance(exc, BadRequestError):
        return (
            "Solicitud rechazada por Azure. Revisa endpoint /openai/v1, "
            "AZURE_DEPLOYMENT y compatibilidad del modelo. "
            f"Detalle: {exc}"
        )
    if isinstance(exc, AuthenticationError):
        return "Autenticación fallida. Revisa AZURE_KEY o regenera la clave del recurso."
    if isinstance(exc, RateLimitError):
        return "Límite de uso alcanzado. Espera unos segundos o revisa cuota/rate limit."
    if isinstance(exc, APIConnectionError):
        return "No se pudo conectar con Azure. Revisa red, endpoint y proxy/firewall."
    if isinstance(exc, APIError):
        return f"Error de API desde Azure/OpenAI SDK: {exc}"
    return str(exc)


@app.get("/")
def home():
    return render_template(
        "index.html",
        deployment=settings.deployment,
        endpoint_host=settings.endpoint_host,
    )


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    user_message = str(payload.get("message", "")).strip()
    mode = str(payload.get("mode", "general")).strip()
    show_reasoning = bool(payload.get("showReasoning", True))

    if not user_message:
        return jsonify({"error": "El mensaje no puede estar vacío."}), 400
    if len(user_message) > 4000:
        return jsonify({"error": "El mensaje es demasiado largo para esta demo."}), 413

    messages = build_messages(user_message, mode=mode, include_visible_reasoning=show_reasoning)

    def generate() -> Generator[str, None, None]:
        try:
            stream = create_chat_stream(client, settings.deployment, messages)
            for token in iter_response_text(stream):
                yield token
        except OpenAIError as exc:
            yield f"\n\n[Error desde Azure/OpenAI SDK] {explain_openai_error(exc)}"
        except Exception as exc:  # noqa: BLE001 - demo controlada
            yield f"\n\n[Error inesperado] {exc}"

    return Response(
        generate(),
        mimetype="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="127.0.0.1", port=5000, debug=debug)
