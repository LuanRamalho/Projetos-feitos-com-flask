import json
import os
from flask import Flask, render_template, request, redirect, url_for, send_file
from fpdf import FPDF
from datetime import datetime

app = Flask(__name__)

# Caminhos dos arquivos JSON
DATA_DIR = 'data'
DONATIONS_FILE = os.path.join(DATA_DIR, 'donations.json')
CAMPAIGNS_FILE = os.path.join(DATA_DIR, 'campaigns.json')

# Inicializa arquivos se não existirem
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
for file in [DONATIONS_FILE, CAMPAIGNS_FILE]:
    if not os.path.exists(file):
        with open(file, 'w', encoding='utf-8') as f:
            json.dump([], f)

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    query = request.args.get('search', '').lower()
    donations = load_json(DONATIONS_FILE)
    campaigns = load_json(CAMPAIGNS_FILE)
    
    if query:
        donations = [d for d in donations if query in d['item'].lower()]
        
    return render_template('index.html', donations=donations, campaigns=campaigns, search_query=query)

@app.route('/add_donation', methods=['POST'])
def add_donation():
    donations = load_json(DONATIONS_FILE)
    new_data = {
        "doador": request.form.get('doador'),
        "item": request.form.get('item'),
        "quantidade": request.form.get('quantidade'),
        "data": datetime.now().strftime("%d/%m/%Y"),
        "impacto": request.form.get('impacto')
    }
    donations.append(new_data)
    save_json(DONATIONS_FILE, donations)
    return redirect(url_for('index'))

@app.route('/edit_donation', methods=['POST'])
def edit_donation():
    donations = load_json(DONATIONS_FILE)
    original_item = request.form.get('original_item')
    
    for d in donations:
        if d['item'] == original_item:
            d['doador'] = request.form.get('doador')
            d['item'] = request.form.get('item')
            d['quantidade'] = request.form.get('quantidade')
            d['impacto'] = request.form.get('impacto')
            break
            
    save_json(DONATIONS_FILE, donations)
    return redirect(url_for('index'))

@app.route('/delete_donation/<item_name>')
def delete_donation(item_name):
    donations = load_json(DONATIONS_FILE)
    donations = [d for d in donations if d['item'] != item_name]
    save_json(DONATIONS_FILE, donations)
    return redirect(url_for('index'))

@app.route('/generate_pdf')
def generate_pdf():
    donations = load_json(DONATIONS_FILE)
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 18)
    pdf.cell(190, 15, "Relatorio de Impacto de Doacoes", ln=True, align='C')
    pdf.ln(5)
    
    card_width = 90  # Aumentado levemente para melhor aproveitamento
    card_height = 70 
    margin = 10
    cols = 2
    
    current_x = margin
    current_y = 30 
    
    def clean_txt(t):
        return str(t).encode('latin-1', 'ignore').decode('latin-1')

    for i, d in enumerate(donations):
        # Controle de nova página
        if current_y + card_height > 270:
            pdf.add_page()
            current_y = 20
            current_x = margin

        # Desenhar borda do card
        pdf.set_xy(current_x, current_y)
        pdf.set_draw_color(74, 144, 226)
        pdf.set_line_width(0.5)
        pdf.rect(current_x, current_y, card_width, card_height)
        
        # Título do Item (Com quebra de linha se for muito grande)
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(74, 144, 226)
        pdf.set_xy(current_x + 5, current_y + 5)
        # multi_cell garante que o texto não saia pela direita
        pdf.multi_cell(card_width - 10, 8, f"Item: {clean_txt(d['item'])}", align='L')
        
        # Detalhes (Usando Y relativo para não sobrepor o título quebrado)
        y_offset = pdf.get_y() + 2
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(44, 62, 80)
        
        # Doador
        pdf.set_xy(current_x + 5, y_offset)
        pdf.multi_cell(card_width - 10, 5, f"Doador: {clean_txt(d['doador'])}", align='L')
        
        # Quantidade
        y_offset = pdf.get_y() + 1
        pdf.set_xy(current_x + 5, y_offset)
        pdf.cell(card_width - 10, 5, f"Quantidade: {clean_txt(d['quantidade'])}", ln=True)
        
        # Impacto (Este costuma ser o campo mais longo)
        y_offset = pdf.get_y() + 1
        pdf.set_xy(current_x + 5, y_offset)
        pdf.multi_cell(card_width - 10, 5, f"Impacto: {clean_txt(d['impacto'])}", align='L')
        
        # Data (Fixada ao final do card ou após o impacto)
        pdf.set_xy(current_x + 5, current_y + card_height - 10)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(card_width - 10, 5, f"Data: {clean_txt(d['data'])}", align='R')
        
        # Lógica de posicionamento para o próximo card
        if (i + 1) % cols == 0:
            current_x = margin
            current_y += card_height + margin
        else:
            current_x += card_width + margin
            
    pdf_path = "relatorio_doacoes_ajustado.pdf"
    pdf.output(pdf_path)
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)