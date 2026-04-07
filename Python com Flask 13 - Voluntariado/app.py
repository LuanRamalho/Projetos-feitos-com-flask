from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'data.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"projetos": []}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def format_date_br(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d/%m/%Y')
    except:
        return date_str

@app.route('/')
def index():
    search = request.args.get('search', '')
    data = load_data()
    projetos = data['projetos']
    
    if search:
        projetos = [p for p in projetos if search.lower() in p['nome'].lower()]
        
    return render_template('index.html', projetos=projetos, search=search)

@app.route('/add', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        data = load_data()
        novo_projeto = {
            "id": len(data['projetos']) + 1 if data['projetos'] else 1,
            "nome": request.form['nome'],
            "descricao": request.form['descricao'],
            "data_inicio": request.form['data_inicio'],
            "data_fim": request.form['data_fim'],
            "status": request.form['status'],
            "voluntarios": ""
        }
        data['projetos'].append(novo_projeto)
        save_data(data)
        return redirect(url_for('index'))
    return render_template('form.html', action="Adicionar", projeto={})

@app.route('/view/<int:id>')
def view_project(id):
    data = load_data()
    projeto = next((p for p in data['projetos'] if p['id'] == id), None)
    if projeto:
        projeto_formatado = projeto.copy()
        projeto_formatado['data_inicio'] = format_date_br(projeto['data_inicio'])
        projeto_formatado['data_fim'] = format_date_br(projeto['data_fim'])
        return render_template('view.html', projeto=projeto_formatado)
    return "Projeto não encontrado", 404

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_project(id):
    data = load_data()
    projeto = next((p for p in data['projetos'] if p['id'] == id), None)
    
    if request.method == 'POST':
        projeto['nome'] = request.form['nome']
        projeto['descricao'] = request.form['descricao']
        projeto['data_inicio'] = request.form['data_inicio']
        projeto['data_fim'] = request.form['data_fim']
        projeto['status'] = request.form['status']
        save_data(data)
        return redirect(url_for('index'))
    
    return render_template('form.html', action="Editar", projeto=projeto)

@app.route('/delete/<int:id>')
def delete_project(id):
    data = load_data()
    data['projetos'] = [p for p in data['projetos'] if p['id'] != id]
    save_data(data)
    return redirect(url_for('index'))

@app.route('/volunteers/<int:id>', methods=['GET', 'POST'])
def add_volunteers(id):
    data = load_data()
    projeto = next((p for p in data['projetos'] if p['id'] == id), None)
    
    if request.method == 'POST':
        projeto['voluntarios'] = request.form['voluntarios']
        save_data(data)
        return redirect(url_for('index'))
    
    return render_template('volunteers.html', projeto=projeto)

if __name__ == '__main__':
    app.run(debug=True)