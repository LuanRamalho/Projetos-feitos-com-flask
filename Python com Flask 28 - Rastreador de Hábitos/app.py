from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = 'habits.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def calculate_days(start_str, end_str):
    fmt = "%d/%m/%Y"
    try:
        start = datetime.strptime(start_str, fmt)
        end = datetime.strptime(end_str, fmt)
        delta = (end - start).days + 1
        return max(delta, 0)
    except:
        return 0

@app.route('/')
def index():
    habits = load_data()
    return render_template('index.html', habits=habits)

@app.route('/add', methods=['GET', 'POST'])
def add_habit():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        habits = load_data()
        habits[name] = {
            "description": description,
            "start_date": start_date,
            "end_date": end_date,
            "manual_completed": 0  # Inicializa o contador manual
        }
        save_data(habits)
        return redirect(url_for('index'))
    return render_template('add_habit.html')

@app.route('/update_progress/<name>', methods=['POST'])
def update_progress(name):
    habits = load_data()
    completed_input = request.form.get('completed_count', 0)
    
    if name in habits:
        try:
            # Salva a quantidade exata de dias informada pelo usuário
            habits[name]['manual_completed'] = int(completed_input)
            save_data(habits)
        except ValueError:
            pass
            
    return redirect(url_for('index'))

@app.route('/progress')
def progress():
    habits = load_data()
    processed_habits = []
    
    for name, info in habits.items():
        # Enviamos apenas os dados básicos
        processed_habits.append({
            "name": name,
            "completed": info.get('manual_completed', 0),
            "start_date": info.get('start_date'),
            "end_date": info.get('end_date')
        })
        
    return render_template('progress.html', habits=processed_habits)

@app.route('/edit/<name>', methods=['GET', 'POST'])
def edit_habit(name):
    habits = load_data()
    habit = habits.get(name)
    
    if request.method == 'POST':
        new_name = request.form.get('name')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        # Se o nome mudou, removemos a chave antiga e criamos a nova
        if new_name != name:
            del habits[name]
            
        habits[new_name] = {
            "description": description,
            "start_date": start_date,
            "end_date": end_date,
            "manual_completed": int(request.form.get('manual_completed', 0))
        }
        save_data(habits)
        return redirect(url_for('index'))
        
    return render_template('edit_habit.html', name=name, habit=habit)

@app.route('/delete/<name>')
def delete_habit(name):
    habits = load_data()
    if name in habits:
        del habits[name]
        save_data(habits)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)