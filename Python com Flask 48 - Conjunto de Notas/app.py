from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)
DB_FILE = 'database.json'

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
    query = request.args.get('search', '').lower()
    notas = load_db()
    if query:
        notas = [n for n in notas if query in n['titulo'].lower()]
    return render_template('index.html', notas=notas)

@app.route('/add', methods=['POST'])
def add_nota():
    titulo = request.form.get('titulo')
    if titulo:
        db = load_db()
        nova_nota = {
            "id": str(uuid.uuid4()),
            "titulo": titulo,
            "conteudo": "",
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        db.append(nova_nota)
        save_db(db)
    return redirect(url_for('index'))

@app.route('/edit_titulo/<id>', methods=['POST'])
def edit_titulo(id):
    novo_titulo = request.form.get('titulo')
    db = load_db()
    for nota in db:
        if nota['id'] == id:
            nota['titulo'] = novo_titulo
            break
    save_db(db)
    return redirect(url_for('index'))

@app.route('/delete/<id>')
def delete_nota(id):
    db = load_db()
    db = [n for n in db if n['id'] != id]
    save_db(db)
    return redirect(url_for('index'))

@app.route('/nota/<id>')
def visualizar_nota(id):
    db = load_db()
    nota = next((n for n in db if n['id'] == id), None)
    return render_template('nota.html', nota=nota)

@app.route('/save_content/<id>', methods=['POST'])
def save_content(id):
    data = request.get_json()
    db = load_db()
    for nota in db:
        if nota['id'] == id:
            nota['conteudo'] = data['conteudo']
            break
    save_db(db)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)