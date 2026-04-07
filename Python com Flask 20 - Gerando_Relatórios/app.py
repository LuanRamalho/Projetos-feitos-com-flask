from flask import Flask, render_template, request, redirect, url_for, send_file
import json
import os
import pandas as pd
from fpdf import FPDF
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'data.json'

# Inicializa o JSON se não existir
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    # Adicione o encoding='utf-8' aqui
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    # Adicione o encoding='utf-8' e ensure_ascii=False aqui
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    services = load_data()
    return render_template('index.html', services=services)

@app.route('/add', methods=['POST'])
def add_service():
    services = load_data()
    new_service = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "nome": request.form['nome'],
        "categoria": request.form['categoria'],
        "preco": request.form['preco'],
        "data": request.form['data']
    }
    services.append(new_service)
    save_data(services)
    return redirect(url_for('index'))

@app.route('/edit/<id>')
def edit_service(id):
    services = load_data()
    # Busca o serviço para preencher o formulário
    service_to_edit = next((s for s in services if s['id'] == id), None)
    return render_template('index.html', services=services, edit_item=service_to_edit)

@app.route('/update/<id>', methods=['POST'])
def update_service(id):
    services = load_data()
    for s in services:
        if s['id'] == id:
            s['nome'] = request.form['nome']
            s['categoria'] = request.form['categoria']
            s['preco'] = request.form['preco']
            s['data'] = request.form['data']
            break
    save_data(services)
    return redirect(url_for('index'))

@app.route('/delete/<id>')
def delete_service(id):
    services = load_data()
    services = [s for s in services if s['id'] != id]
    save_data(services)
    return redirect(url_for('index'))

@app.route('/report')
def report():
    services = load_data()
    return render_template('report.html', services=services)

@app.route('/export/<format>')
def export(format):
    services = load_data()
    if not services:
        return redirect(url_for('report'))

    # Para CSV e Excel, mantemos a estrutura de tabela com Pandas
    df = pd.DataFrame(services).drop(columns=['id'])
    df.columns = ['Nome do Serviço', 'Categoria', 'Preço (R$)', 'Data']

    if format == 'csv':
        file_path = 'relatorio.csv'
        # Adicionamos 'sep=";"' para o Excel brasileiro entender as colunas
        df.to_csv(file_path, index=False, sep=';', encoding='utf-8-sig')
    
    elif format == 'excel':
        file_path = 'relatorio.xlsx'
        df.to_excel(file_path, index=False)

    elif format == 'pdf':
        file_path = 'relatorio.pdf'
        pdf = FPDF()
        pdf.add_page()
        
        # Título do Documento
        pdf.set_font("Arial", 'B', 20)
        pdf.cell(0, 15, "RELATÓRIO GERAL DE SERVIÇOS", ln=True, align='C')
        pdf.set_draw_color(108, 92, 231) # Cor roxa do seu design
        pdf.line(10, 25, 200, 25)
        pdf.ln(10)

        # Listagem em formato de documento corrido
        for s in services:
            # Nome do Serviço em destaque
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(108, 92, 231)
            pdf.multi_cell(0, 8, f"SERVIÇO: {s['nome'].upper()}")
            
            # Detalhes do serviço
            pdf.set_font("Arial", '', 11)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 7, f"Categoria: {s['categoria']}", ln=True)
            pdf.cell(0, 7, f"Data da Realização: {s['data']}", ln=True)
            
            # Preço em negrito
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 7, f"Valor Total: R$ {s['preco']}", ln=True)
            
            # Linha separadora discreta entre itens
            pdf.set_draw_color(230, 230, 230)
            pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
            pdf.ln(8)

        pdf.output(file_path)

    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)