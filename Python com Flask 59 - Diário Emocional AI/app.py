from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from flask import Flask, flash, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ENTRIES_FILE = DATA_DIR / "entries.json"

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "emotion-diary-secret-key")

# Optional Hugging Face pipeline. The app still works with a local fallback.
_SENTIMENT_PIPELINE = None


def ensure_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not ENTRIES_FILE.exists():
        demo_entries = [
            {
                "id": str(uuid4()),
                "created_at": "2026-04-15 09:10",
                "title": "Voltei a estudar Flask",
                "text": "Hoje consegui corrigir um bug e isso me deixou animado.",
                "sentiment_label": "positive",
                "sentiment_score": 0.96,
                "emotion_label": "joy",
                "text_category": "emoção",
                "keywords": ["bug", "animado"],
            },
            {
                "id": str(uuid4()),
                "created_at": "2026-04-16 20:40",
                "title": "Dia pesado",
                "text": "Passei o dia cansado e um pouco irritado, mas consegui terminar uma tarefa.",
                "sentiment_label": "negative",
                "sentiment_score": 0.71,
                "emotion_label": "sadness",
                "text_category": "emoção",
                "keywords": ["cansado", "irritado"],
            },
            {
                "id": str(uuid4()),
                "created_at": "2026-04-17 14:20",
                "title": "Mensagem estranha",
                "text": "Ganhe dinheiro rápido clicando neste link!",
                "sentiment_label": "negative",
                "sentiment_score": 0.84,
                "emotion_label": "anger",
                "text_category": "spam",
                "keywords": ["dinheiro", "link"],
            },
        ]
        save_entries(demo_entries)


