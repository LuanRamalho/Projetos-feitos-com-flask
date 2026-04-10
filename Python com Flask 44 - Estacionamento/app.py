# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Configuração do banco de dados JSON
app.config['DB_FILE'] = 'database.json'

def load_db():
    # Corrigido para usar app.config
    if not os.path.exists(app.config['DB_FILE']):
        with open(app.config['DB_FILE'], 'w', encoding='utf-8') as f:
            json.dump({"clientes": []}, f, ensure_ascii=False, indent=4)
    
    with open(app.config['DB_FILE'], 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data):
    # Corrigido de DATA_FILE para app.config['DB_FILE']
    with open(app.config['DB_FILE'], 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    return render_template('index.html')

# --- CRUD CLIENTES ---
@app.route('/api/clientes', methods=['GET', 'POST'])
def api_clientes():
    db = load_db()
    if request.method == 'POST':
        novo_cliente = {
            "id": str(datetime.now().timestamp()),
            "nome": request.json['nome'],
            "registros": []
        }
        db['clientes'].append(novo_cliente)
        save_db(db) # Agora salva corretamente
        return jsonify(novo_cliente)
    return jsonify(db['clientes'])

@app.route('/api/clientes/<id>', methods=['PUT', 'DELETE'])
def api_cliente_detail(id):
    db = load_db()
    if request.method == 'DELETE':
        db['clientes'] = [c for c in db['clientes'] if c['id'] != id]
        save_db(db)
        return jsonify({"status": "ok"})
    
    elif request.method == 'PUT':
        for c in db['clientes']:
            if c['id'] == id:
                c['nome'] = request.json['nome']
                break
        save_db(db)
        return jsonify({"status": "ok"})
    
    return "NotFound", 404

# --- SEGUNDA PÁGINA (DETALHES) ---
@app.route('/cliente/<id>')
def detalhes_cliente(id):
    return render_template('detalhes.html', cliente_id=id)

@app.route('/api/estacionamento/<cliente_id>', methods=['GET', 'POST'])
def api_estacionamento(cliente_id):
    db = load_db()
    # Busca o cliente específico no banco
    cliente = next((c for c in db['clientes'] if c['id'] == cliente_id), None)
    
    if not cliente:
        return jsonify({"error": "Cliente não encontrado"}), 404

    if request.method == 'POST':
        data = request.json
        # Cálculo do total conforme solicitado
        valor_un = float(data['valor_unidade'])
        qtd_horas = float(data['horas'])
        
        novo_registro = {
            "reg_id": str(datetime.now().timestamp()),
            "tipo": data['tipo'],
            "valor_unidade": valor_un,
            "data_hora": data['data_hora'],
            "horas": qtd_horas,
            "total": valor_un * qtd_horas
        }
        cliente['registros'].append(novo_registro)
        save_db(db) # Salva a lista de registros atualizada
        return jsonify(novo_registro)
    
    return jsonify(cliente)

@app.route('/api/estacionamento/<cliente_id>/<reg_id>', methods=['PUT', 'DELETE'])
def api_reg_detail(cliente_id, reg_id):
    db = load_db()
    cliente = next((c for c in db['clientes'] if c['id'] == cliente_id), None)
    
    if not cliente: return "NotFound", 404

    if request.method == 'DELETE':
        cliente['registros'] = [r for r in cliente['registros'] if r['reg_id'] != reg_id]
    
    elif request.method == 'PUT':
        data = request.json
        for r in cliente['registros']:
            if r['reg_id'] == reg_id:
                r.update({
                    "tipo": data['tipo'],
                    "valor_unidade": float(data['valor_unidade']),
                    "data_hora": data['data_hora'],
                    "horas": float(data['horas']),
                    "total": float(data['valor_unidade']) * float(data['horas'])
                })
                break
                
    save_db(db)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True)