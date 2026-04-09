from flask import Flask, render_template, request, redirect, url_for
import json
import os
import math

app = Flask(__name__)
DB_FILE = 'livros.json'

def carregar_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def salvar_db(dados):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    livros = carregar_db()
    busca = request.args.get('busca', '').strip().lower()
    
    if busca:
        # Filtra os livros onde o termo de busca está contido no título
        livros = {k: v for k, v in livros.items() if busca in v['titulo'].lower()}
        
    return render_template('index.html', livros=livros, busca=busca)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    titulo = request.form.get('titulo').strip()
    if titulo:
        db = carregar_db()
        if titulo not in db:
            db[titulo] = {
                "titulo": titulo,
                "total_paginas": 0,
                "paginas_lidas": 0,
                "ritmo_diario": 10 # Meta padrão de páginas por dia
            }
            salvar_db(db)
    return redirect(url_for('index'))

@app.route('/editar_index/<titulo_antigo>', methods=['POST'])
def editar_index(titulo_antigo):
    novo_titulo = request.form.get('novo_titulo').strip()
    db = carregar_db()
    if titulo_antigo in db and novo_titulo and novo_titulo != titulo_antigo:
        dados = db.pop(titulo_antigo)
        dados['titulo'] = novo_titulo
        db[novo_titulo] = dados
        salvar_db(db)
    return redirect(url_for('index'))

@app.route('/excluir/<titulo>', methods=['POST'])
def excluir(titulo):
    db = carregar_db()
    if titulo in db:
        del db[titulo]
        salvar_db(db)
    # Redireciona para onde a requisição veio (index ou livro)
    return redirect(url_for('index'))

@app.route('/livro/<titulo>', methods=['GET', 'POST'])
def visualizar_livro(titulo):
    db = carregar_db()
    if titulo not in db:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        # Atualização completa dos dados do livro
        novo_titulo = request.form.get('titulo').strip()
        total_paginas = int(request.form.get('total_paginas', 0))
        paginas_lidas = int(request.form.get('paginas_lidas', 0))
        ritmo_diario = int(request.form.get('ritmo_diario', 1))
        
        dados = db.pop(titulo) # Remove a chave antiga (útil caso o título mude)
        dados['titulo'] = novo_titulo if novo_titulo else titulo
        dados['total_paginas'] = total_paginas
        dados['paginas_lidas'] = paginas_lidas
        dados['ritmo_diario'] = ritmo_diario if ritmo_diario > 0 else 1
        
        db[dados['titulo']] = dados
        salvar_db(db)
        return redirect(url_for('visualizar_livro', titulo=dados['titulo']))

    livro = db[titulo]
    
    # Cálculos do Simulador
    total = livro.get('total_paginas', 0)
    lidas = livro.get('paginas_lidas', 0)
    ritmo = livro.get('ritmo_diario', 10)
    
    porcentagem = (lidas / total * 100) if total > 0 else 0
    porcentagem = round(porcentagem, 1)
    
    faltam = total - lidas
    dias_restantes = math.ceil(faltam / ritmo) if faltam > 0 else 0

    return render_template('livro.html', livro=livro, porcentagem=porcentagem, faltam=faltam, dias_restantes=dias_restantes)

if __name__ == '__main__':
    app.run(debug=True)