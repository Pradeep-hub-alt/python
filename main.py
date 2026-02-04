import os
import uuid
from flask import Flask, request, send_file
import google.generativeai as genai
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("api")
if not API_KEY:
    raise RuntimeError("Gemini key is empty")

genai.configure(api_key=API_KEY)

app = Flask(__name__)

# ---------------------------
# GET → Show text input form
# ---------------------------
@app.route("/", methods=["GET"])
def text_form():
    return """
    <html>
    <head>
        <title>Text to Audio</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea, #764ba2);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0;
            }

            .card {
                background: white;
                padding: 30px;
                border-radius: 12px;
                width: 420px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                text-align: center;
            }

            h2 {
                margin-bottom: 20px;
                color: #333;
            }

            textarea {
                width: 100%;
                height: 120px;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #ccc;
                font-size: 14px;
                resize: none;
            }

            input[type="submit"] {
                margin-top: 20px;
                padding: 12px 25px;
                font-size: 15px;
                border: none;
                border-radius: 25px;
                background: #667eea;
                color: white;
                cursor: pointer;
                transition: background 0.3s ease;
            }

            input[type="submit"]:hover {
                background: #5a67d8;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>TEXT → AUDIO</h2>
            <form action="/result" method="post">
                <textarea name="text" required placeholder="Enter your text here..."></textarea>
                <input type="submit" value="Generate Audio">
            </form>
        </div>
    </body>
    </html>
    """

# ---------------------------
# POST → Process text
# ---------------------------
@app.route("/result", methods=["POST"])
def result():
    text = request.form.get("text")

    model = genai.GenerativeModel("gemini-flash-latest")
    response = model.generate_content(text)
    generated_text = response.text

    filename = f"{uuid.uuid4().hex}.mp3"
    tts = gTTS(generated_text, lang="en")
    tts.save(filename)

    return f"""
    <html>
    <head>
        <title>Result</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea, #764ba2);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0;
            }}

            .card {{
                background: white;
                padding: 30px;
                border-radius: 12px;
                width: 500px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}

            h2 {{
                color: #333;
            }}

            p {{
                background: #f7f7f7;
                padding: 15px;
                border-radius: 8px;
                font-size: 14px;
                line-height: 1.6;
            }}

            audio {{
                width: 100%;
                margin-top: 15px;
            }}

            a {{
                display: inline-block;
                margin-top: 20px;
                text-decoration: none;
                color: #667eea;
                font-weight: bold;
            }}

            a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Generated Text</h2>
            <p>{generated_text}</p>

            <h2>Audio Output</h2>
            <audio controls>
                <source src="/audio/{filename}" type="audio/mpeg">
            </audio>

            <br>
            <a href="/">← Back</a>
        </div>
    </body>
    </html>
    """

# ---------------------------
# Serve audio file
# ---------------------------
@app.route("/audio/<filename>")
def serve_audio(filename):
    return send_file(filename, mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(debug=True)
