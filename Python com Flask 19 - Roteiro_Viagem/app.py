from flask import Flask, render_template, request, redirect, url_for
import json
import os
import uuid

app = Flask(__name__)
DATA_FILE = 'data.json'

# Inicializa o arquivo JSON se não existir
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    itineraries = load_data()
    return render_template('index.html', itineraries=itineraries)

@app.route('/add', methods=['POST'])
def add_itinerary():
    data = load_data()
    new_itinerary = {
        "id": str(uuid.uuid4()),
        "destino": request.form.get('destino'),
        "data": request.form.get('data'), # Formato DD/MM/YYYY
        "orcamento": request.form.get('orcamento'), # Formato R$
        "atividades": request.form.get('atividades'),
        "pontos_turisticos": request.form.get('pontos_turisticos')
    }
    data.append(new_itinerary)
    save_data(data)
    return redirect(url_for('index'))

@app.route('/edit/<id>', methods=['POST'])
def edit_itinerary(id):
    data = load_data()
    for item in data:
        if item['id'] == id:
            item['destino'] = request.form.get('destino')
            item['data'] = request.form.get('data')
            item['orcamento'] = request.form.get('orcamento')
            item['atividades'] = request.form.get('atividades')
            item['pontos_turisticos'] = request.form.get('pontos_turisticos')
            break
    save_data(data)
    return redirect(url_for('index'))

@app.route('/delete/<id>')
def delete_itinerary(id):
    data = load_data()
    data = [item for item in data if item['id'] != id]
    save_data(data)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)