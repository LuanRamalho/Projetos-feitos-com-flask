from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
DATA_FILE = 'enquetes.json'

def carregar_dados():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_dados(dados):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    enquetes = carregar_dados()
    return render_template('index.html', enquetes=enquetes)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        pergunta = request.form.get('pergunta')
        opcoes = request.form.get('opcoes').split(',')
        
        dados = carregar_dados()
        # Usamos a própria pergunta como chave, eliminando a necessidade de IDs
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