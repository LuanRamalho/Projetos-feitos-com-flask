from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

import requests
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

app = Flask(__name__)
app.secret_key = "troque-esta-chave-em-producao"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "musicas.json"
DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)


@dataclass
class Musica:
    id: int
    nome: str
    autor: str
    link: str
    criado_em: str


def carregar_musicas() -> List[Musica]:
    if not DB_PATH.exists():
        salvar_musicas([])
        return []

    try:
        with DB_PATH.open("r", encoding="utf-8") as f:
            dados = json.load(f)
        return [Musica(**item) for item in dados]
    except (json.JSONDecodeError, TypeError, KeyError):
        return []


def salvar_musicas(musicas: List[Musica]) -> None:
    with DB_PATH.open("w", encoding="utf-8") as f:
        json.dump([asdict(m) for m in musicas], f, ensure_ascii=False, indent=4)


def proximo_id(musicas: List[Musica]) -> int:
    return max((m.id for m in musicas), default=0) + 1


def buscar_musica_por_id(musicas: List[Musica], musica_id: int) -> Optional[Musica]:
    return next((m for m in musicas if m.id == musica_id), None)


def filtrar_musicas(musicas: List[Musica], termo: str) -> List[Musica]:
    termo = termo.strip().lower()
    if not termo:
        return musicas
    return [
        m for m in musicas
        if termo in m.nome.lower() or termo in m.autor.lower()
    ]


def nome_arquivo_seguro(texto: str) -> str:
    return (
        texto.strip()
        .replace("/", "-")
        .replace("\\", "-")
        .replace(":", "-")
        .replace("*", "")
        .replace("?", "")
        .replace('"', "")
        .replace("<", "")
        .replace(">", "")
        .replace("|", "")
    )


@app.route("/")
def index():
    musicas = carregar_musicas()
    termo = request.args.get("q", "").strip()
    musicas_filtradas = filtrar_musicas(musicas, termo)
    return render_template(
        "index.html",
        musicas=musicas_filtradas,
        termo=termo,
    )


@app.route("/salvar", methods=["POST"])
def salvar():
    musicas = carregar_musicas()

    musica_id = request.form.get("id", "").strip()
    nome = request.form.get("nome", "").strip()
    autor = request.form.get("autor", "").strip()
    link = request.form.get("link", "").strip()

    if not nome or not autor or not link:
        flash("Preencha todos os campos.")
        return redirect(url_for("index"))

    if musica_id:
        musica = buscar_musica_por_id(musicas, int(musica_id))
        if not musica:
            flash("Música não encontrada para edição.")
            return redirect(url_for("index"))

        musica.nome = nome
        musica.autor = autor
        musica.link = link
        flash("Música atualizada com sucesso.")
    else:
        nova = Musica(
            id=proximo_id(musicas),
            nome=nome,
            autor=autor,
            link=link,
            criado_em=datetime.now().isoformat(timespec="seconds"),
        )
        musicas.append(nova)
        flash("Música adicionada com sucesso.")

    salvar_musicas(musicas)
    return redirect(url_for("index"))


@app.route("/editar/<int:musica_id>")
def editar(musica_id: int):
    musicas = carregar_musicas()
    musica = buscar_musica_por_id(musicas, musica_id)
    if not musica:
        abort(404)

    termo = request.args.get("q", "").strip()
    musicas_filtradas = filtrar_musicas(musicas, termo)
    return render_template(
        "index.html",
        musicas=musicas_filtradas,
        termo=termo,
        musica_edicao=musica,
    )


@app.route("/excluir/<int:musica_id>")
def excluir(musica_id: int):
    musicas = carregar_musicas()
    musica = buscar_musica_por_id(musicas, musica_id)
    if not musica:
        abort(404)

    musicas = [m for m in musicas if m.id != musica_id]
    salvar_musicas(musicas)
    flash("Música excluída com sucesso.")
    return redirect(url_for("index"))


@app.route("/baixar/<int:musica_id>")
def baixar(musica_id: int):
    musicas = carregar_musicas()
    musica = buscar_musica_por_id(musicas, musica_id)
    if not musica:
        abort(404)

    url_audio = musica.link.strip()
    nome_base = nome_arquivo_seguro(f"{musica.autor} - {musica.nome}")

    try:
        with requests.get(url_audio, stream=True, timeout=20) as resposta:
            resposta.raise_for_status()

            caminho = urlparse(url_audio).path.lower()
            extensao = ".mp3"
            for ext in [".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac", ".mp4"]:
                if caminho.endswith(ext):
                    extensao = ext
                    break

            destino = DOWNLOAD_DIR / f"{musica.id}_{nome_base}{extensao}"
            with destino.open("wb") as f:
                for chunk in resposta.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        return send_file(destino, as_attachment=True, download_name=destino.name)
    except Exception:
        flash("Não foi possível baixar automaticamente. Use um link direto de áudio.")
        return redirect(url_for("index"))


@app.errorhandler(404)
def nao_encontrado(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    if not DB_PATH.exists():
        salvar_musicas([])
    app.run(debug=True)
