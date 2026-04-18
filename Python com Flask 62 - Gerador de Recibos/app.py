import os
import json
import io
from datetime import datetime
from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors

app = Flask(__name__)

DB_FILE = 'recibos.json'

def salvar_recibo(pagador, valor, referencia):
    """Salva o log de emissão do recibo em JSON."""
    registro = {
        "id_recibo": datetime.now().strftime("%Y%m%d%H%M%S"),
        "pagador": pagador,
        "valor": valor,
        "referencia": referencia,
        "data_emissao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    dados = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            try:
                dados = json.load(f)
            except json.JSONDecodeError:
                pass
                
    dados.append(registro)
    
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gerar_recibo', methods=['POST'])
def gerar_recibo():
    pagador = request.form.get('pagador')
    valor = request.form.get('valor')
    referencia = request.form.get('referencia')
    data_raw = request.form.get('data')

    try:
        data_obj = datetime.strptime(data_raw, '%Y-%m-%d')
        data_formatada = data_obj.strftime('%d/%m/%Y')
    except:
        data_formatada = data_raw

    # Salva no banco NoSQL em JSON
    salvar_recibo(pagador, valor, referencia)

    # Prepara o PDF (Modo Retrato/Portrait em A4)
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    numero_recibo = datetime.now().strftime("%Y%m%d-%H%M")

    # --- DESIGN DO RECIBO (Cores Flat Modernas) ---
    
    # Bloco superior (Header Azul Escuro)
    c.setFillColor(colors.HexColor("#2C3E50"))
    c.rect(0, altura - 4*cm, largura, 4*cm, fill=1, stroke=0)

    # Título do Header
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(colors.white)
    c.drawString(2*cm, altura - 2.2*cm, "RECIBO DE PAGAMENTO")

    # Número do Recibo no Header
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.HexColor("#BDC3C7"))
    c.drawRightString(largura - 2*cm, altura - 2.2*cm, f"Nº {numero_recibo}")

    # --- CORPO DO RECIBO ---
    y_pos = altura - 6*cm

    # Caixa de Valor Destaque (Verde Flat)
    c.setFillColor(colors.HexColor("#16A085"))
    c.rect(largura - 7*cm, y_pos, 5*cm, 1.5*cm, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.white)
    c.drawCentredString(largura - 4.5*cm, y_pos + 0.4*cm, f"R$ {valor}")

    # Textos do Corpo
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.HexColor("#34495E"))
    c.drawString(2*cm, y_pos + 0.5*cm, "Recebemos de:")
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, y_pos - 0.5*cm, pagador.upper())

    c.setFont("Helvetica", 14)
    c.drawString(2*cm, y_pos - 2.5*cm, "A quantia de:")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, y_pos - 3.2*cm, f"R$ {valor} (Valor documentado acima)")

    c.setFont("Helvetica", 14)
    c.drawString(2*cm, y_pos - 5*cm, "Referente a:")
    
    # Texto descritivo (Pode ser longo, quebrando em linhas simples)
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#8E44AD")) # Roxo Flat para a referência
    c.drawString(2*cm, y_pos - 5.7*cm, referencia)

    # --- ÁREA DA ASSINATURA ---
    y_assinatura = y_pos - 10*cm

    c.setFont("Helvetica", 12)
    c.setFillColor(colors.HexColor("#7F8C8D"))
    c.drawString(2*cm, y_assinatura + 1*cm, f"Emitido em: {data_formatada}")

    c.setStrokeColor(colors.HexColor("#BDC3C7"))
    c.setLineWidth(1)
    c.line(largura - 9*cm, y_assinatura + 0.5*cm, largura - 2*cm, y_assinatura + 0.5*cm)
    
    c.setFont("Helvetica", 10)
    c.drawCentredString(largura - 5.5*cm, y_assinatura, "ASSINATURA DO EMISSOR")

    # Rodapé de autenticidade
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.HexColor("#95A5A6"))
    c.drawString(2*cm, 2*cm, f"Documento gerado automaticamente pelo sistema. ID: {numero_recibo}")

    c.showPage()
    c.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"Recibo_{pagador.replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(debug=True)