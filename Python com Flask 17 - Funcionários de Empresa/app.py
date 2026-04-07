from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
DATA_FILE = 'empresa.json'

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
    funcionarios = load_data()
    search_nome = request.args.get('nome', '').lower()
    search_cargo = request.args.get('cargo', '').lower()

    if search_nome:
        funcionarios = [f for f in funcionarios if search_nome in f['Nome'].lower()]
    if search_cargo:
        funcionarios = [f for f in funcionarios if search_cargo in f['Funcao'].lower()]

    return render_template('index.html', funcionarios=funcionarios)

@app.route('/add', methods=['POST'])
def add():
    funcionarios = load_data()
    novo_func = {
        "Nome": request.form['nome'],
        "Funcao": request.form['funcao'],
        "Salario": request.form['salario'],
        "DataAdmissao": request.form['admissao'],
        "DataDemissao": request.form['demissao'] or None
    }
    funcionarios.append(novo_func)
    save_data(funcionarios)
    return redirect(url_for('index'))

@app.route('/delete/<nome>')
def delete(nome):
    funcionarios = load_data()
    funcionarios = [f for f in funcionarios if f['Nome'] != nome]
    save_data(funcionarios)
    return redirect(url_for('index'))

@app.route('/edit/<nome_antigo>', methods=['POST'])
def edit(nome_antigo):
    funcionarios = load_data()
    for f in funcionarios:
        if f['Nome'] == nome_antigo:
            f['Nome'] = request.form['nome']
            f['Funcao'] = request.form['funcao']
            f['Salario'] = request.form['salario']
            f['DataAdmissao'] = request.form['admissao']
            f['DataDemissao'] = request.form['demissao'] or None
            break
    save_data(funcionarios)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)