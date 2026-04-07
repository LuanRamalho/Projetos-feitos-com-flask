from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
DATA_FILE = 'data.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    faturamentos = load_data()
    # Calcula o total para exibir nos cards
    for f in faturamentos:
        f['total'] = sum(f['meses'].values())
    return render_template('index.html', faturamentos=faturamentos)

@app.route('/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        ano = request.form.get('ano')
        meses = {str(i): float(request.form.get(f'mes_{i}')) for i in range(1, 13)}
        
        data = load_data()
        data.append({"ano": ano, "meses": meses})
        save_data(data)
        return redirect(url_for('index'))
    return render_template('form.html', faturamento=None)

@app.route('/editar/<ano>', methods=['GET', 'POST'])
def editar(ano):
    data = load_data()
    faturamento = next((f for f in data if f['ano'] == ano), None)
    
    if request.method == 'POST':
        faturamento['meses'] = {str(i): float(request.form.get(f'mes_{i}')) for i in range(1, 13)}
        save_data(data)
        return redirect(url_for('index'))
    
    return render_template('form.html', faturamento=faturamento)

@app.route('/excluir/<ano>')
def excluir(ano):
    data = load_data()
    data = [f for f in data if f['ano'] != ano]
    save_data(data)
    return redirect(url_for('index'))

@app.route('/grafico/<ano>')
def grafico(ano):
    data = load_data()
    faturamento = next((f for f in data if f['ano'] == ano), None)
    total = sum(faturamento['meses'].values())
    return render_template('grafico.html', f=faturamento, total=total)

if __name__ == '__main__':
    app.run(debug=True)