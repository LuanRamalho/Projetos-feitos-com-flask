import json
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB_FILE = 'database.json'

# Inicializa o banco JSON se não existir
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w') as f:
        json.dump([], f)

def load_data():
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    filmes = load_data()
    busca_nome = request.args.get('nome', '').lower()
    busca_genero = request.args.get('genero', '').lower()

    if busca_nome:
        filmes = [f for f in filmes if busca_nome in f['titulo'].lower()]
    if busca_genero:
        filmes = [f for f in filmes if busca_genero in f['genero'].lower()]

    return render_template('index.html', filmes=filmes)

@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar():
    if request.method == 'POST':
        filmes = load_data()
        novo_filme = {
            'id': len(filmes) + 1,
            'titulo': request.form['titulo'],
            'diretor': request.form['diretor'],
            'genero': request.form['genero'],
            'ano': request.form['ano'],
            'sinopse': request.form['sinopse'],
            'capa': request.form['capa']
        }
        filmes.append(novo_filme)
        save_data(filmes)
        return redirect(url_for('index'))
    return render_template('adicionar.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    filmes = load_data()
    filme = next((f for f in filmes if f['id'] == id), None)

    if request.method == 'POST':
        filme.update({
            'titulo': request.form['titulo'],
            'diretor': request.form['diretor'],
            'genero': request.form['genero'],
            'ano': request.form['ano'],
            'sinopse': request.form['sinopse'],
            'capa': request.form['capa']
        })
        save_data(filmes)
        return redirect(url_for('index'))
    return render_template('editar.html', filme=filme)

@app.route('/deletar/<int:id>')
def deletar(id):
    filmes = load_data()
    filmes = [f for f in filmes if f['id'] != id]
    save_data(filmes)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)