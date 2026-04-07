import os
import json
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
DB_FILE = 'database.json'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def load_db():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nome de arquivo vazio"}), 400

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    # Indexação básica
    db = load_db()
    entry = {
        "id": len(db) + 1,
        "nome": file.filename,
        "tamanho": f"{os.path.getsize(path) / 1024:.2f} KB",
        "data_indexacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "extensao": file.filename.split('.')[-1].upper()
    }
    db.append(entry)
    save_db(db)
    
    return jsonify(entry)

@app.route('/delete/<int:doc_id>', methods=['DELETE'])
def delete(doc_id):
    db = load_db()
    # Encontra o documento
    doc = next((d for d in db if d['id'] == doc_id), None)
    
    if doc:
        # Remove o arquivo físico da pasta uploads
        file_path = os.path.join(UPLOAD_FOLDER, doc['nome'])
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Remove do banco de dados JSON
        db = [d for d in db if d['id'] != doc_id]
        save_db(db)
        return jsonify({"success": True})
    
    return jsonify({"error": "Documento não encontrado"}), 404

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    db = load_db()
    results = [doc for doc in db if query in doc['nome'].lower()]
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)