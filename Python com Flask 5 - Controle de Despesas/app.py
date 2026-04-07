import json
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DATA_FILE = 'data.json'

# Inicializa o arquivo JSON se não existir
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    return jsonify(load_data())

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    new_item = request.json
    transactions = load_data()
    transactions.append(new_item)
    save_data(transactions)
    return jsonify({"status": "success"})

@app.route('/api/transactions/update', methods=['POST'])
def update_transaction():
    data = request.json
    idx = data.get('index')
    updated_item = data.get('item')
    transactions = load_data()
    
    if 0 <= idx < len(transactions):
        transactions[idx] = updated_item
        save_data(transactions)
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 400

@app.route('/api/transactions/delete', methods=['POST'])
def delete_transaction():
    data = request.json
    idx = data.get('index')
    transactions = load_data()
    
    if 0 <= idx < len(transactions):
        transactions.pop(idx)
        save_data(transactions)
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    app.run(debug=True)