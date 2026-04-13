from flask import Flask, render_template, request, redirect, url_for, Response
from functools import wraps
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

# --- SISTEMA DE LOGIN MINIMALISTA ---
def check_auth(username, password):
    # Defina aqui o seu usuário e senha
    return username == 'admin' and password == '12345'

def authenticate():
    # Retorna o aviso para o navegador abrir a caixa de login nativa
    return Response(
    'Acesso negado. Credenciais incorretas.\n', 401,
    {'WWW-Authenticate': 'Basic realm="Acesso Restrito ao Painel Admin"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
# ------------------------------------

@app.route('/')
def index():
    produtos = carregar_produtos()
    return render_template('index.html', produtos=produtos)

# O decorador @requires_auth foi adicionado aqui para proteger a rota
@app.route('/admin', methods=['GET', 'POST'])
@requires_auth
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
