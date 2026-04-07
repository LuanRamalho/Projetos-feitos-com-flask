from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# Nome do arquivo conforme fornecido
DATA_FILE = 'economic_data.json'

def get_db():
    """Lê o arquivo JSON com suporte a caracteres portugueses."""
    try:
        # 'utf-8' garante que acentos e caracteres especiais sejam lidos corretamente
        with open(DATA_FILE, 'r', encoding='utf-8') as f: 
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_db(data):
    """Salva os dados no JSON mantendo a codificação legível."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        # ensure_ascii=False impede que o Python converta caracteres como 'ç' em códigos Unicode
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    return render_template('index.html')

# --- API Endpoints ---

@app.route('/api/data', methods=['GET'])
def read_data():
    return jsonify(get_db())

@app.route('/api/data', methods=['POST'])
def create_or_update():
    req_data = request.json
    year = str(req_data.get('year'))
    values = req_data.get('values') # Espera uma lista de 12 valores
    
    if not year or not values:
        return jsonify({"status": "error", "message": "Dados incompletos"}), 400

    db = get_db()
    db[year] = [float(v) for v in values]
    save_db(db)
    return jsonify({"status": "success", "message": f"Dados de {year} salvos com sucesso."})

@app.route('/api/data/<year>', methods=['DELETE'])
def delete_data(year):
    db = get_db()
    if year in db:
        del db[year]
        save_db(db)
        return jsonify({"status": "success", "message": f"O ano {year} foi removido."})
    return jsonify({"status": "error", "message": "Ano não encontrado."}), 404

if __name__ == '__main__':
    # O Flask rodará no ambiente local para desenvolvimento
    app.run(debug=True)