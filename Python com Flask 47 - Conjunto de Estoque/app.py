from flask import Flask, render_template, request, redirect, url_for
import json
import os
import uuid

app = Flask(__name__)
DATA_FILE = 'data.json'

# --- Funções Auxiliares ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"stores": []}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# --- Rotas da Primeira Janela (Lojas) ---
@app.route('/', methods=['GET', 'POST'])
def index():
    data = load_data()
    search = request.args.get('search', '').lower()
    
    if search:
        stores = [s for s in data['stores'] if search in s['name'].lower()]
    else:
        stores = data['stores']
        
    return render_template('index.html', stores=stores)

@app.route('/add_store', methods=['POST'])
def add_store():
    data = load_data()
    new_store = {
        "id": str(uuid.uuid4()),
        "name": request.form.get('name'),
        "products": []
    }
    data['stores'].append(new_store)
    save_data(data)
    return redirect(url_for('index'))

@app.route('/edit_store/<id>', methods=['POST'])
def edit_store(id):
    data = load_data()
    for s in data['stores']:
        if s['id'] == id:
            s['name'] = request.form.get('name')
            break
    save_data(data)
    return redirect(url_for('index'))

@app.route('/delete_store/<id>')
def delete_store(id):
    data = load_data()
    data['stores'] = [s for s in data['stores'] if s['id'] != id]
    save_data(data)
    return redirect(url_for('index'))

# --- Rotas da Segunda Janela (Produtos) ---
@app.route('/store/<store_id>')
def store_details(store_id):
    data = load_data()
    store = next((s for s in data['stores'] if s['id'] == store_id), None)
    
    search_prod = request.args.get('search_prod', '').lower()
    search_supp = request.args.get('search_supp', '').lower()
    
    products = store['products']
    if search_prod:
        products = [p for p in products if search_prod in p['name'].lower()]
    if search_supp:
        products = [p for p in products if search_supp in p['supplier'].lower()]
        
    return render_template('store_details.html', store=store, products=products)

@app.route('/store/<store_id>/add_product', methods=['POST'])
def add_product(store_id):
    data = load_data()
    for s in data['stores']:
        if s['id'] == store_id:
            new_prod = {
                "id": str(uuid.uuid4()),
                "name": request.form.get('name'),
                "supplier": request.form.get('supplier'),
                "quantity": int(request.form.get('quantity')),
                "price": float(request.form.get('price'))
            }
            s['products'].append(new_prod)
            break
    save_data(data)
    return redirect(url_for('store_details', store_id=store_id))

@app.route('/store/<store_id>/edit_product/<prod_id>', methods=['POST'])
def edit_product(store_id, prod_id):
    data = load_data()
    for s in data['stores']:
        if s['id'] == store_id:
            for p in s['products']:
                if p['id'] == prod_id:
                    p['name'] = request.form.get('name')
                    p['supplier'] = request.form.get('supplier')
                    p['quantity'] = int(request.form.get('quantity'))
                    p['price'] = float(request.form.get('price'))
                    break
    save_data(data)
    return redirect(url_for('store_details', store_id=store_id))

@app.route('/store/<store_id>/delete_product/<prod_id>')
def delete_product(store_id, prod_id):
    data = load_data()
    for s in data['stores']:
        if s['id'] == store_id:
            s['products'] = [p for p in s['products'] if p['id'] != prod_id]
            break
    save_data(data)
    return redirect(url_for('store_details', store_id=store_id))

if __name__ == '__main__':
    app.run(debug=True)