from flask import Flask, render_template, request, redirect
import json
import os

app = Flask(__name__)

DATA_FILE = 'dados.json'

def salvar_no_json(novo_dado):
    # Inicializa a lista de dados
    dados_existentes = []
    
    # Verifica se o arquivo já existe e carrega o conteúdo
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                dados_existentes = json.load(f)
            except json.JSONDecodeError:
                dados_existentes = []

    # Adiciona o novo registro
    dados_existentes.append(novo_dado)

    # Salva de volta no arquivo
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados_existentes, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enviar', methods=['POST'])
def enviar():
    # Coleta dados do formulário
    usuario = {
        "nome": request.form.get('nome'),
        "idade": request.form.get('idade'),
        "email": request.form.get('email'),
        "genero": request.form.get('genero'),
        "hobbies": request.form.get('hobbies')
    }
    
    salvar_no_json(usuario)
    return "Dados salvos com sucesso! <a href='/'>Voltar</a>"

if __name__ == '__main__':
    app.run(debug=True)