from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

DATA_FILE = 'musicas.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    query = request.args.get('search')
    musicas = load_data()
    
    if query:
        musicas = [m for m in musicas if query.lower() in m['nome'].lower()]
    
    return render_template('index.html', musicas=musicas)

@app.route('/add', methods=['POST'])
def add():
    musicas = load_data()
    nova_musica = {
        "nome": request.form.get('nome'),
        "artista": request.form.get('artista'),
        "album": request.form.get('album'),
        "anotacoes": request.form.get('anotacoes')
    }
    musicas.append(nova_musica)
    save_data(musicas)
    return redirect(url_for('index'))

@app.route('/edit/<int:index>', methods=['POST'])
def edit(index):
    musicas = load_data()
    if 0 <= index < len(musicas):
        musicas[index] = {
            "nome": request.form.get('nome'),
            "artista": request.form.get('artista'),
            "album": request.form.get('album'),
            "anotacoes": request.form.get('anotacoes')
        }
        save_data(musicas)
    return redirect(url_for('index'))

@app.route('/delete/<int:index>')
def delete(index):
    musicas = load_data()
    if 0 <= index < len(musicas):
        musicas.pop(index)
        save_data(musicas)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)