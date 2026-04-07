from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
import secrets
import string

app = Flask(__name__)
DB_FILE = 'database.json'

# Inicializa o JSON se não existir
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w') as f:
        json.dump({}, f)

def get_db():
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    search = request.args.get('search', '').lower()
    db = get_db()
    if search:
        # Filtra os cards pelo nome do site
        items = {k: v for k, v in db.items() if search in k.lower()}
    else:
        items = db
    return render_template('index.html', items=items)

@app.route('/add', methods=['POST'])
def add_site():
    site_name = request.form.get('site_name')
    data = {
        "url": request.form.get('url'),
        "user": request.form.get('user'),
        "passwords": [request.form.get('password')],
        "extra_fields": {}
    }
    db = get_db()
    db[site_name] = data
    save_db(db)
    return redirect(url_for('index'))

@app.route('/details/<site_name>')
def details(site_name):
    db = get_db()
    site_data = db.get(site_name)
    return render_template('details.html', name=site_name, data=site_data)

@app.route('/update/<site_name>', methods=['POST'])
def update_site(site_name):
    db = get_db()
    # Captura campos dinâmicos
    passwords = request.form.getlist('passwords[]')
    extra_keys = request.form.getlist('extra_keys[]')
    extra_vals = request.form.getlist('extra_vals[]')
    
    extra_fields = dict(zip(extra_keys, extra_vals))
    
    db[site_name].update({
        "url": request.form.get('url'),
        "user": request.form.get('user'),
        "passwords": passwords,
        "extra_fields": extra_fields
    })
    save_db(db)
    return redirect(url_for('index'))

@app.route('/delete/<site_name>')
def delete_site(site_name):
    db = get_db()
    if site_name in db:
        del db[site_name]
        save_db(db)
    return redirect(url_for('index'))

@app.route('/generator')
def generator():
    return render_template('generator.html')

@app.route('/api/generate')
def api_generate():
    length = int(request.args.get('length', 16))
    chars = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(chars) for _ in range(length))
    return jsonify(password=password)

if __name__ == '__main__':
    app.run(debug=True)