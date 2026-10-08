# **Khipus.ai**
# Unidad 3: Retrieval-Augmented Generation
# © Copyright Notice 2025, Khipus.ai - All Rights Reserved.

## Ejecutar los laboratorios

Usa Python 3.10–3.13 y un entorno propio de esta unidad. Desde esta carpeta:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m jupyter lab
```

Selecciona ese entorno como kernel. También puedes abrir los notebooks desde la raíz del repositorio; el código resuelve la carpeta de los PDFs.

1. **Assignment 3:** completa `PINECONE_API_KEY` y crea o valida el índice.
2. **Case Study RAG:** completa las constantes de Azure y Pinecone y ejecuta de arriba hacia abajo.
3. **Assignment 4:** conserva celdas intencionalmente vacías. Complétalas siguiendo el caso de estudio; no es una solución terminada.

Los tres notebooks usan el índice `khipus-unit3-3072`, de **3072 dimensiones**, compatible con el despliegue `text-embedding-3-large`. El modelo de chat es `gpt-4.1-mini` y el endpoint de Azure termina en `/openai/v1/`. Los valores se toman de constantes, como en la unidad 1.

Si ya tienes un índice de 1536 dimensiones, elige un nombre diferente para estas prácticas. No se borran índices ni datos existentes. La región predeterminada es AWS `us-east-1`; revisa los límites y costos de tu plan antes de crear recursos. La cuenta puede limitar la cantidad de índices.

Cada documento/versión usa su propio namespace. La demo usa IDs estables, lotes pequeños y espera tanto la preparación del índice como la visibilidad de los vectores. Repetir la ingesta no duplica los mismos fragmentos, pero vuelve a consumir embeddings y operaciones de Pinecone. Si modificas el contenido o la segmentación, se conserva la versión previa en otro namespace.

Las dependencias usan `PyPDFLoader/pypdf`. No se necesitan `pdfminer`, `unstructured`, Tesseract ni Poppler para los PDFs incluidos. Los PDFs escaneados requerirían OCR adicional.

### Comprobaciones y errores

- Las claves de Azure y Pinecone son diferentes; completa ambas sin compartirlas en la entrega.
- `401/403`: revisa credenciales y acceso al recurso; `404`: endpoint o despliegue.
- `429`: espera y revisa cuotas; evita ejecutar la ingesta repetidamente.
- Error de dimensión/métrica: utiliza otro índice que corresponda al modelo; no borres un índice con datos.
- `TimeoutError` o búsqueda sin resultados: espera a Pinecone y verifica el namespace.
- En la tarea 4, `docs` y `vectorstore` solo existen después de completar las celdas del estudiante.

Referencias: [Azure OpenAI v1 con LangChain](https://docs.langchain.com/oss/python/integrations/chat/azure_chat_openai), [creación de índices Pinecone](https://docs.pinecone.io/guides/index-data/create-an-index).

---

## Crear una cuenta Pinecone (guía de referencia)

This guide walks you through setting up a **free Pinecone vector database account**, completing the onboarding questionnaire, and generating your first API key.

---

## Prerequisites

- A valid **Google, GitHub, or Microsoft** account _(or an email address you can verify)._
- A modern web browser (Chrome, Edge, Firefox, Safari).

---

## 1  Navigate to the Pinecone sign‑in page

1. Open a browser and go to <https://www.pinecone.io/> and select **Sing up**.
2. Click **Continue with Google** (highlighted in the screenshot below).  
   _You may instead choose GitHub, Microsoft, or sign up with email._


![alt text](images/image.png)
---

## 2  Complete the account details form

After authentication you will be asked to **customize your Pinecone setup**:

| Field | Example value |
|-------|---------------|
| **First Name** | Your Name |
| **Last Name** |  Your Last neme|
| **Purpose of use** | Business |
| **Company** | Khipus.ai |
| **Preferred coding language** | Python |

1. Fill in each field.  
2. Select your preferred language (Python is shown selected).  
3. Click **Continue**.

![alt text](images/image-1.png)

---

## 3  Tell Pinecone what you plan to build

1. Choose the primary use‑case. In the example we select **AI Agents**.  
2. Estimate the size of your corpus (e.g. **Less than 100 k** documents).  
3. Click **Continue**.

![alt text](images/image-2.png)
---

## 4  Specify your embedding model status

Select the option that best fits your workflow. Most developers who already work with OpenAI or another embedding provider should choose **I have an embedding model**.  
After selecting, click **Let’s Get Started**.


![alt text](images/image-3.png)

---

## 5  Generate and save your API key

Pinecone immediately issues a **default** API key:

![alt text](images/image-4.png)

> **Important:** The key is shown **only once**. Click the clipboard icon to copy it, then store it in a secure location such as an environment variable manager (e.g., GitHub Secrets, Azure Key Vault, or a local `.env` file).
