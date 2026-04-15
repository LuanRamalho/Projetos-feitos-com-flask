from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
import uuid
from pathlib import Path

app = Flask(__name__)
app.secret_key = "troque-esta-chave-para-producao"

DB_PATH = Path(__file__).parent / "clothes.json"

def load_db():
    if not DB_PATH.exists():
        save_db([])
        return []
    with open(DB_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_db(data):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def find_item(item_id):
    data = load_db()
    for item in data:
        if item.get("id") == item_id:
            return item
    return None

@app.route("/", methods=["GET"])
def index():
    q_name = request.args.get("name", "").strip().lower()
    q_brand = request.args.get("brand", "").strip().lower()
    q_type = request.args.get("type", "").strip().lower()
    q_color = request.args.get("color", "").strip().lower()
    q_size = request.args.get("size", "").strip().lower()

    data = load_db()

    def matches(item):
        if q_name and q_name not in item.get("name","").lower():
            return False
        if q_brand and q_brand not in item.get("brand","").lower():
            return False
        if q_type and q_type not in item.get("type","").lower():
            return False
        if q_color and q_color not in item.get("color","").lower():
            return False
        if q_size and q_size not in item.get("size","").lower():
            return False
        return True

    filtered = [d for d in data if matches(d)]
    filtered.sort(key=lambda x: x.get("name","").lower())
    return render_template("index.html", items=filtered, query=request.args)

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        color = request.form.get("color","").strip()
        type_ = request.form.get("type","").strip()
        brand = request.form.get("brand","").strip()
        url = request.form.get("url","").strip()
        size = request.form.get("size","").strip()

        if not name:
            flash("O nome da roupa é obrigatório.", "danger")
            return redirect(url_for("create"))

        item = {
            "id": str(uuid.uuid4()),
            "name": name,
            "color": color,
            "type": type_,
            "brand": brand,
            "url": url,
            "size": size
        }
        data = load_db()
        data.append(item)
        save_db(data)
        flash("Roupa criada com sucesso.", "success")
        return redirect(url_for("index"))

    return render_template("form.html", action="create", item={})

@app.route("/edit/<item_id>", methods=["GET", "POST"])
def edit(item_id):
    item = find_item(item_id)
    if not item:
        flash("Item não encontrado.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name","").strip()
        color = request.form.get("color","").strip()
        type_ = request.form.get("type","").strip()
        brand = request.form.get("brand","").strip()
        url = request.form.get("url","").strip()
        size = request.form.get("size","").strip()

        if not name:
            flash("O nome da roupa é obrigatório.", "danger")
            return redirect(url_for("edit", item_id=item_id))

        data = load_db()
        for d in data:
            if d.get("id") == item_id:
                d["name"] = name
                d["color"] = color
                d["type"] = type_
                d["brand"] = brand
                d["url"] = url
                d["size"] = size
                break
        save_db(data)
        flash("Roupa atualizada com sucesso.", "success")
        return redirect(url_for("index"))

    return render_template("form.html", action="edit", item=item)

@app.route("/delete/<item_id>", methods=["POST"])
def delete(item_id):
    data = load_db()
    new_data = [d for d in data if d.get("id") != item_id]
    if len(new_data) == len(data):
        flash("Item não encontrado.", "danger")
    else:
        save_db(new_data)
        flash("Roupa excluída com sucesso.", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
