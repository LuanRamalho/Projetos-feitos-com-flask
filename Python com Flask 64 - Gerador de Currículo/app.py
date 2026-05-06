from __future__ import annotations

import io
import os
from datetime import datetime
from pathlib import Path
from typing import List

from flask import Flask, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Image as RLImage,
    Table,
    TableStyle,
)

APP_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = APP_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
MAX_UPLOAD_SIZE_MB = 8

app = Flask(__name__)
app.config["SECRET_KEY"] = "curriculo-flask-secret"
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE_MB * 1024 * 1024

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def normalize_lines(text: str) -> List[str]:
    if not text:
        return []
    parts = []
    for line in text.replace("\r", "\n").split("\n"):
        line = line.strip()
        if not line:
            continue
        if "," in line and len(line.split(",")) > 1:
            for item in line.split(","):
                item = item.strip()
                if item:
                    parts.append(item)
        else:
            parts.append(line)
    return parts

def get_resume_styles():
    """Gera e retorna o conjunto de estilos para o currículo."""
    styles = getSampleStyleSheet()
    
    # Estilo do Título Principal (Nome)
    styles.add(ParagraphStyle(
        name="ResumeTitle",
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=2,
    ))
    
    # Estilo do Subtítulo (Cargo)
    styles.add(ParagraphStyle(
        name="ResumeSubTitle",
        fontName="Helvetica",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8,
    ))
    
    # Estilo do Corpo de Texto (Alinhado com o padding das caixas)
    styles.add(ParagraphStyle(
        name="BodyTextResume",
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        leftIndent=12,  # AJUSTE DE ALINHAMENTO
    ))
    
    return styles

def _section_box(title: str) -> Table:
    """Cria a barra roxa de título da seção com 18cm de largura."""
    style = ParagraphStyle(
        name=f"Style_{title}",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=13,
        textColor=colors.white,
    )
    
    t = Table([[Paragraph(title, style)]], colWidths=[18.0 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#7c3aed")),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t

def create_pdf(data: dict, photo_path: str | None) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = get_resume_styles()
    story = []

    # Cabeçalho
    nome = data.get("nome", "") or "Seu Nome"
    cargo = data.get("cargo", "") or "Profissional"
    
    contato_info = []
    for key in ["email", "telefone", "cidade", "linkedin"]:
        if data.get(key):
            contato_info.append(data[key])

    left_content = [
        Paragraph(nome, styles["ResumeTitle"]),
        Paragraph(cargo, styles["ResumeSubTitle"]),
        Paragraph("<br/>".join(contato_info), styles["BodyTextResume"])
    ]

    if photo_path and os.path.exists(photo_path):
        img = RLImage(photo_path, width=3.6*cm, height=4.2*cm)
        header_table = Table([[left_content, img]], colWidths=[14.0 * cm, 4.0 * cm])
    else:
        header_table = Table([[left_content]], colWidths=[18.0 * cm])

    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#e0f2fe")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#38bdf8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))

    story.append(header_table)
    story.append(Spacer(1, 0.4 * cm))

    # Mapeamento de Seções
    sections = [
        ("resumo", "Resumo profissional"),
        ("formacao", "Formação acadêmica"),
        ("habilidades", "Habilidades"),
        ("experiencia", "Experiência profissional")
    ]

    for field, label in sections:
        content = data.get(field, "").strip()
        if content:
            story.append(_section_box(label))
            story.append(Spacer(1, 0.15 * cm))
            
            if field == "resumo":
                text = content.replace("\n", "<br/>")
            else:
                items = normalize_lines(content)
                text = "<br/>".join([f"• {i}" for i in items])
            
            story.append(Paragraph(text, styles["BodyTextResume"]))
            story.append(Spacer(1, 0.4 * cm))

    # Build
    doc.build(story)
    buffer.seek(0)
    return buffer

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = {k: request.form.get(k, "").strip() for k in [
        "nome", "cargo", "email", "telefone", "cidade", 
        "linkedin", "resumo", "formacao", "habilidades", "experiencia"
    ]}

    photo_file = request.files.get("foto")
    photo_path = None

    if photo_file and photo_file.filename and allowed_file(photo_file.filename):
        filename = secure_filename(f"{datetime.now().timestamp()}_{photo_file.filename}")
        photo_path = str(UPLOAD_DIR / filename)
        photo_file.save(photo_path)

    pdf_buffer = create_pdf(data, photo_path)

    if photo_path and os.path.exists(photo_path):
        os.remove(photo_path)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"curriculo_{secure_filename(data['nome'] or 'doc')}.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(debug=True)