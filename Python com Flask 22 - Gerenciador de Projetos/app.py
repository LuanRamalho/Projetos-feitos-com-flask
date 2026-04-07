from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'tarefas.json'

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

def carregar_dados():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_dados(dados):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4)

@app.route('/')
def index():
    busca = request.args.get('busca', '').lower()
    tarefas = carregar_dados()
    
    for t in tarefas:
        try:
            data_obj = datetime.strptime(t['prazo'], '%Y-%m-%d')
            t['prazo_formatado'] = data_obj.strftime('%d/%m/%Y')
        except:
            t['prazo_formatado'] = t['prazo']

    if busca:
        tarefas = [t for t in tarefas if busca in t['nome'].lower()]
        
    return render_template('index.html', tarefas=tarefas, busca=busca)

@app.route('/add', methods=['POST'])
def add():
    tarefas = carregar_dados()
    nova_tarefa = {
        "nome": request.form.get('nome'),
        "time": request.form.get('time'),
        "prazo": request.form.get('prazo'),
        "status": request.form.get('status'),
        "descricao": request.form.get('descricao') # Novo campo
    }
    tarefas.append(nova_tarefa)
    salvar_dados(tarefas)
    return redirect(url_for('index'))

@app.route('/edit_status/<int:index>', methods=['POST'])
def edit_status(index):
    tarefas = carregar_dados()
    tarefas[index]['status'] = request.form.get('status')
    salvar_dados(tarefas)
    return redirect(url_for('index'))

@app.route('/update_completo/<int:index>', methods=['POST'])
def update_completo(index):
    tarefas = carregar_dados()
    tarefas[index]['nome'] = request.form.get('nome_editado')
    tarefas[index]['time'] = request.form.get('time_editado')
    tarefas[index]['prazo'] = request.form.get('prazo_editado')
    tarefas[index]['descricao'] = request.form.get('descricao_editada') # Atualização da descrição
    salvar_dados(tarefas)
    return redirect(url_for('index'))

@app.route('/delete/<int:index>')
def delete(index):
    tarefas = carregar_dados()
    tarefas.pop(index)
    salvar_dados(tarefas)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)