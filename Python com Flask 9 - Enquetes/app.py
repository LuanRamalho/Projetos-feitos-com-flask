from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import locale

# Configura o Python para usar o padrão brasileiro (ponto para milhar)
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, '') # Fallback caso o sistema não tenha o locale instalado

app = Flask(__name__)
app.secret_key = 'projeto_enquetes_key'

ADMIN_USER = "admin"
ADMIN_PASS = "12345"
DATA_FILE = 'enquetes.json'

# --- Funções de Dados ---
def carregar_dados():
    if not os.path.exists(DATA_FILE): return {}
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
def admin():
    if not session.get('logado'):
        return "Acesso Negado", 403
    if request.method == 'POST':
        pergunta = request.form.get('pergunta')
        opcoes = request.form.get('opcoes').split(',')
        dados = carregar_dados()
        dados[pergunta] = {opcao.strip(): 0 for opcao in opcoes}
        salvar_dados(dados)
        return redirect(url_for('index'))
    return render_template('admin.html')

@app.route('/login_admin_prompt')
def login_admin_prompt():
    if request.args.get('u') == ADMIN_USER and request.args.get('p') == ADMIN_PASS:
        session['logado'] = True
        return redirect(url_for('admin'))
    return "Acesso Negado", 401

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
    if not enquete: return redirect(url_for('index'))
        
    total_votos = sum(enquete.values())
    processado = []

    for opcao, votos in enquete.items():
        porcentagem = (votos / total_votos * 100) if total_votos > 0 else 0
        processado.append({
            'opcao': opcao,
            'votos_formatados': f"{votos:n}", # Formata com pontos (ex: 5.748.237)
            'porcentagem': round(porcentagem, 2) 
        })
        
    return render_template('resultados.html', 
                           titulo=titulo, 
                           resultados=processado, 
                           total=f"{total_votos:n}") # Total também formatado

if __name__ == '__main__':
    app.run(debug=True)
