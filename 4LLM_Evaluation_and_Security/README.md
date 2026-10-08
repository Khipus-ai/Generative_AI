# Unidad 4: evaluación de LLM

## Preparar el entorno

Usa un entorno independiente de la unidad 3: Azure AI Evaluation instala sus propias dependencias. Las comprobaciones locales se realizan con Python 3.13.

Desde esta carpeta, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m jupyter lab
```

Selecciona ese entorno como kernel.

## Orden de ejecución

1. [Evaluadores NLP](1NLP_Evaluators_Case_Study.ipynb): BLEU, GLEU, METEOR y ROUGE. Se ejecutan localmente sin clave ni proyecto Azure. La preparación descarga recursos NLTK si faltan; requiere Internet la primera vez.
2. [Tarea 5](2llm_evaluation_Assignment5.ipynb): coherencia, fluidez, groundedness, relevancia y recuperación con un LLM como juez. Completa las constantes y ejecuta en orden. Se conserva el ejemplo de groundedness modificado por el estudiante.

## Conexión del juez

- `AZURE_OPENAI_API_KEY`: clave del recurso del instructor.
- `AZURE_OPENAI_API_BASE`: `https://khipus-ai-dev-chmrq-resource.openai.azure.com/openai/v1`.
- `AZURE_OPENAI_CHAT_DEPLOYMENT`: `gpt-4.1-mini`.

Se usa `OpenAIModelConfiguration` con el endpoint compatible Azure v1. No se añade `api_version` ni se utiliza el Project Endpoint. Ejecuta de nuevo la configuración y la creación de evaluadores si cambias las constantes. Las evaluaciones con juez consumen cuota de Azure; la demo NLP no hace llamadas a modelos.

## Interpretar resultados

Las métricas NLP comparan coincidencias textuales y no prueban exactitud factual. Groundedness mide el respaldo en el contexto suministrado. Retrieval evalúa la relación entre pregunta y contexto recuperado; no necesita la respuesta generada.

Los puntajes del juez pueden variar. Lee también las explicaciones y contrasta los casos manualmente. Estos notebooks cubren calidad de respuestas: no constituyen pruebas de seguridad, red teaming ni una auditoría de la aplicación.

## Problemas frecuentes

- Si falta un módulo, instala el archivo de requisitos en el mismo entorno seleccionado como kernel.
- Para un `LookupError` de NLTK, ejecuta la celda de preparación con Internet.
- Un `401/403` del juez indica revisar clave, permisos o red; un `404` requiere revisar endpoint y despliegue.
- Un `429` requiere esperar y revisar cuota.
- No publiques la clave al entregar el notebook.

Referencias: [Azure AI Evaluation SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-evaluation-readme?view=azure-python), [configuración compatible OpenAI](https://learn.microsoft.com/en-us/python/api/azure-ai-evaluation/azure.ai.evaluation.openaimodelconfiguration?view=azure-python).
