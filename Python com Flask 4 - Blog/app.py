from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'database.json'

# Inicializa o arquivo JSON se não existir
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

def read_db():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_db(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    posts = read_db()
    # Ordenar posts pelo mais recente
    posts.reverse()
    return render_template('index.html', posts=posts)

@app.route('/add', methods=['POST'])
def add():
    content = request.form.get('content')
    if content:
        posts = read_db()
        new_post = {
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "content": content
        }
        posts.append(new_post)
        write_db(posts)
    return redirect(url_for('index'))

@app.route('/delete/<int:post_index>')
def delete(post_index):
    posts = read_db()
    # Como revertemos a lista no index, precisamos tratar o índice corretamente ou usar ID
    # Para simplificar neste CRUD NoSQL sem ID, usamos a ordem original
    posts.reverse() # Reverte para alinhar com a visualização
    if 0 <= post_index < len(posts):
        posts.pop(post_index)
    posts.reverse() # Reverte de volta para salvar
    write_db(posts)
    return redirect(url_for('index'))

@app.route('/edit/<int:post_index>', methods=['POST'])
def edit(post_index):
    new_content = request.form.get('content')
    posts = read_db()
    posts.reverse()
    if 0 <= post_index < len(posts):
        posts[post_index]['content'] = new_content
        posts[post_index]['timestamp'] = f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} (editado)"
    posts.reverse()
    write_db(posts)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)