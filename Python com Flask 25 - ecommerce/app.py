from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = 'produtos.json'

def carregar_produtos():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_produtos(produtos):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(produtos, f, indent=4)

@app.route('/')
def index():
    produtos = carregar_produtos()
    return render_template('index.html', produtos=produtos)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        novo_produto = {
            "id": len(carregar_produtos()) + 1,
            "nome": request.form.get('nome'),
            "descricao": request.form.get('descricao'),
            "preco": float(request.form.get('preco')),
            "url_imagem": request.form.get('url_imagem')
        }
        produtos = carregar_produtos()
        produtos.append(novo_produto)
        salvar_produtos(produtos)
        return redirect(url_for('index'))
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)