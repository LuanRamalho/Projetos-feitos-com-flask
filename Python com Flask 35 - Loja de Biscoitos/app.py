from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

DATA_FILE = 'biscoitos.json'

def carregar_dados():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_dados(dados):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form.get('nome')
    fabricante = request.form.get('fabricante')
    quantidade = request.form.get('quantidade')

    biscoitos = carregar_dados()
    biscoitos.append({
        'nome': nome,
        'fabricante': fabricante,
        'quantidade': int(quantidade)
    })
    salvar_dados(biscoitos)
    return redirect(url_for('estoque'))

@app.route('/estoque')
def estoque():
    busca_nome = request.args.get('nome', '').lower()
    busca_fabricante = request.args.get('fabricante', '').lower()
    
    todos = carregar_dados()
    
    # Filtro de busca (CRUD - Read)
    resultado = [
        b for b in todos 
        if busca_nome in b['nome'].lower() and busca_fabricante in b['fabricante'].lower()
    ]
    
    return render_template('estoque.html', biscoitos=resultado)

@app.route('/editar/<nome>/<fabricante>', methods=['GET', 'POST'])
def editar(nome, fabricante):
    biscoitos = carregar_dados()
    # Localiza o biscoito original
    biscoito = next((b for b in biscoitos if b['nome'] == nome and b['fabricante'] == fabricante), None)

    if request.method == 'POST':
        if biscoito:
            # Atualiza os dados com o que veio do formulário
            biscoito['nome'] = request.form.get('nome')
            biscoito['fabricante'] = request.form.get('fabricante')
            biscoito['quantidade'] = int(request.form.get('quantidade'))
            salvar_dados(biscoitos)
        return redirect(url_for('estoque'))

    return render_template('editar.html', biscoito=biscoito)

@app.route('/deletar/<nome>/<fabricante>')
def deletar(nome, fabricante):
    biscoitos = carregar_dados()
    # Filtra mantendo apenas os que NÃO coincidem com o par nome/fabricante
    novos_biscoitos = [b for b in biscoitos if not (b['nome'] == nome and b['fabricante'] == fabricante)]
    salvar_dados(novos_biscoitos)
    return redirect(url_for('estoque'))

if __name__ == '__main__':
    app.run(debug=True)