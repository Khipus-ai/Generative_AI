import os
import re
from flask import Flask, request, Response, render_template_string
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from azure.ai.inference.models import SystemMessage, UserMessage

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize the ChatCompletionsClient
client = ChatCompletionsClient(
    endpoint=os.environ["AZURE_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["AZURE_KEY"]),
)

@app.route('/')
def home():
    return render_template_string(r'''
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width,initial-scale=1" />
            <title>Khipus AI — Caso de Estudio</title>
            <style>
                :root{
                --bg:#0f1724; /* deep navy */
                --panel:#0b1220;
                --muted:#9aa4b2;
                --accent:#5eead4; /* teal */
                --accent-2:#60a5fa; /* blue */
                --user:#1f2937;
                --assistant:#e6f2ff;
                --glass: rgba(255,255,255,0.04);
                }
                *{box-sizing:border-box}
                body{
                margin:0; font-family:Inter, Segoe UI, Roboto, Arial, sans-serif;
                background:linear-gradient(180deg,var(--bg),#071226);
                color:#e6eef6; min-height:100vh;
                display:flex; flex-direction:column; align-items:center;
                padding:28px;
                }

                /* === Encabezado principal === */
                header{
                width:100%; max-width:980px;
                margin-bottom:30px;
                text-align:center;
                padding:24px 20px;
                background:transparent; /* sin fondo, usa el fondo global */
                }
                header h1{
                margin:0;
                font-size:36px; /* más grande */
                font-weight:800;
                color:#ffffff; /* blanco */
                }
                header p{
                margin:10px 0 0;
                font-size:18px; /* más grande */
                color:#ffffff; /* blanco */
                opacity:0.85;
                }

                .app {
                width:100%; max-width:980px;
                background:linear-gradient(180deg,var(--panel), rgba(11,18,32,0.9));
                border-radius:14px;
                box-shadow:0 10px 30px rgba(2,6,23,0.7);
                overflow:hidden;
                display:grid;
                grid-template-columns:1fr 360px;
                gap:0;
                }
                .panel-left{padding:28px}
                .brand{display:flex; align-items:center; gap:14px}
                .logo{width:52px; height:52px; border-radius:10px;
                background:linear-gradient(135deg,var(--accent),var(--accent-2));
                display:flex; align-items:center; justify-content:center;
                font-weight:700; color:#04263b}
                h2{font-size:20px; margin:0}
                p.lead{margin:6px 0 18px; color:var(--muted)}

                #messages{height:64vh; max-height:820px; overflow:auto;
                padding:18px; background:linear-gradient(180deg, rgba(255,255,255,0.02), transparent);
                border-radius:8px; border:1px solid rgba(255,255,255,0.03)}
                .msg{display:flex; gap:12px; margin-bottom:14px; align-items:flex-start}
                .avatar{width:44px; height:44px; border-radius:10px;
                display:flex; align-items:center; justify-content:center; font-weight:700}
                .avatar.user{background:linear-gradient(180deg,#111827,#0b1220); color:#fff}
                .avatar.assistant{background:linear-gradient(180deg,var(--assistant),#dbeeff); color:#052040}
                .bubble{max-width:78%; padding:12px 14px; border-radius:12px; line-height:1.4}
                .bubble.user{background:linear-gradient(180deg,#0b1220,var(--glass)); color:#dbe7f2; border:1px solid rgba(255,255,255,0.03); margin-left:auto}
                .bubble.assistant{background:linear-gradient(180deg,#ffffff,#f0f7ff); color:#04263b; border:1px solid rgba(6,22,39,0.04)}
                .thinking{font-style:italic; color:var(--muted); background:linear-gradient(180deg,#fff6d6,#fff9e6); border:1px solid rgba(0,0,0,0.04)}
                .meta{font-size:12px; color:var(--muted); margin-top:6px}

                .composer{display:flex; gap:8px; margin-top:16px}
                .composer input{flex:1; padding:12px 14px; border-radius:10px; border:1px solid rgba(255,255,255,0.04); background:transparent; color:inherit}
                .composer button{padding:10px 14px; border-radius:10px; border:none;
                background:linear-gradient(90deg,var(--accent),var(--accent-2));
                color:#04263b; font-weight:600; cursor:pointer}
                .composer button[disabled]{opacity:0.6; cursor:not-allowed}
                .right-column{padding:22px; border-left:1px solid rgba(255,255,255,0.02);
                background:linear-gradient(180deg, rgba(255,255,255,0.02), transparent)}
                .small{font-size:13px; color:var(--muted)}

                @media (max-width:900px){
                .app{grid-template-columns:1fr}
                .right-column{display:none}
                }
            </style>
        </head>

        <body>
        <!-- Nuevo encabezado -->
            <header>
                <h1>Khipus AI — Caso de Estudio</h1>
                <p>Interfaz práctica para visualización de razonamiento interno</p>
            </header>

            <div class="app">
                <div class="panel-left">
                <div class="brand">
                    <div class="logo">DK</div>
                    <div>
                    <h2>DeepSeek — Chatbot</h2>
                    <p class="lead">Assignment 2 · Añade tu nombre arriba · Streaming con razonamiento interno (etiquetado &lt;think&gt;).</p>
                    </div>
                </div>

                <div id="messages" role="log" aria-live="polite"></div>

                <form class="composer" onsubmit="sendMessage(event)">
                    <input id="input" autocomplete="off" placeholder="Escribe tu mensaje y presiona Enter..." />
                    <button id="sendBtn" type="submit">Enviar</button>
                </form>
                <div class="meta small">© 2025 Khipus.ai — Práctica local. Añade tu nombre en el código si lo deseas.</div>
                </div>

                <aside class="right-column">
                <h3 class="small">Estado</h3>
                <div id="status" class="small">Listo</div>
                <hr/>
                <h4 class="small">Instrucciones</h4>
                <p class="small">El asistente incluye su razonamiento interno entre &lt;think&gt;...&lt;/think&gt; antes de la respuesta final. Verás primero el razonamiento (si existe) y luego la respuesta.</p>
                </aside>
            </div>

            <script>
                // Simple HTML escape
                function escapeHtml(str){
                    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
                }

                // Minimal Markdown -> HTML renderer (handles paragraphs, bold, italic, inline code, code blocks, links, line breaks)
                function renderMarkdown(md){
                    if(!md) return '';
                    // Normalize CRLF
                    md = md.replace(/\r\n/g,'\n');

                    // Extract code blocks first
                    md = md.replace(/```([\s\S]*?)```/g, function(_, code){
                        return '<pre><code>' + escapeHtml(code) + '</code></pre>';
                    });

                    // Escape remaining HTML
                    md = escapeHtml(md);

                    // Inline code `code`
                    md = md.replace(/`([^`]+)`/g, function(_, c){ return '<code>' + escapeHtml(c) + '</code>'; });

                    // Bold **text** or __text__
                    md = md.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
                    md = md.replace(/__([^_]+)__/g, '<strong>$1</strong>');

                    // Italic *text* or _text_
                    md = md.replace(/\*([^*]+)\*/g, '<em>$1</em>');
                    md = md.replace(/_([^_]+)_/g, '<em>$1</em>');

                    // Links [text](url)
                    md = md.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

                    // Convert two or more newlines to paragraph breaks
                    const parts = md.split(/\n{2,}/g).map(p => p.replace(/\n/g,'<br/>'));
                    return parts.map(p => '<p>' + p + '</p>').join('');
                }

                // Helper to append messages with avatars. If opts.html=true, bubble.innerHTML will be used.
                function appendMessage(text, who, opts = {}){
                    const messages = document.getElementById('messages');
                    const wrapper = document.createElement('div');
                    wrapper.className = 'msg ' + (who === 'user' ? 'user' : 'assistant');

                    const avatar = document.createElement('div');
                    avatar.className = 'avatar ' + (who === 'user' ? 'user' : 'assistant');
                    avatar.textContent = who === 'user' ? 'Tú' : 'AI';

                    const bubble = document.createElement('div');
                    bubble.className = 'bubble ' + (who === 'user' ? 'user' : 'assistant');
                    if(opts.html) bubble.innerHTML = text || '';
                    else bubble.textContent = text || '';

                    wrapper.appendChild(avatar);
                    wrapper.appendChild(bubble);

                    // If an insertBefore node is provided, insert before that node instead of appending.
                    if(opts.insertBefore && opts.insertBefore.nodeType){
                        messages.insertBefore(wrapper, opts.insertBefore);
                    } else if(opts.insertAtTop){
                        messages.insertBefore(wrapper, messages.firstChild);
                    } else {
                        messages.appendChild(wrapper);
                    }

                    messages.scrollTop = messages.scrollHeight - 20;
                    return {wrapper, bubble};
                }

                async function sendMessage(e){
                    e.preventDefault();
                    const input = document.getElementById('input');
                    const sendBtn = document.getElementById('sendBtn');
                    const raw = input.value || '';
                    const message = raw.trim();
                    if(!message) return;

                    // Optimistic UI
                    appendMessage(escapeHtml(message), 'user', {html:false});
                    input.value = '';
                    input.disabled = true; sendBtn.disabled = true; document.getElementById('status').textContent = 'Enviando...';

                    try{
                        const res = await fetch('/chat', {
                            method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({message})
                        });

                        if(!res.ok){
                            appendMessage('Error del servidor: ' + res.statusText, 'assistant');
                            return;
                        }

                        // Prepare UI placeholders: create the response bubble first, then insert thinking above it
                        let thinkingElement = null;
                        const responseObj = appendMessage('', 'assistant', {html:true});
                        let responseElement = responseObj.bubble;

                        if(res.body && res.body.getReader){
                            const reader = res.body.getReader();
                            const decoder = new TextDecoder();
                            let {value, done} = await reader.read();
                            let buffer = '';

                            while(!done){
                                if(value) buffer += decoder.decode(value, {stream:true});

                                // Process all complete <think> blocks available in buffer
                                let keepProcessing = true;
                                while(keepProcessing){
                                    keepProcessing = false;
                                    const start = buffer.indexOf('<think>');
                                    const end = buffer.indexOf('</think>');
                                    if(start !== -1 && end !== -1 && end > start){
                                        const thinkText = buffer.substring(start + 7, end).trim();
                                        // append or update thinking element and ensure it's above the response
                                        if(!thinkingElement) thinkingElement = appendMessage('', 'assistant', {html:true, insertBefore: responseObj.wrapper}).bubble;
                                        thinkingElement.classList.add('thinking');
                                        thinkingElement.innerHTML = '<strong style="font-size:12px;color:#06335a;">Pensamiento:</strong><br/>' + renderMarkdown(thinkText);
                                        // remove processed part
                                        buffer = buffer.substring(0, start) + buffer.substring(end + 8);
                                        keepProcessing = true; // there might be more <think> blocks
                                    }
                                }

                                // If there is an unterminated <think> start (partial), show partial thinking
                                const partialStart = buffer.indexOf('<think>');
                                if(partialStart !== -1 && buffer.indexOf('</think>') === -1){
                                    const partial = buffer.substring(partialStart + 7).trim();
                                    if(!thinkingElement) thinkingElement = appendMessage('', 'assistant', {html:true, insertBefore: responseObj.wrapper}).bubble;
                                    thinkingElement.classList.add('thinking');
                                    thinkingElement.innerHTML = '<strong style="font-size:12px;color:#06335a;">Pensamiento:</strong><br/>' + renderMarkdown(partial);
                                    // keep buffer as-is because response may arrive after closing tag
                                }

                                // The rest of buffer (without any <think> blocks) is response content
                                // Remove any stray tags and render markdown
                                let safeBuffer = buffer.replace(/<think>/g,'').replace(/<\/think>/g,'');
                                if(safeBuffer.trim().length > 0){
                                    responseElement.innerHTML = renderMarkdown(safeBuffer);
                                }

                                ({value, done} = await reader.read());
                            }

                            // Final flush
                            const tail = decoder.decode();
                            if(tail) buffer += tail;
                            // Clean remaining tags
                            buffer = buffer.replace(/<think>/g,'').replace(/<\/think>/g,'').trim();
                            if(buffer.length > 0) responseElement.innerHTML = renderMarkdown(buffer);

                        } else {
                            // Fallback non-stream
                            const text = await res.text();
                            // If contains think block, separate it
                            const m = text.match(/<think>([\s\S]*?)<\/think>/);
                            if(m){
                                const thinkText = m[1].trim();
                                // ensure thinking is inserted above the response
                                const respObj = appendMessage('', 'assistant', {html:true});
                                const thinkEl = appendMessage('', 'assistant', {html:true, insertBefore: respObj.wrapper}).bubble;
                                thinkEl.classList.add('thinking');
                                thinkEl.innerHTML = '<strong style="font-size:12px;color:#06335a;">Pensamiento:</strong><br/>' + renderMarkdown(thinkText);
                                const rest = text.replace(m[0], '').trim();
                                respObj.bubble.innerHTML = renderMarkdown(rest);
                            } else {
                                appendMessage(renderMarkdown(text), 'assistant', {html:true});
                            }
                        }

                    }catch(err){
                        console.error(err);
                        appendMessage('Error de red o interno: ' + (err.message||err), 'assistant');
                    } finally {
                        document.getElementById('status').textContent = 'Listo';
                        input.disabled = false; sendBtn.disabled = false; input.focus();
                    }
                }

                // focus input on load
                window.addEventListener('load', ()=>{ document.getElementById('input').focus(); });
            </script>
        </body>
        </html>
    ''')

@app.route('/chat', methods=['POST'])
def chat():
    """
    Streams partial chunks so the client receives tokens incrementally.
    """
    data = request.get_json()
    user_message = data['message']

    messages = [
        SystemMessage(content="You are a helpful assistant. Include internal reasoning wrapped in <think>...</think> before providing the final answer."),
        UserMessage(content=user_message),
    ]

    # Add the model parameter to the call
    stream = client.complete(
        messages=messages,
        model="DeepSeek-R1",  # Specify your deployment model
        stream=True
    )

    def generate():
        """
        Generator that yields partial tokens as they come in.
        The front-end code will gather chunks, look for the
        <think>...</think> block, and then display the rest.
        """
        # Yield partial chunks; append a newline to encourage flushing in some servers
        for chunk in stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
                    # small separator to help flush buffers in some WSGI/proxy setups
                    yield ""

    # Note: We use 'text/plain' because the front-end code manually reads
    # the raw chunks, not SSE events.
    # Add headers which reduce proxy buffering in many deployments.
    headers = {
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no'
    }
    return Response(generate(), mimetype='text/plain', headers=headers)

if __name__ == '__main__':
    app.run(debug=True)