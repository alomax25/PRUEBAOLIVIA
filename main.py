from flask import Flask, request, render_template_string, session
from datetime import timedelta
from markupsafe import Markup
import openai
import re

app = Flask(__name__)
app.secret_key = 'clave-segura'
app.permanent_session_lifetime = timedelta(minutes=1)

openai.api_key = "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"

def responder_con_olivia(mensajes):
    try:
        with open("politica_vacaciones.txt", "r", encoding="utf-8") as f:
            vacaciones = f.read()
        with open("politica_permisos.txt", "r", encoding="utf-8") as f:
            permisos = f.read()
        with open("politica_compras.txt", "r", encoding="utf-8") as f:
            compras = f.read()
        with open("banco_preguntas.txt", "r", encoding="utf-8") as f:
            preguntas = f.read()
        with open("politica_comision.txt", "r", encoding="utf-8") as f:
            comision = f.read()

        system_prompt = f"""
Eres Olivia, una asistente virtual creada por Gabriela y Nicolás para Óptica Los Andes. Tu función es responder de forma clara, natural y confiable todas las preguntas sobre las políticas internas de Desarrollo Organizacional.

💡 Tu estilo es directo, empático y práctico, como si hablaras con una compañera de trabajo. Usa frases cortas, sin tecnicismos ni repeticiones. No des explicaciones innecesarias. Solo responde lo que la persona necesita saber.

🎯 Tu objetivo:
Responder consultas sobre vacaciones, permisos, asistencia, compras internas y comisiones, exclusivamente con base en los documentos oficiales.

🚫 No inventes, no combines políticas y no uses frases condicionales. Si algo no está permitido o no existe, dilo claro y desde el inicio. Si se necesita autorización de jefatura o DO, acláralo de forma transparente.

🗣️ Tono de comunicación:
- Natural, empático y cálido.
- Frases cortas y fáciles de entender.
- Nunca suenes robótica o demasiado formal.
- Siempre cierra con disposición de ayuda, como: “¿Te ayudo con algo más?”

📌 Normas generales para responder:
- Si la solicitud no está contemplada en la política, responde:
  “Esa información no está contemplada en la política actual. Te recomiendo consultarlo con Desarrollo Organizacional.”
- No combines temas de distintas políticas.
- No uses afirmaciones condicionales.
- No te contradigas.
- Confirma siempre con la política antes de responder.

🧩 Estructura sugerida (solo si aplica):
❌ Negación clara al inicio.  
✅ Qué dice la política.  
🔄 Alternativa (si existe).  
🙋‍♀ Cierre empático.

📂 POLÍTICAS OFICIALES

🔴 VACACIONES:
{vacaciones}

🔺 PERMISOS Y ATRASOS:
{permisos}

🟩 COMPRAS DE EMPLEADOS:
{compras}

🟩 COMISIONES:
{comision}

🧠 BANCO DE PREGUNTAS DO:
{preguntas}
"""

        conversation = [{"role": "system", "content": system_prompt}] + mensajes

        respuesta = openai.chat.completions.create(
            model="gpt-3.5 turbo",
            messages=conversation,
            temperature=0.4,
            max_tokens=250  # puedes bajarlo a 250 si quieres aún más brevedad
        )
        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        return f"Ocurrió un error: {str(e)}"

@app.route("/ping")
def ping():
    return "pong", 200

def formatear_respuesta_olivia(texto):
    texto = re.sub(r'(https?://\S+)', r'<a href="\1" target="_blank">\1</a>', texto)
    texto = texto.replace('\n', '<br>')
    return Markup(texto)

@app.route("/", methods=["GET", "POST"])
def chat_web():
    session.permanent = True
    if 'historial' not in session:
        session['historial'] = []

    respuesta_bot = ""
    mensaje_usuario = ""

    if request.method == "POST":
        mensaje_usuario = request.form.get("mensaje", "")
        session['historial'].append({"role": "user", "content": mensaje_usuario})
        respuesta_bot = responder_con_olivia(session['historial'])
        session['historial'].append({"role": "assistant", "content": respuesta_bot})

    historial_html = ""
    for msg in session.get("historial", []):
        if msg["role"] == "user":
            historial_html += Markup(f'<div class="bubble usuario">{msg["content"]}</div>')
        elif msg["role"] == "assistant":
            historial_html += Markup(f'<div class="bubble olivia">{formatear_respuesta_olivia(msg["content"])}</div>')

    return render_template_string("""
<html>
<head>
    <title>Olivia 3.0 - Chat</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #ffffff; margin: 0; padding: 0; height: 100%; overflow: hidden; }
        .chat-box {
            max-width: 400px; height: 100%; max-height: 100%; margin: auto; margin-top: 20px; margin-bottom: 0; padding-bottom: 20px; background: white;
            border-radius: 10px; overflow: hidden; box-shadow: none;
            display: flex; flex-direction: column; position: relative; box-sizing: border-box;
        }
        .header {
            position: sticky; top: 0; background: #ffffff; text-align: center;
            padding: 20px 10px 10px; border-bottom: 1px solid #e0e0e0; z-index: 100;
        }
        .header img { height: 50px; margin-bottom: 10px; }
        .header h2 { margin: 0; color: #00989a; font-size: 20px; }
        .intro {
            color: #333; text-align: center; padding: 10px 20px;
            background: #f7fafa; font-size: 13px; border-bottom: 1px solid #eee;
        }
        .messages {
            flex: 1; overflow-y: auto; padding: 10px; background: #f9f9f9;
        }
        .bubble {
            max-width: 75%; padding: 10px 14px; margin-bottom: 10px;
            border-radius: 12px; font-size: 14px; line-height: 1.4; clear: both;
        }
        .usuario { background: #d1f1e3; color: #00332f; float: right; }
        .olivia { background: #eeeeee; color: #222; float: left; }
        .input-area {
            display: flex; border-top: 1px solid #ddd; background: #fafafa;
            padding: 10px; margin: 0; box-sizing: border-box; position: sticky; bottom: 0; z-index: 100;
        }
        input[type="text"] {
            flex: 1; padding: 10px; border-radius: 20px; border: 1px solid #ccc;
            background: white; color: #333; font-size: 14px; outline: none;
        }
        button {
            margin-left: 10px; padding: 10px 16px; background: #00989a;
            border: none; border-radius: 20px; color: white; cursor: pointer; font-weight: bold;
        }
        html, body {
            margin: 0; padding: 0; height: 100%; overflow: hidden;
        }
    </style>
</head>
<body>
    <div class="chat-box" id="chatBox">
        <div class="header">
            <img src="https://intranet.opticalosandes.com.ec/wp-content/uploads/2022/02/grupo-ola.png" alt="Grupo OLA" style="width: 100px; height: auto;" />
            <h2>OLIVIA 3.0</h2>
        </div>
        <div class="intro">
            “Tu asistente confiable, con información clara, precisa y siempre actualizada. Resuelve tus dudas sobre la política de permisos, vacaciones y control de asistencia del área de Desarrollo Organizacional. ¡Estoy aquí para ayudarte!”
        </div>
        <div class="messages">
            {{ historial_html|safe }}
        </div>
        <form method="post" class="input-area">
            <input type="text" name="mensaje" placeholder="Mensaje" required />
            <button type="submit">Enviar</button>
        </form>
    </div>
</body>
</html>
""", historial_html=historial_html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
