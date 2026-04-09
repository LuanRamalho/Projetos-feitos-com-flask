from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime
from collections import Counter

app = Flask(__name__)
DATA_FILE = 'sonhos.json'

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
    sonhos = carregar_dados()
    
    # Filtros de busca
    busca_nome = request.args.get('nome', '').lower()
    busca_cat = request.args.get('categoria', '').lower()
    
    if busca_nome:
        sonhos = [s for s in sonhos if busca_nome in s['titulo'].lower()]
    if busca_cat:
        sonhos = [s for s in sonhos if busca_cat in s['categoria'].lower()]

    # Estatísticas
    categorias = [s['categoria'] for s in sonhos]
    stats = Counter(categorias).most_common(3)
    
    return render_template('index.html', sonhos=sonhos, stats=stats)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    dados = carregar_dados()
    novo_sonho = {
        "titulo": request.form['titulo'],
        "data": request.form['data'], # Formato esperado DD/MM/YYYY
        "categoria": request.form['categoria'],
        "descricao": request.form['descricao']
    }
    dados.append(novo_sonho)
    salvar_dados(dados)
    return redirect(url_for('index'))

@app.route('/editar/<titulo_original>', methods=['GET', 'POST'])
def editar(titulo_original):
    dados = carregar_dados()
    sonho = next((s for s in dados if s['titulo'] == titulo_original), None)
    
    if request.method == 'POST':
        for s in dados:
            if s['titulo'] == titulo_original:
                s['titulo'] = request.form['titulo']
                s['data'] = request.form['data']
                s['categoria'] = request.form['categoria']
                s['descricao'] = request.form['descricao']
                break
        salvar_dados(dados)
        return redirect(url_for('index'))
    
    return render_template('editar.html', sonho=sonho)

@app.route('/excluir/<titulo>')
def excluir(titulo):
    dados = carregar_dados()
    dados = [s for s in dados if s['titulo'] != titulo]
    salvar_dados(dados)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)