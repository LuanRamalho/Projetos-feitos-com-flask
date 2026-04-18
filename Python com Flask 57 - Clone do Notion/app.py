from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for

APP_DIR = Path(__file__).resolve().parent
USERS_DB = APP_DIR / "users.json"
PAGES_DB = APP_DIR / "pages.json"

app = Flask(__name__)
app.secret_key = "notion_clone_level_2_secret_key"


# -----------------------------
# JSON storage helpers
# -----------------------------
def ensure_file(path: Path, default: Any) -> None:
    if not path.exists():
        path.write_text(json.dumps(default, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path, default: Any):
    ensure_file(path, default)
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        path.write_text(json.dumps(default, ensure_ascii=False, indent=2), encoding="utf-8")
        return default


def save_json(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_users() -> Dict[str, str]:
    return load_json(USERS_DB, {})


def save_users(users: Dict[str, str]) -> None:
    save_json(USERS_DB, users)


def get_pages() -> Dict[str, List[dict]]:
    return load_json(PAGES_DB, {})


def save_pages(pages: Dict[str, List[dict]]) -> None:
    save_json(PAGES_DB, pages)


def current_user() -> str | None:
    return session.get("user")


def require_login():
    if not current_user():
        return redirect(url_for("login"))
    return None


def user_pages(username: str) -> List[dict]:
    pages = get_pages()
    return pages.get(username, [])


def save_user_pages(username: str, pages_list: List[dict]) -> None:
    pages = get_pages()
    pages[username] = pages_list
    save_pages(pages)


def get_page_or_404(username: str, page_id: int) -> dict | None:
    pages = user_pages(username)
    for page in pages:
        if page["id"] == page_id:
            return page
    return None


def next_page_id(username: str) -> int:
    pages = user_pages(username)
    if not pages:
        return 1
    return max(page["id"] for page in pages) + 1


def next_block_id(page: dict) -> int:
    blocks = page.get("blocks", [])
    if not blocks:
        return 1
    return max(block["id"] for block in blocks) + 1


# -----------------------------
# Authentication
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        users = get_users()
        if username in users and users[username] == password:
            session["user"] = username
            flash("Login realizado com sucesso.", "success")
            return redirect(url_for("dashboard"))

        flash("Usuário ou senha inválidos.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if len(username) < 3:
            flash("O usuário precisa ter pelo menos 3 caracteres.", "error")
            return redirect(url_for("register"))
        if len(password) < 3:
            flash("A senha precisa ter pelo menos 3 caracteres.", "error")
            return redirect(url_for("register"))

        users = get_users()
        if username in users:
            flash("Esse usuário já existe.", "error")
            return redirect(url_for("register"))

        users[username] = password
        save_users(users)
        save_user_pages(username, [])

        flash("Cadastro realizado com sucesso.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    recovered = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        users = get_users()
        if username in users:
            recovered = {"username": username, "password": users[username]}
        else:
            flash("Usuário não encontrado.", "error")

    return render_template("forgot.html", recovered=recovered)


@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da conta.", "success")
    return redirect(url_for("login"))


# -----------------------------
# Dashboard
# -----------------------------
@app.route("/dashboard")
def dashboard():
    denied = require_login()
    if denied:
        return denied

    username = current_user()
    pages = sorted(user_pages(username), key=lambda p: p["updated_at"], reverse=True)
    return render_template("dashboard.html", pages=pages, user=username)


@app.route("/search")
def search():
    denied = require_login()
    if denied:
        return jsonify({"results": []}), 401

    query = request.args.get("q", "").strip().lower()
    pages = user_pages(current_user())

    if not query:
        results = pages
    else:
        results = []
        for page in pages:
            page_match = query in page["title"].lower()
            block_match = any(query in block.get("text", "").lower() for block in page.get("blocks", []))
            if page_match or block_match:
                results.append(page)

    results = sorted(results, key=lambda p: p["updated_at"], reverse=True)
    payload = [
        {
            "id": page["id"],
            "title": page["title"],
            "updated_at": page["updated_at"],
            "block_count": len(page.get("blocks", [])),
        }
        for page in results
    ]
    return jsonify({"results": payload})


# -----------------------------
# Pages CRUD
# -----------------------------
@app.route("/page/new", methods=["GET", "POST"])
def new_page():
    denied = require_login()
    if denied:
        return denied

    if request.method == "POST":
        title = request.form.get("title", "").strip() or "Nova página"
        username = current_user()
        pages = user_pages(username)

        page = {
            "id": next_page_id(username),
            "title": title,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "blocks": [
                {
                    "id": 1,
                    "type": "paragraph",
                    "text": "Comece a escrever aqui.",
                    "checked": False,
                }
            ],
        }
        pages.insert(0, page)
        save_user_pages(username, pages)
        flash("Página criada.", "success")
        return redirect(url_for("edit_page", page_id=page["id"]))

    return render_template("page_new.html")


@app.route("/page/<int:page_id>", methods=["GET", "POST"])
def edit_page(page_id: int):
    denied = require_login()
    if denied:
        return denied

    username = current_user()
    pages = user_pages(username)
    page_index = next((i for i, p in enumerate(pages) if p["id"] == page_id), None)
    if page_index is None:
        flash("Página não encontrada.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "save_title":
            return save_page_title(page_id, pages, page_index, username)

        if action == "add_block":
            return add_block_to_page(page_id, pages, page_index, username)

        if action == "delete_block":
            return delete_block_from_page(page_id, pages, page_index, username)

    return render_template("page_editor.html", page=pages[page_index], user=username, block_label=block_label)


@app.route("/page/<int:page_id>/title", methods=["POST"])
def save_page_title(page_id: int, pages=None, page_index=None, username=None):
    denied = require_login()
    if denied:
        return denied

    username = username or current_user()
    pages = pages or user_pages(username)
    page_index = page_index if page_index is not None else next((i for i, p in enumerate(pages) if p["id"] == page_id), None)
    if page_index is None:
        flash("Página não encontrada.", "error")
        return redirect(url_for("dashboard"))

    title = request.form.get("title", "").strip()
    if title:
        pages[page_index]["title"] = title
        pages[page_index]["updated_at"] = now_iso()
        save_user_pages(username, pages)
        flash("Título atualizado.", "success")

    return redirect(url_for("edit_page", page_id=page_id))


@app.route("/page/<int:page_id>/blocks", methods=["POST"])
def add_block_to_page(page_id: int, pages=None, page_index=None, username=None):
    denied = require_login()
    if denied:
        return denied

    username = username or current_user()
    pages = pages or user_pages(username)
    page_index = page_index if page_index is not None else next((i for i, p in enumerate(pages) if p["id"] == page_id), None)
    if page_index is None:
        flash("Página não encontrada.", "error")
        return redirect(url_for("dashboard"))

    block_type = request.form.get("block_type", "paragraph")
    text = request.form.get("text", "").strip()

    new_block = {
        "id": next_block_id(pages[page_index]),
        "type": block_type,
        "text": text or block_label(block_type),
        "checked": False,
    }
    if block_type == "todo":
        new_block["checked"] = bool(request.form.get("checked"))

    pages[page_index].setdefault("blocks", []).append(new_block)
    pages[page_index]["updated_at"] = now_iso()
    save_user_pages(username, pages)
    flash("Bloco adicionado.", "success")
    return redirect(url_for("edit_page", page_id=page_id))


@app.route("/page/<int:page_id>/block/<int:block_id>/save", methods=["POST"])
def save_block(page_id: int, block_id: int):
    denied = require_login()
    if denied:
        return denied

    username = current_user()
    pages = user_pages(username)
    page_index = next((i for i, p in enumerate(pages) if p["id"] == page_id), None)
    if page_index is None:
        flash("Página não encontrada.", "error")
        return redirect(url_for("dashboard"))

    block = next((b for b in pages[page_index].get("blocks", []) if b["id"] == block_id), None)
    if block is None:
        flash("Bloco não encontrado.", "error")
        return redirect(url_for("edit_page", page_id=page_id))

    block["type"] = request.form.get("block_type", block["type"])
    block["text"] = request.form.get("text", "").strip()
    if block["type"] == "todo":
        block["checked"] = bool(request.form.get("checked"))
    else:
        block["checked"] = False

    pages[page_index]["updated_at"] = now_iso()
    save_user_pages(username, pages)
    flash("Bloco salvo.", "success")
    return redirect(url_for("edit_page", page_id=page_id))


@app.route("/page/<int:page_id>/block/<int:block_id>/delete", methods=["POST"])
def delete_block(page_id: int, block_id: int):
    denied = require_login()
    if denied:
        return denied

    username = current_user()
    pages = user_pages(username)
    page_index = next((i for i, p in enumerate(pages) if p["id"] == page_id), None)
    if page_index is None:
        flash("Página não encontrada.", "error")
        return redirect(url_for("dashboard"))

    pages[page_index]["blocks"] = [b for b in pages[page_index].get("blocks", []) if b["id"] != block_id]
    pages[page_index]["updated_at"] = now_iso()
    save_user_pages(username, pages)
    flash("Bloco removido.", "success")
    return redirect(url_for("edit_page", page_id=page_id))


@app.route("/page/<int:page_id>/delete", methods=["POST"])
def delete_page(page_id: int):
    denied = require_login()
    if denied:
        return denied

    username = current_user()
    pages = user_pages(username)
    pages = [page for page in pages if page["id"] != page_id]
    save_user_pages(username, pages)
    flash("Página excluída.", "success")
    return redirect(url_for("dashboard"))


def block_label(block_type: str) -> str:
    return {
        "paragraph": "Novo parágrafo",
        "heading1": "Novo título",
        "quote": "Nova citação",
        "todo": "Nova tarefa",
        "bullet": "Novo item",
    }.get(block_type, "Novo bloco")


if __name__ == "__main__":
    ensure_file(USERS_DB, {})
    ensure_file(PAGES_DB, {})
    app.run(debug=True)
