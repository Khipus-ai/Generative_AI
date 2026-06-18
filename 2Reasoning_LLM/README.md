# Khipus AI — Demos para webinar

Demos listas para presentar el tema: **El nuevo rol del profesional Tech en la era de la IA Generativa**.

Incluye dos variantes:

1. `terminal_demo.py`: demo por consola.
2. `ui_demo.py`: demo web con Flask.

## Importante sobre el razonamiento visible

La demo permite mostrar un bloque llamado **Razonamiento visible del agente**.

Ese bloque no es cadena de pensamiento interna oculta. Es una trazabilidad breve, segura y presentable para explicar a la audiencia cómo se orientó la respuesta.

Esto es más profesional para un webinar porque permite transparencia sin exponer deliberaciones internas extensas.

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edita `.env` con tu endpoint, clave nueva y deployment:

```env
AZURE_ENDPOINT=https://<tu-recurso>.services.ai.azure.com/openai/v1
AZURE_KEY=<tu-clave-regenerada>
AZURE_DEPLOYMENT=DeepSeek-V3.2
```

## Demo terminal

```bash
python terminal_demo.py
```

Comandos útiles:

```txt
/ayuda
/config
/razonamiento on
/razonamiento off
/limpiar
/salir
```

## Demo UI

```bash
python ui_demo.py
```

Abrir:

```txt
http://127.0.0.1:5000
```

La UI incluye:

- Modo general.
- Modo ingeniería / arquitectura.
- Modo valor de negocio.
- Modo docencia.
- Toggle para mostrar u ocultar el razonamiento visible.
- Streaming de respuesta.
- Branding Khipus.

## Seguridad

No imprimas `AZURE_KEY` en consola.
No subas `.env` a repositorios.
Si una clave fue compartida por error, regénérala antes de usar la demo.
