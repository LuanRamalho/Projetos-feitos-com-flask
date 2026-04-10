from flask import Flask, render_template, request, jsonify
import json
import os
import uuid

app = Flask(__name__)
DATA_FILE = 'bolos.json'

# Função para ler os dados do banco JSON
def ler_dados():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Função para salvar os dados no banco JSON
def salvar_dados(dados):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    return render_template('index.html')

# --- Rotas CRUD (API) ---

# READ (Buscar todos)
@app.route('/api/bolos', methods=['GET'])
def obter_bolos():
    return jsonify(ler_dados())

# CREATE (Criar novo bolo)
@app.route('/api/bolos', methods=['POST'])
def adicionar_bolo():
    dados = request.json
    dados['id'] = uuid.uuid4().hex # Gera um ID único
    bolos = ler_dados()
    bolos.append(dados)
    salvar_dados(bolos)
    return jsonify({'success': True, 'bolo': dados})

# UPDATE (Atualizar bolo existente)
@app.route('/api/bolos/<bolo_id>', methods=['PUT'])
def atualizar_bolo(bolo_id):
    dados_atualizados = request.json
    bolos = ler_dados()
    for bolo in bolos:
        if bolo['id'] == bolo_id:
            bolo['nome'] = dados_atualizados.get('nome', bolo['nome'])
            bolo['tipo'] = dados_atualizados.get('tipo', bolo['tipo'])
            bolo['descricao'] = dados_atualizados.get('descricao', bolo['descricao'])
            bolo['link'] = dados_atualizados.get('link', bolo['link'])
            bolo['preco'] = dados_atualizados.get('preco', bolo['preco'])
            break
    salvar_dados(bolos)
    return jsonify({'success': True})

# DELETE (Excluir bolo)
@app.route('/api/bolos/<bolo_id>', methods=['DELETE'])
def excluir_bolo(bolo_id):
    bolos = ler_dados()
    bolos = [b for b in bolos if b['id'] != bolo_id]
    salvar_dados(bolos)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)