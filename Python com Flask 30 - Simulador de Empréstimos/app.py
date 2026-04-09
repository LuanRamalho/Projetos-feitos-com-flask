from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = 'simulacoes.json'

# Inicializa o arquivo JSON se não existir
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

def get_db():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

# CRUD - Create / Update
@app.route('/api/simular', methods=['POST'])
def simular():
    data = request.json
    nome = data.get('nome')
    valor = float(data.get('valor'))
    taxa = float(data.get('taxa')) / 100  # Convertendo para decimal
    prazo = int(data.get('prazo'))

    # Fórmula Price (Parcelas Fixas)
    # PMT = P * [i(1+i)^n] / [(1+i)^n - 1]
    if taxa > 0:
        parcela = valor * (taxa * (1 + taxa)**prazo) / ((1 + taxa)**prazo - 1)
    else:
        parcela = valor / prazo

    # Gerar Tabela de Amortização
    saldo_devedor = valor
    tabela = []
    total_juros = 0
    
    for i in range(1, prazo + 1):
        juros_mes = saldo_devedor * taxa
        amortizacao_mes = parcela - juros_mes
        saldo_devedor -= amortizacao_mes
        total_juros += juros_mes
        
        tabela.append({
            "mes": i,
            "parcela": round(parcela, 2),
            "juros": round(juros_mes, 2),
            "amortizacao": round(amortizacao_mes, 2),
            "saldo": max(0, round(saldo_devedor, 2))
        })

    resultado = {
        "nome": nome,
        "valor_principal": valor,
        "taxa_mensal": taxa * 100,
        "prazo": prazo,
        "valor_parcela": round(parcela, 2),
        "total_pago": round(parcela * prazo, 2),
        "total_juros": round(total_juros, 2),
        "tabela": tabela
    }

    # Salvar no JSON (CRUD)
    db = get_db()
    # Se já existir uma simulação com o mesmo nome, atualiza (Update)
    db = [s for s in db if s['nome'] != nome]
    db.append(resultado)
    save_db(db)

    return jsonify(resultado)

# CRUD - Read
@app.route('/api/historico', methods=['GET'])
def historico():
    return jsonify(get_db())

# CRUD - Delete
@app.route('/api/deletar/<nome>', methods=['DELETE'])
def deletar(nome):
    db = get_db()
    novo_db = [s for s in db if s['nome'] != nome]
    save_db(novo_db)
    return jsonify({"status": "sucesso"})

if __name__ == '__main__':
    app.run(debug=True)