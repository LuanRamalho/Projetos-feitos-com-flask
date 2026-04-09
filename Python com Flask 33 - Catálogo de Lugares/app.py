from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
DATA_FILE = 'dados.json'

def carregar_dados():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_dados(dados):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --- ROTAS DA PÁGINA PRINCIPAL (Cidades) ---

@app.route('/')
def index():
    busca = request.args.get('busca', '').lower()
    cidades = carregar_dados()
    
    if busca:
        cidades = [c for c in cidades if busca in c['cidade'].lower() or busca in c['pais'].lower()]
        
    return render_template('index.html', cidades=cidades, busca=busca)

@app.route('/adicionar_cidade', methods=['POST'])
def adicionar_cidade():
    nome = request.form.get('cidade')
    pais = request.form.get('pais')
    dados = carregar_dados()
    
    if nome and pais:
        dados.append({'cidade': nome, 'pais': pais, 'pontos': []})
        salvar_dados(dados)
    return redirect(url_for('index'))

@app.route('/editar_cidade/<nome_antigo>', methods=['POST'])
def editar_cidade(nome_antigo):
    novo_nome = request.form.get('cidade')
    novo_pais = request.form.get('pais')
    dados = carregar_dados()
    
    for c in dados:
        if c['cidade'] == nome_antigo:
            c['cidade'] = novo_nome
            c['pais'] = novo_pais
            break
    salvar_dados(dados)
    return redirect(url_for('index'))

@app.route('/excluir_cidade/<nome>')
def excluir_cidade(nome):
    dados = carregar_dados()
    dados = [c for c in dados if c['cidade'] != nome]
    salvar_dados(dados)
    return redirect(url_for('index'))

# --- ROTAS DA SEGUNDA PÁGINA (Pontos Turísticos) ---

@app.route('/cidade/<nome_cidade>')
def detalhes(nome_cidade):
    busca = request.args.get('busca', '').lower()
    dados = carregar_dados()
    cidade = next((c for c in dados if c['cidade'] == nome_cidade), None)
    
    if not cidade:
        return "Cidade não encontrada", 404
    
    pontos = cidade['pontos']
    if busca:
        pontos = [p for p in pontos if busca in p['nome'].lower()]
        
    return render_template('detalhes.html', cidade=cidade, pontos=pontos, busca=busca)

@app.route('/cidade/<nome_cidade>/add_ponto', methods=['POST'])
def add_ponto(nome_cidade):
    nome_ponto = request.form.get('ponto')
    status = request.form.get('status')
    dados = carregar_dados()
    
    for c in dados:
        if c['cidade'] == nome_cidade:
            c['pontos'].append({'nome': nome_ponto, 'status': status})
            break
    salvar_dados(dados)
    return redirect(url_for('detalhes', nome_cidade=nome_cidade))

@app.route('/cidade/<nome_cidade>/editar_ponto/<int:idx>', methods=['POST'])
def editar_ponto(nome_cidade, idx):
    novo_nome = request.form.get('ponto')
    novo_status = request.form.get('status')
    dados = carregar_dados()
    
    for c in dados:
        if c['cidade'] == nome_cidade:
            c['pontos'][idx] = {'nome': novo_nome, 'status': novo_status}
            break
    salvar_dados(dados)
    return redirect(url_for('detalhes', nome_cidade=nome_cidade))

@app.route('/cidade/<nome_cidade>/excluir_ponto/<int:idx>')
def excluir_ponto(nome_cidade, idx):
    dados = carregar_dados()
    for c in dados:
        if c['cidade'] == nome_cidade:
            c['pontos'].pop(idx)
            break
    salvar_dados(dados)
    return redirect(url_for('detalhes', nome_cidade=nome_cidade))

if __name__ == '__main__':
    app.run(debug=True)