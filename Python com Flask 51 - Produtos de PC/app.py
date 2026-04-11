import json
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DB_FILE = 'db.json'

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump({"pcs": [], "produtos": []}, f, indent=4)
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    return render_template('index.html')

# --- Rotas para PCs ---
@app.route('/api/pcs', methods=['GET', 'POST'])
def manage_pcs():
    db = load_db()
    if request.method == 'GET':
        return jsonify(db['pcs'])
    
    if request.method == 'POST':
        novo_pc = request.json
        db['pcs'].append(novo_pc)
        save_db(db)
        return jsonify({"message": "PC adicionado com sucesso!"}), 201

@app.route('/api/pcs/update', methods=['PUT'])
def update_pc():
    db = load_db()
    data = request.json
    old_fabricante = data.get('old_fabricante')
    old_modelo = data.get('old_modelo')
    new_data = data.get('new_data')

    for i, pc in enumerate(db['pcs']):
        if pc['fabricante'] == old_fabricante and pc['modelo'] == old_modelo:
            db['pcs'][i] = new_data
            save_db(db)
            return jsonify({"message": "PC atualizado!"}), 200
    return jsonify({"error": "PC não encontrado"}), 404

@app.route('/api/pcs/delete', methods=['DELETE'])
def delete_pc():
    db = load_db()
    fabricante = request.json.get('fabricante')
    modelo = request.json.get('modelo')
    
    db['pcs'] = [pc for pc in db['pcs'] if not (pc['fabricante'] == fabricante and pc['modelo'] == modelo)]
    save_db(db)
    return jsonify({"message": "PC removido!"}), 200

# --- Rotas para Produtos ---
@app.route('/api/produtos', methods=['GET', 'POST'])
def manage_produtos():
    db = load_db()
    if request.method == 'GET':
        return jsonify(db['produtos'])
    
    if request.method == 'POST':
        novo_produto = request.json
        db['produtos'].append(novo_produto)
        save_db(db)
        return jsonify({"message": "Produto adicionado com sucesso!"}), 201

@app.route('/api/produtos/update', methods=['PUT'])
def update_produto():
    db = load_db()
    data = request.json
    old_nome = data.get('old_nome')
    old_fabricante = data.get('old_fabricante')
    new_data = data.get('new_data')

    for i, prod in enumerate(db['produtos']):
        if prod['nome'] == old_nome and prod['fabricante'] == old_fabricante:
            db['produtos'][i] = new_data
            save_db(db)
            return jsonify({"message": "Produto atualizado!"}), 200
    return jsonify({"error": "Produto não encontrado"}), 404

@app.route('/api/produtos/delete', methods=['DELETE'])
def delete_produto():
    db = load_db()
    nome = request.json.get('nome')
    fabricante = request.json.get('fabricante')
    
    db['produtos'] = [p for p in db['produtos'] if not (p['nome'] == nome and p['fabricante'] == fabricante)]
    save_db(db)
    return jsonify({"message": "Produto removido!"}), 200

if __name__ == '__main__':
    app.run(debug=True)