from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

DATA_FILE = 'data.json'

# Função para garantir que o JSON exista com dados iniciais
def load_data():
    if not os.path.exists(DATA_FILE):
        # Dados iniciais para o seu portfólio
        initial_data = {
            "perfil": {
                "nome": "Luan Ramalho",
                "cargo": "Full Stack Developer",
                "bio": "Desenvolvedor focado em Python, C# e arquiteturas NoSQL.",
                "redes_sociais": [
                    {"nome": "GitHub", "url": "#"},
                    {"nome": "LinkedIn", "url": "#"},
                    {"nome": "Telegram", "url": "#"}
                ]
            },
            "habilidades": ["Python", "Flask", "C#", "Javascript", "HTML/CSS"],
            "projetos": [
                {
                    "titulo": "Projeto Inicial",
                    "descricao": "Este é um projeto de exemplo carregado do JSON.",
                    "link": "#"
                }
            ]
        }
        # Cria o arquivo JSON fisicamente na pasta
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=4, ensure_ascii=False)
        return initial_data
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/')
def index():
    data = load_data()
    return render_template('index.html', data=data)

@app.route('/contato', methods=['POST'])
def contato():
    nome = request.form.get('nome')
    print(f"Contato recebido de: {nome}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)