from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
DATA_FILE = 'data.json'

# Inicializa o arquivo JSON se não existir
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

def read_db():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def write_db(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    registros = read_db()
    for reg in registros:
        # Cálculo do saldo individual
        reg['saldo'] = round(reg['gerado'] - reg['consumido'], 2)
    return render_template('index.html', registros=registros)

@app.route('/add', methods=['POST'])
def add():
    gerado = float(request.form.get('gerado'))
    consumido = float(request.form.get('consumido'))
    data = request.form.get('data')
    
    db = read_db()
    novo_registro = {
        "id": len(db) + 1,
        "gerado": gerado,
        "consumido": consumido,
        "data": data
    }
    db.append(novo_registro)
    write_db(db)
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    db = read_db()
    registro = next((r for r in db if r['id'] == id), None)
    
    if request.method == 'POST':
        registro['gerado'] = float(request.form.get('gerado'))
        registro['consumido'] = float(request.form.get('consumido'))
        registro['data'] = request.form.get('data')
        write_db(db)
        return redirect(url_for('index'))
    
    return render_template('edit.html', reg=registro)

@app.route('/delete/<int:id>')
def delete(id):
    db = read_db()
    db = [r for r in db if r['id'] != id]
    write_db(db)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)