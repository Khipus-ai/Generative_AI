# Módulo 5 · Unidad 1: Microsoft Foundry

Prácticas de generación de texto y embeddings en Python/Jupyter para el proyecto **khipus-ai-dev-chmrq**. Cada notebook es independiente y se ejecuta de arriba hacia abajo.

## Orden de trabajo

| Notebook | Actividad | Despliegue | Solicitudes por ejecución completa |
| --- | --- | --- | --- |
| [text-generation-demo.ipynb](text-generation-demo.ipynb) | Primera solicitud, roles, mejora de prompts y tokens | `gpt-4.1-mini` | 2 de chat |
| [social-posts-assignment1.ipynb](social-posts-assignment1.ipynb) | Cinco publicaciones, comparación de prompts y evaluación | `gpt-4.1-mini` | 2 de chat |
| [semantic-search_demo.ipynb](semantic-search_demo.ipynb) | Vectores, similitud coseno y búsqueda semántica | `text-embedding-3-large` | 2 de embeddings |

Los tres notebooks comparten el único archivo `requirements.txt` de esta carpeta. Los dos ejercicios de generación de texto se conectan a **Microsoft Foundry**. Las llamadas se facturan en Azure; repetir una celda de solicitud genera consumo adicional. El SDK puede reintentar errores transitorios hasta dos veces.

## 1. Entorno

Utiliza Python 3.10 o posterior. En VS Code instala las extensiones Python y Jupyter y selecciona `.venv` como intérprete y kernel. Desde esta carpeta, en PowerShell, crea el entorno virtual si todavía no existe y actívalo:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instala las dependencias compartidas una sola vez, o de nuevo solo si cambió `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

Si ya creaste y activaste `.venv` y ya instalaste los requirements, no repitas estos pasos. Luego inicia Jupyter desde el entorno activado:

```powershell
python -m jupyter lab
```

## 2. Endpoints y despliegues

**Endpoint utilizado por las tres prácticas:**

```text
https://khipus-ai-dev-chmrq-resource.openai.azure.com/openai/v1/
```

**Project Endpoint, como referencia:**

```text
https://khipus-ai-dev-chmrq-resource.services.ai.azure.com/api/projects/khipus-ai-dev-chmrq
```

El Project Endpoint corresponde a funciones de proyecto y agentes. Para estas llamadas de chat y embeddings, `OpenAI(base_url=...)` recibe el endpoint **Azure OpenAI v1**. No se añade `api-version`; tampoco se necesita el cliente `AzureOpenAI` ni un token de GitHub.

La captura proporcionada contiene los siguientes nombres. La disponibilidad efectiva y cuota se comprueban con una solicitud autenticada:

| Despliegue | Uso |
| --- | --- |
| `gpt-4.1-mini` | Predeterminado para texto |
| `gpt-4.1` | Alternativa para comparar los mismos prompts |
| `text-embedding-3-large` | Embeddings, 3072 dimensiones por defecto |

En Azure, `model` es el **nombre del despliegue**, no la versión ni un nombre con prefijo `openai/`. Las celdas de texto usan `temperature` para `gpt-4.1-mini` y `gpt-4.1`. No sustituyas directamente por un modelo de razonamiento conservando todos los parámetros.

## 3. API key

Obtén la clave del recurso **khipus-ai-dev-chmrq-resource** en Azure/Foundry. Esta clave se te ofrece de manera gratuita por tu instructor

Configura y ejecuta la celda de constantes de cada notebook antes de crear el cliente:

| Constante | Valor utilizado |
| --- | --- |
| `AZURE_OPENAI_API_KEY` | Clave del recurso proporcionada por el instructor |
| `AZURE_OPENAI_API_BASE` | `https://khipus-ai-dev-chmrq-resource.openai.azure.com/openai/v1` |
| `AZURE_OPENAI_CHAT_DEPLOYMENT` | `gpt-4.1-mini`, en los dos notebooks de texto |
| `AZURE_OPENAI_DEPLOYMENT` | `text-embedding-3-large`, en el notebook de búsqueda semántica |

La conexión toma la clave y el endpoint de estas constantes; cada solicitud usa la constante de despliegue correspondiente. No se utilizan variables de entorno ni una entrada interactiva de contraseña. La API v1 no necesita la constante `AZURE_OPENAI_API_VERSION`.

Si modificas las constantes, vuelve a ejecutar las celdas de conexión y selección del despliegue antes de enviar otra solicitud. Retira la clave de la celda de constantes antes de compartir o entregar el archivo.

## 4. Actividades y entrega

1. Ejecuta la demo de texto y explica los roles `system` y `user`.
2. Completa la tarea: compara dos prompts, llena la rúbrica y redacta tu propia mejora. El contexto es didáctico; el modelo no está consultando noticias ni navegando por Internet.
3. Ejecuta embeddings, modifica la consulta y explica los cambios en el ranking.
4. Entrega los notebooks con tus observaciones y salidas, comprobando que no incluyan credenciales. Los archivos distribuidos tienen las salidas y contadores vacíos.

## Resolver problemas

| Síntoma | Qué revisar |
| --- | --- |
| `ModuleNotFoundError: openai` | Activa `.venv`, instala `python -m pip install -r requirements.txt` y selecciona `.venv` como kernel. Reinicia el kernel si acabas de instalar el SDK. |
| Constante no definida o clave vacía | Completa y ejecuta la celda de constantes antes de la conexión; no aparece una entrada interactiva de contraseña. |
| `401` | La clave debe corresponder al recurso del endpoint; revisa si fue regenerada. |
| `403` o error de conexión | Revisa permisos y restricciones de red. Un endpoint privado puede requerir acceso a su red. |
| `404` / `DeploymentNotFound` | Comprueba despliegue, disponibilidad y ruta `/openai/v1/`. No uses el Project Endpoint como `base_url`. |
| `429` | Espera el intervalo indicado por Azure y revisa cuota/capacidad. Evita repetir celdas continuamente. |
| `400` / parámetro no admitido | Usa `gpt-4.1-mini` o `gpt-4.1` para las celdas de texto; otros modelos pueden requerir parámetros diferentes. |
| `finish_reason='length'` | Reduce la extensión solicitada o aumenta moderadamente `max_completion_tokens`. |
| Respuesta vacía/filtrada | Revisa `finish_reason` y reformula la solicitud; una salida vacía no es una generación correcta. |
