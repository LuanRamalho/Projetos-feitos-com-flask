from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
DB_FILE = 'database.json'

# Inicializa o banco de dados se não existir
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w') as f:
        json.dump([], f)

def get_db():
    # O encoding='utf-8' aceita os acentos legíveis no JSON
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data):
    # O encoding='utf-8' aceita os acentos legíveis no JSON
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False) # ensure_ascii=False mantém os acentos legíveis no JSON

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form.get('nome')
    fabricante = request.form.get('fabricante')
    quantidade = request.form.get('quantidade')

    db = get_db()
    db.append({
        "nome": nome,
        "fabricante": fabricante,
        "quantidade": int(quantidade)
    })
    save_db(db)
    return redirect(url_for('estoque'))

@app.route('/estoque')
def estoque():
    search_query = request.args.get('search', '').lower()
    db = get_db()
    
    if search_query:
        # Busca por nome ou fabricante
        bebidas = [b for b in db if search_query in b['nome'].lower() or search_query in b['fabricante'].lower()]
    else:
        bebidas = db
        
    return render_template('estoque.html', bebidas=bebidas)

@app.route('/editar', methods=['GET'])
def editar_form():
    nome = request.args.get('nome')
    fabricante = request.args.get('fabricante')
    
    db = get_db()
    # Busca o item específico para preencher o formulário
    item = next((b for b in db if b['nome'] == nome and b['fabricante'] == fabricante), None)
    
    if item:
        return render_template('editar.html', item=item)
    return redirect(url_for('estoque'))

@app.route('/atualizar', methods=['POST'])
def atualizar():
    # Nome e fabricante originais (para encontrar o registro)
    old_nome = request.form.get('old_nome')
    old_fabricante = request.form.get('old_fabricante')
    
    # Novos dados
    novo_nome = request.form.get('nome')
    novo_fabricante = request.form.get('fabricante')
    nova_quantidade = request.form.get('quantidade')

    db = get_db()
    for bebida in db:
        if bebida['nome'] == old_nome and bebida['fabricante'] == old_fabricante:
            bebida['nome'] = novo_nome
            bebida['fabricante'] = novo_fabricante
            bebida['quantidade'] = int(nova_quantidade)
            break
            
    save_db(db)
    return redirect(url_for('estoque'))

@app.route('/deletar', methods=['POST'])
def deletar():
    nome = request.form.get('nome')
    fabricante = request.form.get('fabricante')
    
    db = get_db()
    # Filtra mantendo apenas o que não corresponde ao item deletado
    db = [b for b in db if not (b['nome'] == nome and b['fabricante'] == fabricante)]
    save_db(db)
    return redirect(url_for('estoque'))

if __name__ == '__main__':
    app.run(debug=True)