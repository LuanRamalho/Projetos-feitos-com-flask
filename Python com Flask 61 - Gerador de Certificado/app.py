import os
import json
import io
from datetime import datetime
from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import cm
from reportlab.lib import colors

app = Flask(__name__)

DB_FILE = 'database.json'

def salvar_registro(nome, curso):
    registro = {
        "nome": nome,
        "curso": curso,
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

@app.route('/gerar', methods=['POST'])
def gerar():
    nome = request.form.get('nome')
    curso = request.form.get('curso')
    data_raw = request.form.get('data')

    # Conversão para o padrão DD/MM/YYYY
    try:
        data_obj = datetime.strptime(data_raw, '%Y-%m-%d')
        data_formatada = data_obj.strftime('%d/%m/%Y')
    except:
        data_formatada = data_raw

    salvar_registro(nome, curso)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    largura, altura = landscape(A4)

    # --- FUNDO ---
    # Borda azul escura
    c.setFillColor(colors.HexColor("#2C3E50"))
    c.rect(0, 0, largura, altura, fill=1, stroke=0)

    # Papel interno branco
    c.setFillColor(colors.HexColor("#FFFFFF"))
    margem = 1.2 * cm
    c.rect(margem, margem, largura - (2 * margem), altura - (2 * margem), fill=1, stroke=0)

    # --- CONTEÚDO ---
    
    # Título
    c.setFont("Helvetica-Bold", 35)
    c.setFillColor(colors.HexColor("#2980B9"))
    c.drawCentredString(largura/2, altura - 4.5 * cm, "CERTIFICADO DE CONCLUSÃO")

    # Texto 1
    c.setFont("Helvetica", 20)
    c.setFillColor(colors.HexColor("#34495E"))
    c.drawCentredString(largura/2, altura - 7.5 * cm, "Certificamos que")

    # Nome do Aluno
    c.setFont("Helvetica-Bold", 42)
    c.setFillColor(colors.HexColor("#16A085"))
    c.drawCentredString(largura/2, altura - 10 * cm, nome.upper())

    # Texto 2
    c.setFont("Helvetica", 20)
    c.setFillColor(colors.HexColor("#34495E"))
    c.drawCentredString(largura/2, altura - 12.5 * cm, "concluiu com êxito o curso de")

    # Nome do Curso (Posição Superior Central)
    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(colors.HexColor("#8E44AD"))
    c.drawCentredString(largura/2, altura - 14.5 * cm, curso.upper())

    # --- ÁREA DA ASSINATURA (ESPACIAMENTO REVISADO) ---
    # Definimos uma altura fixa para a assinatura bem abaixo do curso
    # O curso está em aproximadamente 14.5cm do topo, a assinatura fica agora a 4.5cm da base
    y_assinatura = 4.5 * cm 

    c.setStrokeColor(colors.HexColor("#BDC3C7"))
    c.setLineWidth(1)
    # Linha de assinatura
    c.line(largura/2 - 4*cm, y_assinatura + 0.6 * cm, largura/2 + 4*cm, y_assinatura + 0.6 * cm)
    
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#7F8C8D"))
    c.drawCentredString(largura/2, y_assinatura, "ASSINATURA DA INSTITUIÇÃO")

    # Data de Emissão (Rodapé final)
    c.setFont("Helvetica", 12)
    c.drawCentredString(largura/2, 2.2 * cm, f"Emitido em: {data_formatada}")

    c.showPage()
    c.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"Certificado_{nome.replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(debug=True)