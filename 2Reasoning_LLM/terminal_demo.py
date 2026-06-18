"""
Demo 1: Terminal profesional para Azure OpenAI / Microsoft Foundry Models v1.

Comandos:
  /salir              termina la demo
  /limpiar            limpia la pantalla
  /ayuda              muestra ejemplos rápidos
  /config             muestra configuración segura, sin imprimir la clave
  /razonamiento on    muestra trazabilidad visible del agente
  /razonamiento off   oculta trazabilidad visible del agente
"""

from __future__ import annotations

import os
import sys

from openai import APIConnectionError, APIError, AuthenticationError, BadRequestError, OpenAIError, RateLimitError
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.status import Status

from common import build_client, build_messages, create_chat_stream, iter_response_text, split_visible_reasoning

console = Console()


EXAMPLES = [
    "Explica qué es Deep Learning con una analogía para profesionales Tech.",
    "Tengo un proceso manual de revisión de documentos. ¿Cómo podría convertirlo en una solución con IA?",
    "Dame 5 riesgos técnicos al integrar un LLM en una aplicación empresarial.",
    "Explícame la diferencia entre usar IA como usuario y construir soluciones con IA.",
]


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_header(endpoint_host: str, endpoint: str, deployment: str, show_reasoning: bool) -> None:
    reasoning_state = "activado" if show_reasoning else "desactivado"
    console.print(
        Panel.fit(
            f"[bold cyan]Khipus AI — Demo Terminal[/bold cyan]\n"
            f"[white]Modelo/Deployment:[/white] [bold]{deployment}[/bold]\n"
            f"[white]Endpoint host:[/white] {endpoint_host}\n"
            f"[white]API:[/white] OpenAI v1\n"
            f"[white]Razonamiento visible:[/white] {reasoning_state}\n\n"
            "[dim]La clave nunca se imprime. Usa /ayuda para ejemplos.[/dim]",
            border_style="cyan",
        )
    )


def print_help() -> None:
    console.print(
        Panel(
            "\n".join(f"• {example}" for example in EXAMPLES)
            + "\n\n[dim]Comandos útiles: /razonamiento on · /razonamiento off · /config[/dim]",
            title="Prompts sugeridos",
            border_style="green",
        )
    )


def print_config(settings, show_reasoning: bool) -> None:
    console.print(
        Panel.fit(
            f"[white]Endpoint usado:[/white] {settings.endpoint}\n"
            f"[white]Deployment:[/white] {settings.deployment}\n"
            f"[white]Timeout:[/white] {settings.timeout_seconds}s\n"
            f"[white]Razonamiento visible:[/white] {'sí' if show_reasoning else 'no'}\n"
            f"[white]Clave:[/white] [dim]oculta por seguridad[/dim]",
            title="Configuración segura",
            border_style="blue",
        )
    )


def explain_openai_error(exc: OpenAIError) -> str:
    if isinstance(exc, BadRequestError):
        return (
            "Solicitud rechazada por Azure. Revisa principalmente: endpoint /openai/v1, "
            "nombre exacto del deployment en AZURE_DEPLOYMENT y compatibilidad del modelo.\n"
            f"Detalle: {exc}"
        )
    if isinstance(exc, AuthenticationError):
        return "Autenticación fallida. Revisa AZURE_KEY o regenera la clave del recurso."
    if isinstance(exc, RateLimitError):
        return "Límite de uso alcanzado. Espera unos segundos o revisa cuota/rate limit del deployment."
    if isinstance(exc, APIConnectionError):
        return "No se pudo conectar con Azure. Revisa red, endpoint y proxy/firewall."
    if isinstance(exc, APIError):
        return f"Error de API desde Azure/OpenAI SDK: {exc}"
    return str(exc)


def ask_model(client, deployment: str, prompt: str, mode: str = "ingenieria", show_reasoning: bool = True) -> None:
    messages = build_messages(prompt, mode=mode, include_visible_reasoning=show_reasoning)

    try:
        stream = create_chat_stream(client, deployment, messages)
    except OpenAIError as exc:
        console.print(f"\n[bold red]Error desde Azure/OpenAI SDK:[/bold red] {explain_openai_error(exc)}")
        return
    except Exception as exc:  # noqa: BLE001 - demo CLI, mensaje controlado
        console.print(f"\n[bold red]Error inesperado:[/bold red] {exc}")
        return

    collected: list[str] = []
    try:
        with Status("[cyan]Generando respuesta...[/cyan]", console=console, spinner="dots"):
            for token in iter_response_text(stream):
                collected.append(token)
    except OpenAIError as exc:
        console.print(f"\n[bold red]Error durante streaming:[/bold red] {explain_openai_error(exc)}")
        return
    except Exception as exc:  # noqa: BLE001
        console.print(f"\n[bold red]Error durante streaming:[/bold red] {exc}")
        return

    raw = "".join(collected).strip()
    visible_reasoning, answer = split_visible_reasoning(raw)

    if show_reasoning and visible_reasoning:
        console.print(
            Panel(
                Markdown(visible_reasoning),
                title="Razonamiento visible del agente",
                border_style="yellow",
            )
        )

    console.print(
        Panel(
            Markdown(answer or raw),
            title="Respuesta final",
            border_style="cyan",
        )
    )


def main() -> int:
    try:
        client, settings = build_client()
    except RuntimeError as exc:
        console.print(f"[bold red]{exc}[/bold red]")
        return 1

    show_reasoning = True

    clear_screen()
    print_header(settings.endpoint_host, settings.endpoint, settings.deployment, show_reasoning)
    print_help()

    while True:
        try:
            user_input = Prompt.ask("\n[bold green]Tú[/bold green]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Demo finalizada.[/dim]")
            return 0

        if not user_input:
            continue

        command = user_input.lower()
        if command in {"/salir", "salir", "exit", "quit"}:
            console.print("[dim]Demo finalizada.[/dim]")
            return 0
        if command in {"/limpiar", "clear", "cls"}:
            clear_screen()
            print_header(settings.endpoint_host, settings.endpoint, settings.deployment, show_reasoning)
            continue
        if command in {"/ayuda", "help", "?"}:
            print_help()
            continue
        if command in {"/config", "config"}:
            print_config(settings, show_reasoning)
            continue
        if command in {"/razonamiento on", "razonamiento on"}:
            show_reasoning = True
            console.print("[green]Razonamiento visible activado.[/green]")
            continue
        if command in {"/razonamiento off", "razonamiento off"}:
            show_reasoning = False
            console.print("[yellow]Razonamiento visible desactivado.[/yellow]")
            continue

        ask_model(client, settings.deployment, user_input, show_reasoning=show_reasoning)


if __name__ == "__main__":
    sys.exit(main())
