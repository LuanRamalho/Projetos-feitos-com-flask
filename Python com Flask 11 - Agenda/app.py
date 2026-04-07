from flask import Flask, render_template, request, redirect, url_for, jsonify
import calendar
from datetime import datetime
import json
import os
import locale # Importe o módulo locale

app = Flask(__name__)
DATA_FILE = 'data.json'

# Configura o locale para Português do Brasil para nomes de meses e dias
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.utf-8')
except locale.Error:
    # Caso o sistema não tenha o locale pt_BR instalado, tenta um fallback
    # Em alguns sistemas Windows, pode ser necessário 'Portuguese_Brazil'
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil')
    except locale.Error:
        # Se falhar totalmente, mantém o inglês (padrão)
        print("Aviso: Locale 'pt_BR' não encontrado. Nomes dos meses podem aparecer em inglês.")

# Inicializa o arquivo JSON se não existir
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

def get_db():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_db(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f: # Garante o encoding UTF-8
        json.dump(data, f, indent=4, ensure_ascii=False) # Permite acentos reais

@app.route('/')
def index():
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)

    if month > 12:
        month = 1
        year += 1
    elif month < 1:
        month = 12
        year -= 1

    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdayscalendar(year, month)
    
    # CORREÇÃO: O nome do mês agora virá em português devido ao locale
    # Capitalizamos a primeira letra (ex: "março" vira "Março")
    month_name = calendar.month_name[month].capitalize()
    
    db = get_db()
    
    highlighted_days = []
    for date_key, content in db.items():
        try:
            dt = datetime.strptime(date_key, '%Y-%m-%d')
            if dt.year == year and dt.month == month:
                if content.get('compromisso') or (content.get('tarefas') and len(content['tarefas']) > 0):
                    highlighted_days.append(dt.day)
        except ValueError:
            continue

    return render_template('index.html', weeks=weeks, month=month, year=year, 
                           month_name=month_name, highlighted_days=highlighted_days)

@app.route('/dia/<int:year>/<int:month>/<int:day>')
def detalhe_dia(year, month, day):
    date_key = f"{year}-{month:02d}-{day:02d}"
    db = get_db()
    dados = db.get(date_key, {"compromisso": "", "tarefas": []})
    return render_template('dia.html', year=year, month=month, day=day, dados=dados)

@app.route('/salvar/<date_key>', methods=['POST'])
def salvar(date_key):
    db = get_db()
    if date_key not in db:
        db[date_key] = {"compromisso": "", "tarefas": []}
    
    tipo = request.form.get('tipo')
    if tipo == 'compromisso':
        db[date_key]['compromisso'] = request.form.get('conteudo')
    elif tipo == 'tarefa':
        nova_tarefa = request.form.get('conteudo').strip()
        if nova_tarefa:
            db[date_key]['tarefas'].append(nova_tarefa)
            
    save_db(db)
    y, m, d = map(int, date_key.split('-'))
    return redirect(url_for('detalhe_dia', year=y, month=m, day=d))

@app.route('/editar_tarefa/<date_key>/<int:index>', methods=['POST'])
def editar_tarefa(date_key, index):
    db = get_db()
    novo_nome = request.form.get('novo_nome').strip()
    
    if date_key in db and index < len(db[date_key]['tarefas']):
        if novo_nome:
            db[date_key]['tarefas'][index] = novo_nome
            save_db(db)
            
    y, m, d = map(int, date_key.split('-'))
    return redirect(url_for('detalhe_dia', year=y, month=m, day=d))

@app.route('/deletar_tarefa/<date_key>/<int:index>')
def deletar_tarefa(date_key, index):
    db = get_db()
    if date_key in db and index < len(db[date_key]['tarefas']):
        db[date_key]['tarefas'].pop(index)
        save_db(db)
        
    y, m, d = map(int, date_key.split('-'))
    return redirect(url_for('detalhe_dia', year=y, month=m, day=d))

if __name__ == '__main__':
    app.run(debug=True)