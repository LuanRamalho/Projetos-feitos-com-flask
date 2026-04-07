from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'feedbacks.json'

# Inicializa o arquivo JSON se não existir
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

def save_feedback(content):
    with open(DATA_FILE, 'r+', encoding='utf-8') as f:
        data = json.load(f)
        new_entry = {
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "mensagem": content,
            "status": "pendente"
        }
        data.append(new_entry)
        f.seek(0)
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enviar', methods=['POST'])
def enviar():
    feedback_text = request.form.get('feedback')
    if feedback_text:
        save_feedback(feedback_text)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)