from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)
DATA_FILE = 'banco.json'

def carregar_dados():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def salvar_dados(dados):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4)

@app.route('/')
def index():
    dados = carregar_dados()
    return render_template('index.html', dados=dados)

# Rota responsável por Criar (Create) e Atualizar (Update)
@app.route('/salvar', methods=['POST'])
def salvar():
    data_registro = request.form.get('data') # Formato DD/MM/YYYY
    litros = request.form.get('litros')
    
    if data_registro and litros:
        dados = carregar_dados()
        # Salva ou atualiza a quantidade de litros na data específica
        dados[data_registro] = float(litros)
        salvar_dados(dados)
        
    return redirect(url_for('index'))

# Rota responsável por Deletar (Delete)
@app.route('/deletar', methods=['POST'])
def deletar():
    data_registro = request.form.get('data')
    dados = carregar_dados()
    
    if data_registro in dados:
        del dados[data_registro]
        salvar_dados(dados)
        
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# API para fornecer os dados ao JavaScript do Gráfico (Read)
@app.route('/api/dados')
def api_dados():
    return jsonify(carregar_dados())

if __name__ == '__main__':
    app.run(debug=True)