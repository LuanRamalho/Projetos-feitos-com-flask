from flask import Flask, render_template, request, redirect, url_for
import json
import os
import uuid

app = Flask(__name__)

DB_FILE = 'database.json'

# Inicializa o JSON se não existir
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w') as f:
        json.dump([], f)

def load_db():
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    games = load_db()
    return render_template('index.html', games=games)

@app.route('/add', methods=['POST'])
def add_game():
    games = load_db()
    new_game = {
        "id": str(uuid.uuid4()),
        "titulo": request.form.get('titulo'),
        "categoria": request.form.get('categoria'),
        "jogadores": request.form.get('jogadores'),
        "status": "Disponível",
        "emprestado_para": ""
    }
    games.append(new_game)
    save_db(games)
    return redirect(url_for('index'))

@app.route('/edit/<id>', methods=['POST'])
def edit_game(id):
    games = load_db()
    for game in games:
        if game['id'] == id:
            game['titulo'] = request.form.get('titulo')
            game['categoria'] = request.form.get('categoria')
            game['jogadores'] = request.form.get('jogadores')
            break
    save_db(games)
    return redirect(url_for('index'))

@app.route('/loan/<id>', methods=['POST'])
def loan_game(id):
    games = load_db()
    for game in games:
        if game['id'] == id:
            if game['status'] == "Disponível":
                game['status'] = "Emprestado"
                game['emprestado_para'] = request.form.get('pessoa')
            else:
                game['status'] = "Disponível"
                game['emprestado_para'] = ""
            break
    save_db(games)
    return redirect(url_for('index'))

@app.route('/delete/<id>')
def delete_game(id):
    games = load_db()
    games = [g for g in games if g['id'] != id]
    save_db(games)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)