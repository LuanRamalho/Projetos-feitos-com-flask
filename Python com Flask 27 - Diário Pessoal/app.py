from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'chave_secreta_colorida'

# Caminhos dos arquivos JSON
USUARIOS_FILE = 'usuarios.json'
ENTRADAS_FILE = 'entradas.json'

def carregar_dados(arquivo):
    if not os.path.exists(arquivo):
        return []
    with open(arquivo, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_dados(arquivo, dados):
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    todas_entradas = carregar_dados(ENTRADAS_FILE)
    entradas_user = [e for e in todas_entradas if e['usuario'] == session['usuario']]
    
    # Esta função resolve o problema da ordenação e das datas antigas
    def ordenar_data(entrada):
        formatos = ['%d/%m/%Y às %H:%M', '%d/%m/%Y']
        for formato in formatos:
            try:
                return datetime.strptime(entrada['data'], formato)
            except ValueError:
                continue
        return datetime.min

    entradas_user.sort(key=ordenar_data, reverse=True)
    return render_template('index.html', entradas=entradas_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            # 1. Carrega a lista atual de usuários
            usuarios = carregar_dados(USUARIOS_FILE)
            
            # 2. Se o usuário não estiver na lista, adiciona ele
            if not any(u['nome'] == username for u in usuarios):
                usuarios.append({"nome": username})
                salvar_dados(USUARIOS_FILE, usuarios) # Aqui o arquivo é criado/atualizado
            
            # 3. Salva na sessão e redireciona
            session['usuario'] = username
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route('/adicionar', methods=['POST'])
def adicionar():
    if 'usuario' not in session: return redirect(url_for('login'))
    
    texto = request.form.get('texto')
    # Formato atualizado com Hora
    data_hora_agora = datetime.now().strftime('%d/%m/%Y às %H:%M')
    
    entradas = carregar_dados(ENTRADAS_FILE)
    nova_entrada = {
        'id': len(entradas) + 1,
        'usuario': session['usuario'],
        'data': data_hora_agora, 
        'texto': texto
    }
    entradas.append(nova_entrada)
    salvar_dados(ENTRADAS_FILE, entradas)
    return redirect(url_for('index'))

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if 'usuario' not in session: return redirect(url_for('login'))
    
    entradas = carregar_dados(ENTRADAS_FILE)
    entrada = next((e for e in entradas if e['id'] == id and e['usuario'] == session['usuario']), None)
    
    if request.method == 'POST':
        entrada['texto'] = request.form.get('texto')
        salvar_dados(ENTRADAS_FILE, entradas)
        return redirect(url_for('index'))
        
    return render_template('editar.html', entrada=entrada)

@app.route('/excluir/<int:id>')
def excluir(id):
    if 'usuario' not in session: return redirect(url_for('login'))
    
    entradas = carregar_dados(ENTRADAS_FILE)
    entradas = [e for e in entradas if not (e['id'] == id and e['usuario'] == session['usuario'])]
    salvar_dados(ENTRADAS_FILE, entradas)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)