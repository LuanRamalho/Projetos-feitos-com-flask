from flask import Flask, render_template, request, redirect, url_for, flash, session
import json
import os

app = Flask(__name__)
app.secret_key = 'chave_secreta_para_sessoes'
DB_FILE = 'banco.json'

# --- FUNÇÕES DO BANCO JSON ---
def load_db():
    if not os.path.exists(DB_FILE):
        save_db({"usuarios": {}, "notas": {}})
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- ROTAS DE AUTENTICAÇÃO ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        matricula = request.form['matricula']
        senha = request.form['senha']
        db = load_db()
        
        if matricula in db['usuarios'] and db['usuarios'][matricula]['senha'] == senha:
            session['matricula'] = matricula
            return redirect(url_for('aluno'))
        else:
            flash('Matrícula ou senha incorretos.', 'error')
            
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome'] # Novo campo
        matricula = request.form['matricula']
        senha = request.form['senha']
        senha2 = request.form['senha2']
        
        if senha != senha2:
            flash('As senhas não coincidem!', 'error')
            return redirect(url_for('cadastro'))
            
        db = load_db()
        if matricula in db['usuarios']:
            flash('Matrícula já cadastrada!', 'error')
        else:
            # Salvando nome e senha atrelados à matrícula
            db['usuarios'][matricula] = {'nome': nome, 'senha': senha}
            save_db(db)
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('login'))
            
    return render_template('cadastro.html')

@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    if request.method == 'POST':
        matricula = request.form['matricula']
        db = load_db()
        
        if matricula in db['usuarios']:
            senha = db['usuarios'][matricula]['senha']
            flash(f'Sua Matrícula: {matricula} | Sua Senha: {senha}', 'success')
        else:
            flash('Matrícula não encontrada no sistema.', 'error')
            
    return render_template('recuperar.html')

@app.route('/logout')
def logout():
    session.pop('matricula', None)
    return redirect(url_for('login'))

# --- ROTAS DO ALUNO ---
@app.route('/aluno')
def aluno():
    if 'matricula' not in session:
        return redirect(url_for('login'))
        
    matricula = session['matricula']
    db = load_db()
    
    # Busca o nome do aluno no banco
    info_usuario = db['usuarios'].get(matricula, {})
    nome_aluno = info_usuario.get('nome', 'Aluno')
    
    notas_aluno = db['notas'].get(matricula, {})
    
    return render_template('aluno.html', matricula=matricula, nome=nome_aluno, notas=notas_aluno)

# --- ROTAS DO ADMIN (CRUD COMPLETO) ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    db = load_db()
    
    if request.method == 'POST':
        mat = request.form['matricula_selecionada'] # Agora vem de um select
        disc = request.form['disciplina']
        
        try:
            # Mantendo a precisão de 1 casa decimal solicitada
            n1 = round(float(request.form['nota1']), 1)
            n2 = round(float(request.form['nota2']), 1)
            n3 = round(float(request.form['nota3']), 1)
            n4 = round(float(request.form['nota4']), 1)
        except ValueError:
            flash('As notas devem ser números válidos!', 'error')
            return redirect(url_for('admin'))
            
        media = round((n1 + n2 + n3 + n4) / 4, 1)
        status = "APROVADO" if media >= 6.0 else "REPROVADO"
        
        if mat not in db['notas']:
            db['notas'][mat] = {}
            
        db['notas'][mat][disc] = {
            "n1": n1, "n2": n2, "n3": n3, "n4": n4,
            "media": media, "status": status,
            "nome_aluno": db['usuarios'][mat]['nome'] # Vincula o nome à nota
        }
        save_db(db)
        flash(f'Notas salvas com sucesso!', 'success')
        return redirect(url_for('admin'))
        
    return render_template('admin.html', bd=db)

@app.route('/admin/delete/<matricula>/<disciplina>', methods=['POST'])
def deletar_nota(matricula, disciplina):
    db = load_db()
    if matricula in db['notas'] and disciplina in db['notas'][matricula]:
        del db['notas'][matricula][disciplina]
        if not db['notas'][matricula]: # Limpa objeto vazio
            del db['notas'][matricula]
        save_db(db)
        flash('Registro removido com sucesso!', 'success')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)