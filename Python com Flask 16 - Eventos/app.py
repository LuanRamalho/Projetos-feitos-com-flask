import json
import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "secret_event_key"
DATA_FILE = 'eventos.json'

# Inicializa o arquivo JSON se não existir
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
    eventos = carregar_dados()
    return render_template('index.html', eventos=eventos)

@app.route('/evento/novo', methods=['GET', 'POST'])
def novo_evento():
    if request.method == 'POST':
        dados = carregar_dados()
        novo = {
            "id": len(dados) + 1,
            "nome": request.form['nome'],
            "data": request.form['data'],
            "palestrantes": request.form['palestrantes'].split(','),
            "vagas": int(request.form['vagas']),
            "participantes": []
        }
        dados.append(novo)
        salvar_dados(dados)
        return redirect(url_for('index'))
    return render_template('evento.html', acao="Criar Novo Evento")

@app.route('/evento/editar/<int:id>', methods=['GET', 'POST'])
def editar_evento(id):
    dados = carregar_dados()
    evento = next((e for e in dados if e['id'] == id), None)
    
    if request.method == 'POST':
        evento['nome'] = request.form['nome']
        evento['data'] = request.form['data']
        evento['palestrantes'] = request.form['palestrantes'].split(',')
        evento['vagas'] = int(request.form['vagas'])
        salvar_dados(dados)
        return redirect(url_for('index'))
    
    palestrantes_str = ",".join(evento['palestrantes'])
    return render_template('evento.html', evento=evento, palestrantes_str=palestrantes_str, acao="Editar Evento")

@app.route('/evento/deletar/<int:id>')
def deletar_evento(id):
    dados = carregar_dados()
    dados = [e for e in dados if e['id'] != id]
    salvar_dados(dados)
    return redirect(url_for('index'))

@app.route('/evento/registrar/<int:id>', methods=['GET', 'POST'])
def registrar_participante(id):
    dados = carregar_dados()
    evento = next((e for e in dados if e['id'] == id), None)
    
    if request.method == 'POST':
        if len(evento['participantes']) < evento['vagas']:
            evento['participantes'].append(request.form['nome_participante'])
            salvar_dados(dados)
            flash("Inscrição confirmada!")
        else:
            flash("Desculpe, vagas esgotadas!")
        return redirect(url_for('index'))
    
    return render_template('participar.html', evento=evento)

if __name__ == '__main__':
    app.run(debug=True)