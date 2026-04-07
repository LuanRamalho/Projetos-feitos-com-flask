from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = "chave_secreta_colorida"
DATA_FILE = 'usuarios.json'

def carregar_usuarios():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_usuarios(usuarios):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, indent=4)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    usuarios = carregar_usuarios()

    if username in usuarios and usuarios[username] == password:
        return redirect(url_for('sucesso', nome=username))
    
    flash("Usuário ou senha incorretos!", "error")
    return redirect(url_for('index'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form.get('username')
        pw1 = request.form.get('password')
        pw2 = request.form.get('confirm_password')

        if pw1 != pw2:
            flash("As senhas não coincidem!", "error")
            return redirect(url_for('cadastro'))

        usuarios = carregar_usuarios()
        if username in usuarios:
            flash("Este usuário já existe!", "error")
            return redirect(url_for('cadastro'))

        usuarios[username] = pw1
        salvar_usuarios(usuarios)
        flash("Cadastro realizado com sucesso!", "success")
        return redirect(url_for('index'))

    return render_template('cadastro.html')

@app.route('/esqueci', methods=['GET', 'POST'])
def esqueci():
    msg = None
    if request.method == 'POST':
        username = request.form.get('username')
        usuarios = carregar_usuarios()
        
        if username in usuarios:
            msg = f"Dados encontrados! Login: {username} | Senha: {usuarios[username]}"
        else:
            flash("Usuário não encontrado!", "error")
            
    return render_template('esqueci_senha.html', info_recuperada=msg)

@app.route('/sucesso/<nome>')
def sucesso(nome):
    return render_template('sucesso.html', nome=nome)

if __name__ == '__main__':
    app.run(debug=True)