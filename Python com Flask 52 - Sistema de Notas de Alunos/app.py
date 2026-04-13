from flask import Flask, render_template, request, redirect, url_for, flash, session
import json
import os

app = Flask(__name__)
app.secret_key = 'chave_secreta_para_sessoes'
DB_FILE = 'banco.json'

# --- CONFIGURAÇÃO DE ACESSO ADMIN ---
ADMIN_USER = "admin"
ADMIN_PASS = "12345"

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

@app.route('/login_admin_prompt')
def login_admin_prompt():
    """ Rota que valida as credenciais enviadas pelo prompt do JavaScript """
    u = request.args.get('u')
    p = request.args.get('p')
    
    if u == ADMIN_USER and p == ADMIN_PASS:
        session['admin_logado'] = True
        return redirect(url_for('admin'))
    
    flash('Credenciais de administrador incorretas!', 'error')
    return redirect(url_for('aluno'))

@app.route('/logout')
def logout():
    session.clear() # Limpa todas as sessões (aluno e admin)
    return redirect(url_for('login'))

# --- ROTAS DO ALUNO ---
@app.route('/aluno')
def aluno():
    if 'matricula' not in session:
        return redirect(url_for('login'))
        
    matricula = session['matricula']
    db = load_db()
    info_usuario = db['usuarios'].get(matricula, {})
    nome_aluno = info_usuario.get('nome', 'Aluno')
    notas_aluno = db['notas'].get(matricula, {})
    
    return render_template('aluno.html', matricula=matricula, nome=nome_aluno, notas=notas_aluno)

# --- ROTAS DO ADMIN (PROTEGIDAS) ---

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Bloqueio de segurança: se não passou pelo prompt, volta pro login
    if not session.get('admin_logado'):
        return redirect(url_for('login'))
        
    db = load_db()
    
    if request.method == 'POST':
        mat = request.form['matricula_selecionada']
        disc = request.form['disciplina']
        
        try:
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
            "nome_aluno": db['usuarios'][mat]['nome']
        }
        save_db(db)
        flash('Notas salvas com sucesso!', 'success')
        return redirect(url_for('admin'))
        
    return render_template('admin.html', bd=db)

@app.route('/admin/delete/<matricula>/<disciplina>', methods=['POST'])
def deletar_nota(matricula, disciplina):
    if not session.get('admin_logado'):
        return redirect(url_for('login'))

    db = load_db()
    if matricula in db['notas'] and disciplina in db['notas'][matricula]:
        del db['notas'][matricula][disciplina]
        if not db['notas'][matricula]:
            del db['notas'][matricula]
        save_db(db)
        flash('Registro removido com sucesso!', 'success')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
