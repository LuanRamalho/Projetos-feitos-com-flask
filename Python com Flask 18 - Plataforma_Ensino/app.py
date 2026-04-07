from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)
DB_FILE = 'db.json'

# --- Funções Auxiliares do Banco de Dados ---
def load_db():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- Rotas da Aplicação ---

@app.route('/')
def index():
    tutorials = load_db()
    return render_template('index.html', tutorials=tutorials)

@app.route('/tutorial/<int:id>')
def view_tutorial(id):
    db = load_db()
    tutorial = next((t for t in db if t['id'] == id), None)
    return render_template('tutorial.html', tutorial=tutorial)

@app.route('/check_answer/<int:id>/<int:pergunta_idx>', methods=['POST'])
def check_specific_answer(id, pergunta_idx):
    db = load_db()
    tutorial = next((t for t in db if t['id'] == id), None)
    user_answer = request.form.get('answer').strip().lower()
    
    # Valida a resposta específica na lista
    correct = tutorial['resposta_correta'][pergunta_idx].lower()
    if user_answer == correct:
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

# --- CRUD Administrativo ---

@app.route('/admin')
def admin():
    tutorials = load_db()
    return render_template('admin.html', tutorials=tutorials)

@app.route('/admin/add', methods=['POST'])
def add_tutorial():
    db = load_db()
    new_id = max([t['id'] for t in db], default=0) + 1
    new_tutorial = {
        "id": new_id,
        "titulo": request.form.get('titulo'),
        "descricao": request.form.get('descricao'),
        "conteudo": request.form.get('conteudo'),
        "pergunta_quiz": request.form.get('pergunta_quiz'),
        "resposta_correta": request.form.get('resposta_correta'),
        "cor": request.form.get('cor', '#FF6584')
    }
    db.append(new_tutorial)
    save_db(db)
    return redirect(url_for('admin'))

@app.route('/admin/edit/<int:id>')
def edit_page(id):
    db = load_db()
    tutorial = next((t for t in db if t['id'] == id), None)
    if tutorial:
        return render_template('edit.html', tutorial=tutorial)
    return redirect(url_for('admin'))

@app.route('/admin/update/<int:id>', methods=['POST'])
def update_tutorial(id):
    db = load_db()
    for t in db:
        if t['id'] == id:
            t['titulo'] = request.form.get('titulo')
            t['descricao'] = request.form.get('descricao')
            t['conteudo'] = request.form.get('conteudo')
            t['pergunta_quiz'] = request.form.get('pergunta_quiz')
            t['resposta_correta'] = request.form.get('resposta_correta')
            t['cor'] = request.form.get('cor')
            break
    save_db(db)
    return redirect(url_for('admin'))

@app.route('/admin/delete/<int:id>')
def delete_tutorial(id):
    db = load_db()
    db = [t for t in db if t['id'] != id]
    save_db(db)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)