def load_entries() -> List[Dict[str, Any]]:
    ensure_storage()
    try:
        with open(ENTRIES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_entries(entries: List[Dict[str, Any]]) -> None:
    ensure_storage()
    with open(ENTRIES_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def try_load_pipeline():
    global _SENTIMENT_PIPELINE
    if _SENTIMENT_PIPELINE is not None:
        return _SENTIMENT_PIPELINE
    try:
        from transformers import pipeline

        _SENTIMENT_PIPELINE = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
        )
    except Exception:
        _SENTIMENT_PIPELINE = False
    return _SENTIMENT_PIPELINE


def analyze_sentiment(text: str) -> Dict[str, Any]:
    pipeline_obj = try_load_pipeline()
    if pipeline_obj:
        try:
            result = pipeline_obj(text[:512])[0]
            label = str(result.get("label", "")).upper()
            score = float(result.get("score", 0.0))
            sentiment_label = "positive" if "POS" in label else "negative"
            emotion_label = "joy" if sentiment_label == "positive" else "sadness"
            return {
                "sentiment_label": sentiment_label,
                "sentiment_score": round(score, 3),
                "emotion_label": emotion_label,
            }
        except Exception:
            pass

    positive_words = {
        "feliz", "feliz", "animado", "bom", "ótimo", "otimo", "amando", "consegui",
        "sucesso", "leve", "tranquilo", "grato", "gratidão", "grato", "empolgado",
    }
    negative_words = {
        "triste", "cansado", "irritado", "raiva", "estresse", "estressado", "ansioso",
        "medo", "ruim", "péssimo", "pessimo", "frustrado", "deprimido", "chorar",
    }
    text_low = text.lower()
    pos = sum(1 for word in positive_words if word in text_low)
    neg = sum(1 for word in negative_words if word in text_low)
    if pos > neg:
        return {"sentiment_label": "positive", "sentiment_score": round(min(0.55 + pos * 0.1, 0.99), 3), "emotion_label": "joy"}
    if neg > pos:
        return {"sentiment_label": "negative", "sentiment_score": round(min(0.55 + neg * 0.1, 0.99), 3), "emotion_label": "sadness"}
    return {"sentiment_label": "neutral", "sentiment_score": 0.5, "emotion_label": "neutral"}


def classify_text(text: str) -> Dict[str, Any]:
    text_low = text.lower()
    spam_terms = ["grátis", "gratis", "clique", "ganhe dinheiro", "pix", "promoção", "promocao", "oferta", "http://", "https://", "link"]
    support_terms = ["ajuda", "erro", "bug", "suporte", "não funciona", "nao funciona", "problema", "falha"]
    emotion_terms = ["triste", "feliz", "ansioso", "cansado", "irritado", "raiva", "medo", "grato", "animado"]

    spam_hits = sum(1 for term in spam_terms if term in text_low)
    support_hits = sum(1 for term in support_terms if term in text_low)
    emotion_hits = sum(1 for term in emotion_terms if term in text_low)

    if spam_hits > max(support_hits, emotion_hits):
        return {"text_category": "spam", "keywords": [term for term in spam_terms if term in text_low][:4]}
    if support_hits > max(spam_hits, emotion_hits):
        return {"text_category": "suporte", "keywords": [term for term in support_terms if term in text_low][:4]}
    if emotion_hits > 0:
        return {"text_category": "emoção", "keywords": [term for term in emotion_terms if term in text_low][:4]}
    return {"text_category": "neutro", "keywords": []}


def extract_words(text: str) -> List[str]:
    words = re.findall(r"[A-Za-zÀ-ÿ0-9']+", text.lower())
    stop = {"a", "o", "e", "de", "da", "do", "das", "dos", "um", "uma", "para", "com", "que", "em", "no", "na", "nos", "nas", "eu", "me", "minha", "meu", "hoje", "ontem", "dia"}
    return [w for w in words if len(w) > 2 and w not in stop]


def top_keywords(entries: List[Dict[str, Any]], limit: int = 6) -> List[str]:
    from collections import Counter

    counter = Counter()
    for entry in entries:
        counter.update(entry.get("keywords", []))
        counter.update(extract_words(entry.get("text", "")))
    return [word for word, _ in counter.most_common(limit)]


def build_stats(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(entries)
    positives = sum(1 for e in entries if e.get("sentiment_label") == "positive")
    negatives = sum(1 for e in entries if e.get("sentiment_label") == "negative")
    neutrals = sum(1 for e in entries if e.get("sentiment_label") == "neutral")
    avg_score = round(sum(float(e.get("sentiment_score", 0)) for e in entries) / total, 3) if total else 0.0

    recent = sorted(entries, key=lambda e: e.get("created_at", ""), reverse=True)[:7]
    score_map = {"positive": 1, "neutral": 0, "negative": -1}
    recent_labels = [score_map.get(e.get("sentiment_label"), 0) for e in reversed(recent)]
    recent_dates = [e.get("created_at", "")[:10] for e in reversed(recent)]

    by_category: Dict[str, int] = {}
    for entry in entries:
        by_category[entry.get("text_category", "neutro")] = by_category.get(entry.get("text_category", "neutro"), 0) + 1

    best_entry = None
    worst_entry = None
    if entries:
        best_entry = max(entries, key=lambda e: float(e.get("sentiment_score", 0)))
        worst_entry = min(entries, key=lambda e: float(e.get("sentiment_score", 0)))

    return {
        "total": total,
        "positives": positives,
        "negatives": negatives,
        "neutrals": neutrals,
        "avg_score": avg_score,
        "recent_dates": recent_dates,
        "recent_labels": recent_labels,
        "by_category": by_category,
        "top_keywords": top_keywords(entries),
        "best_entry": best_entry,
        "worst_entry": worst_entry,
    }


def chat_answer(question: str, entries: List[Dict[str, Any]]) -> str:
    q = question.lower().strip()
    if not q:
        return "Escreva uma pergunta para eu analisar seu histórico emocional."

    if not entries:
        return "Ainda não há registros no diário. Adicione algumas entradas para eu aprender seu padrão emocional."

    stats = build_stats(entries)
    positives = stats["positives"]
    negatives = stats["negatives"]
    total = stats["total"]
    recent = sorted(entries, key=lambda e: e.get("created_at", ""), reverse=True)[:7]

    if any(k in q for k in ["como estou", "como tenho", "resumo", "me senti", "humor"]):
        ratio = round(positives / total * 100)
        neg_ratio = round(negatives / total * 100)
        return (
            f"Pelo seu histórico, você registrou {ratio}% de entradas positivas e {neg_ratio}% negativas. "
            f"Nos últimos dias, o padrão mais comum foi: {', '.join([e.get('sentiment_label', 'neutral') for e in recent[:3]]) or 'sem dados'} ."
        )

    if any(k in q for k in ["melhor dia", "mais feliz", "melhor momento", "melhor entrada"]):
        best = stats["best_entry"]
        if best:
            return f"Seu melhor registro foi '{best.get('title', 'Sem título')}', em {best.get('created_at', '')}, com sentimento {best.get('sentiment_label', 'neutral')} ({best.get('emotion_label', 'neutral')})."

    if any(k in q for k in ["pior dia", "mais triste", "mais pesado", "pior entrada"]):
        worst = stats["worst_entry"]
        if worst:
            return f"Seu registro mais pesado foi '{worst.get('title', 'Sem título')}', em {worst.get('created_at', '')}. Ele foi classificado como {worst.get('sentiment_label', 'neutral')} ({worst.get('emotion_label', 'neutral')})."

    keywords = top_keywords(entries)
    if any(word in q for word in keywords):
        matched = [e for e in entries if any(k in (e.get('text', '').lower() + ' ' + e.get('title', '').lower()) for k in q.split())]
        if matched:
            latest = matched[-1]
            return f"Encontrei relação com seus dados. O último registro semelhante foi '{latest.get('title', 'Sem título')}' em {latest.get('created_at', '')}."

    if any(k in q for k in ["spam", "link", "promoção", "promocao"]):
        spam_count = sum(1 for e in entries if e.get("text_category") == "spam")
        return f"Você tem {spam_count} registros classificados como spam. Posso ajudar a filtrar esse tipo de texto rapidamente."

    return (
        "Eu não sou um modelo treinado por fine-tuning aqui, mas consigo ler seu diário e responder com base nos registros. "
        f"No momento, seus temas mais frequentes são: {', '.join(stats['top_keywords']) if stats['top_keywords'] else 'ainda não há palavras dominantes'} ."
    )


def get_entry(entry_id: str) -> Optional[Dict[str, Any]]:
    for entry in load_entries():
        if entry.get("id") == entry_id:
            return entry
    return None


@app.route("/", methods=["GET", "POST"])
def index():
    entries = sorted(load_entries(), key=lambda e: e.get("created_at", ""), reverse=True)
    if request.method == "POST":
        title = request.form.get("title", "").strip() or "Sem título"
        text = request.form.get("text", "").strip()
        if not text:
            flash("Escreva um texto para registrar.", "danger")
            return redirect(url_for("index"))

        sentiment = analyze_sentiment(text)
        classification = classify_text(text)
        new_entry = {
            "id": str(uuid4()),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "title": title,
            "text": text,
            **sentiment,
            **classification,
        }
        entries.append(new_entry)
        save_entries(entries)
        flash("Registro salvo com sucesso.", "success")
        return redirect(url_for("index"))

    stats = build_stats(entries)
    return render_template("index.html", entries=entries[:5], stats=stats)


@app.route("/history")
def history():
    entries = sorted(load_entries(), key=lambda e: e.get("created_at", ""), reverse=True)
    query = request.args.get("q", "").strip().lower()
    filter_type = request.args.get("filter", "all")

    if query:
        entries = [e for e in entries if query in e.get("title", "").lower() or query in e.get("text", "").lower()]
    if filter_type in {"positive", "negative", "neutral"}:
        entries = [e for e in entries if e.get("sentiment_label") == filter_type]

    return render_template("history.html", entries=entries, query=query, filter_type=filter_type)


@app.route("/entry/<entry_id>/edit", methods=["GET", "POST"])
def edit_entry(entry_id: str):
    entries = load_entries()
    entry = next((e for e in entries if e.get("id") == entry_id), None)
    if not entry:
        flash("Registro não encontrado.", "danger")
        return redirect(url_for("history"))

    if request.method == "POST":
        title = request.form.get("title", "").strip() or "Sem título"
        text = request.form.get("text", "").strip()
        if not text:
            flash("O texto não pode ficar vazio.", "danger")
            return redirect(url_for("edit_entry", entry_id=entry_id))

        sentiment = analyze_sentiment(text)
        classification = classify_text(text)
        entry.update({
            "title": title,
            "text": text,
            **sentiment,
            **classification,
        })
        save_entries(entries)
        flash("Registro atualizado.", "success")
        return redirect(url_for("history"))

    return render_template("edit.html", entry=entry)


@app.route("/entry/<entry_id>/delete", methods=["POST"])
def delete_entry(entry_id: str):
    entries = load_entries()
    entries = [e for e in entries if e.get("id") != entry_id]
    save_entries(entries)
    flash("Registro removido.", "warning")
    return redirect(url_for("history"))


@app.route("/classifier", methods=["GET", "POST"])
def classifier_view():
    result = None
    sample_text = ""
    if request.method == "POST":
        sample_text = request.form.get("sample_text", "").strip()
        if sample_text:
            result = {
                **analyze_sentiment(sample_text),
                **classify_text(sample_text),
            }
        else:
            flash("Digite um texto para classificar.", "danger")
    return render_template("classifier.html", result=result, sample_text=sample_text)


@app.route("/chat", methods=["GET", "POST"])
def chat():
    entries = load_entries()
    answer = None
    question = ""
    if request.method == "POST":
        question = request.form.get("question", "").strip()
        if question:
            answer = chat_answer(question, entries)
        else:
            flash("Digite uma pergunta.", "danger")
    stats = build_stats(entries)
    return render_template("chat.html", answer=answer, question=question, stats=stats)


@app.context_processor
def inject_year():
    return {"current_year": datetime.now().year}


if __name__ == "__main__":
    ensure_storage()
    app.run(debug=True)
