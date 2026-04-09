from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'chave_secreta_para_flash'
ARQUIVO_JSON = 'dados.json'

# --- Funções de Manipulação do JSON ---
def ler_dados():
    if not os.path.exists(ARQUIVO_JSON):
        return []
    with open(ARQUIVO_JSON, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def salvar_dados(dados):
    with open(ARQUIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# --- Cálculo de Progresso (HH/MM) ---
def calcular_percentual(cumpridas, totais):
    try:
        hc, mc = map(int, cumpridas.split(':'))
        ht, mt = map(int, totais.split(':'))
        minutos_c = hc * 60 + mc
        minutos_t = ht * 60 + mt
        
        if minutos_t == 0:
            return 0
        
        percentual = (minutos_c / minutos_t) * 100
        # Alterado para 2 casas decimais
        return min(round(percentual, 2), 100.0) 
    except ValueError:
        return 0

# --- Rotas ---
@app.route('/')
def index():
    dados = ler_dados()
    materias = []
    percentuais = []
    
    for item in dados:
        materias.append(item['materia'])
        percentuais.append(calcular_percentual(item['horas_cumpridas'], item['horas_totais']))
        
    return render_template('index.html', dados=dados, materias=json.dumps(materias), percentuais=json.dumps(percentuais))

@app.route('/gerenciar', methods=['GET', 'POST'])
def gerenciar():
    dados = ler_dados()
    
    # Criar (C)
    if request.method == 'POST':
        nova_materia = {
            "materia": request.form['materia'].strip(),
            "horas_totais": request.form['horas_totais'],
            "horas_cumpridas": request.form['horas_cumpridas']
        }
        
        # Evita duplicatas usando o nome da matéria
        if any(d['materia'].lower() == nova_materia['materia'].lower() for d in dados):
            flash('Esta matéria já está cadastrada!', 'erro')
        else:
            dados.append(nova_materia)
            salvar_dados(dados)
            flash('Matéria adicionada com sucesso!', 'sucesso')
            return redirect(url_for('gerenciar'))

    # Buscar (R)
    termo_busca = request.args.get('busca', '').lower()
    if termo_busca:
        dados = [d for d in dados if termo_busca in d['materia'].lower()]

    return render_template('gerenciar.html', dados=dados, busca=termo_busca)

@app.route('/editar/<nome_materia>', methods=['GET', 'POST'])
def editar(nome_materia):
    dados = ler_dados()
    materia_obj = next((d for d in dados if d['materia'] == nome_materia), None)
    
    if not materia_obj:
        return redirect(url_for('gerenciar'))

    # Atualizar (U)
    if request.method == 'POST':
        novo_nome = request.form['materia'].strip()
        
        # Checa se o novo nome já existe em outra matéria
        if novo_nome != nome_materia and any(d['materia'].lower() == novo_nome.lower() for d in dados):
            flash('Já existe outra matéria com esse nome.', 'erro')
        else:
            materia_obj['materia'] = novo_nome
            materia_obj['horas_totais'] = request.form['horas_totais']
            materia_obj['horas_cumpridas'] = request.form['horas_cumpridas']
            salvar_dados(dados)
            flash('Matéria atualizada!', 'sucesso')
            return redirect(url_for('gerenciar'))

    return render_template('editar.html', materia=materia_obj)

@app.route('/excluir/<nome_materia>', methods=['POST'])
def excluir(nome_materia):
    dados = ler_dados()
    # Deletar (D) - Filtrando fora a matéria pelo nome
    dados_atualizados = [d for d in dados if d['materia'] != nome_materia]
    salvar_dados(dados_atualizados)
    flash('Matéria excluída.', 'sucesso')
    return redirect(url_for('gerenciar'))

if __name__ == '__main__':
    app.run(debug=True)