from flask import Flask, render_template, request, redirect, url_for, Response
from functools import wraps
import json
import os

app = Flask(__name__)

# Configurações de acesso
ADMIN_USER = "admin"
ADMIN_PASS = "12345"
DATA_FILE = 'enquetes.json'

# --- Funções de Segurança (Basic Auth) ---

def check_auth(username, password):
    """Verifica se as credenciais coincidem com o definido"""
    return username == ADMIN_USER and password == ADMIN_PASS

def authenticate():
    """Envia o cabeçalho que solicita o login ao navegador"""
    return Response(
        'Acesso restrito. Por favor, faça login para continuar.', 401,
        {'WWW-Authenticate': 'Basic realm="Login Requerido"'}
    )

def requires_auth(f):
    """Decorator para proteger rotas específicas"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# --- Funções de Dados ---

def carregar_dados():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_dados(dados):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --- Rotas ---

@app.route('/')
def index():
    enquetes = carregar_dados()
    return render_template('index.html', enquetes=enquetes)

@app.route('/admin', methods=['GET', 'POST'])
@requires_auth # Proteção ativada aqui
def admin():
    if request.method == 'POST':
        pergunta = request.form.get('pergunta')
        opcoes = request.form.get('opcoes').split(',')
        
        dados = carregar_dados()
        dados[pergunta] = {opcao.strip(): 0 for opcao in opcoes}
        salvar_dados(dados)
        return redirect(url_for('index'))
    return render_template('admin.html')

@app.route('/votar/<titulo>', methods=['GET', 'POST'])
def votar(titulo):
    dados = carregar_dados()
    enquete = dados.get(titulo)
    
    if request.method == 'POST':
        escolha = request.form.get('opcao')
        if escolha in enquete:
            enquete[escolha] += 1
            salvar_dados(dados)
        return redirect(url_for('resultados', titulo=titulo))
    
    return render_template('votar.html', titulo=titulo, enquete=enquete)

@app.route('/resultados/<titulo>')
def resultados(titulo):
    dados = carregar_dados()
    enquete = dados.get(titulo)
    total_votos = sum(enquete.values())
    
    processado = []
    for opcao, votos in enquete.items():
        porcentagem = (votos / total_votos * 100) if total_votos > 0 else 0
        processado.append({
            'opcao': opcao,
            'votos': votos,
            'porcentagem': round(porcentagem, 2) 
        })
        
    return render_template('resultados.html', titulo=titulo, resultados=processado, total=total_votos)

if __name__ == '__main__':
    app.run(debug=True)
