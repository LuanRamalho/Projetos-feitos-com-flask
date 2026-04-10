from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
import math

app = Flask(__name__)
app.secret_key = "secret_comics"
DATA_FILE = 'gibis.json'

def carregar_dados():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_dados(gibis):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(gibis, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    todos_gibis = carregar_dados()
    
    # Filtros de Busca
    busca_nome = request.args.get('nome', '').lower()
    busca_editora = request.args.get('editora', '').lower()
    
    # Aplicar Filtros
    gibis_filtrados = [
        g for g in todos_gibis 
        if busca_nome in g['titulo'].lower() and busca_editora in g['editora'].lower()
    ]

    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total = len(gibis_filtrados) # Este é o contador que você quer
    total_pages = math.ceil(total / per_page)
    
    start = (page - 1) * per_page
    end = start + per_page
    gibis_paginados = gibis_filtrados[start:end]

    # Enviando 'total_items' para o HTML
    return render_template('index.html', 
                           gibis=gibis_paginados, 
                           page=page, 
                           total_pages=total_pages,
                           total_items=total,  # <-- Garanta que esta linha existe
                           busca_nome=busca_nome,
                           busca_editora=busca_editora)

@app.route('/add', methods=['POST'])
def add():
    gibis = carregar_dados()
    novo_gibi = {
        "titulo": request.form.get('titulo'),
        "volume": request.form.get('volume'),
        "edicao": request.form.get('edicao'),
        "paginas": request.form.get('paginas'),
        "editora": request.form.get('editora')
    }
    gibis.append(novo_gibi)
    salvar_dados(gibis)
    flash("Gibi adicionado com sucesso!")
    return redirect(url_for('index'))

@app.route('/edit/<int:index_id>', methods=['POST'])
def edit(index_id):
    gibis = carregar_dados()
    # No JSON, o ID é a posição na lista
    gibis[index_id] = {
        "titulo": request.form.get('titulo'),
        "volume": request.form.get('volume'),
        "edicao": request.form.get('edicao'),
        "paginas": request.form.get('paginas'),
        "editora": request.form.get('editora')
    }
    salvar_dados(gibis)
    return redirect(url_for('index'))

@app.route('/delete/<int:index_id>')
def delete(index_id):
    gibis = carregar_dados()
    if 0 <= index_id < len(gibis):
        gibis.pop(index_id)
        salvar_dados(gibis)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)