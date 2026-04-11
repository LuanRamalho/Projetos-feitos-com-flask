from flask import Flask, render_template, request, redirect, url_for
import json
import os
import uuid

app = Flask(__name__)
DB_FILE = 'database.json'

def read_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return []
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    query = request.args.get('busca', '').lower()
    db = read_db()
    if query:
        db = [item for item in db if query in item['fabricante'].lower() or query in item['modelo'].lower()]
    return render_template('index.html', smartphones=db, busca=query)

@app.route('/salvar', methods=['POST'])
def salvar():
    db = read_db()
    item_id = request.form.get('id')
    
    smartphone = {
        "id": item_id if item_id else str(uuid.uuid4()),
        "fabricante": request.form.get('fabricante'),
        "modelo": request.form.get('modelo'),
        "ram": request.form.get('ram'),
        "armazenamento": request.form.get('armazenamento'),
        "bateria": request.form.get('bateria'),
        "velocidade_cpu": request.form.get('velocidade_cpu'), 
        "nucleos": request.form.get('nucleos'),
        "qtd_cameras": request.form.get('qtd_cameras'),
        "megapixels": request.form.get('megapixels'),
        "imagem_url": request.form.get('imagem_url')
    }

    if item_id:
        for i, item in enumerate(db):
            if item['id'] == item_id:
                db[i] = smartphone
                break
    else:
        db.append(smartphone)

    write_db(db)
    return redirect(url_for('index'))

@app.route('/excluir/<item_id>')
def excluir(item_id):
    db = read_db()
    db = [item for item in db if item['id'] != item_id]
    write_db(db)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)