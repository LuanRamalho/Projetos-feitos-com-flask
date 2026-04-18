from __future__ import annotations

import json
import os
from pathlib import Path
from uuid import uuid4

from flask import Flask, flash, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "carros.json"

app = Flask(__name__)
app.secret_key = "troque-esta-chave-em-producao"


def ensure_data_file() -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        save_cars([])


def load_cars() -> list[dict]:
    ensure_data_file()
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_cars(cars: list[dict]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp_file = DATA_FILE.with_suffix(".json.tmp")
    with tmp_file.open("w", encoding="utf-8") as f:
        json.dump(cars, f, ensure_ascii=False, indent=4)
    os.replace(tmp_file, DATA_FILE)


def normalize(value: str) -> str:
    return (value or "").strip().lower()


def plate_exists(plate: str, ignore_id: str | None = None) -> bool:
    plate_norm = normalize(plate)
    for car in load_cars():
        if normalize(car.get("placa", "")) == plate_norm and car.get("id") != ignore_id:
            return True
    return False


@app.route("/")
def index():
    fabricante = normalize(request.args.get("fabricante", ""))
    modelo = normalize(request.args.get("modelo", ""))

    cars = load_cars()
    if fabricante:
        cars = [c for c in cars if fabricante in normalize(c.get("fabricante", ""))]
    if modelo:
        cars = [c for c in cars if modelo in normalize(c.get("modelo", ""))]

    return render_template(
        "index.html",
        cars=cars,
        filters={
            "fabricante": request.args.get("fabricante", ""),
            "modelo": request.args.get("modelo", ""),
        },
    )


@app.route("/novo", methods=["GET", "POST"])
def novo_carro():
    if request.method == "POST":
        fabricante = request.form.get("fabricante", "").strip()
        modelo = request.form.get("modelo", "").strip()
        ano = request.form.get("ano", "").strip()
        placa = request.form.get("placa", "").strip()
        cor = request.form.get("cor", "").strip()
        link = request.form.get("link", "").strip()
        combustivel = request.form.get("combustivel", "").strip()

        if not all([fabricante, modelo, ano, placa, cor, link, combustivel]):
            flash("Preencha todos os campos.", "danger")
            return redirect(url_for("novo_carro"))

        if plate_exists(placa):
            flash("Já existe um carro cadastrado com essa placa.", "danger")
            return redirect(url_for("novo_carro"))

        cars = load_cars()
        cars.append(
            {
                "id": str(uuid4()),
                "fabricante": fabricante,
                "modelo": modelo,
                "ano": ano,
                "placa": placa,
                "cor": cor,
                "link": link,
                "combustivel": combustivel,
            }
        )
        save_cars(cars)
        flash("Carro cadastrado com sucesso.", "success")
        return redirect(url_for("index"))

    return render_template(
        "form.html",
        title="Novo carro",
        button_text="Salvar",
        car={
            "fabricante": "",
            "modelo": "",
            "ano": "",
            "placa": "",
            "cor": "",
            "link": "",
            "combustivel": "",
        },
    )


@app.route("/editar/<car_id>", methods=["GET", "POST"])
def editar_carro(car_id: str):
    cars = load_cars()
    car = next((c for c in cars if c["id"] == car_id), None)

    if not car:
        flash("Carro não encontrado.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        fabricante = request.form.get("fabricante", "").strip()
        modelo = request.form.get("modelo", "").strip()
        ano = request.form.get("ano", "").strip()
        placa = request.form.get("placa", "").strip()
        cor = request.form.get("cor", "").strip()
        link = request.form.get("link", "").strip()
        combustivel = request.form.get("combustivel", "").strip()

        if not all([fabricante, modelo, ano, placa, cor, link, combustivel]):
            flash("Preencha todos os campos.", "danger")
            return redirect(url_for("editar_carro", car_id=car_id))

        if plate_exists(placa, ignore_id=car_id):
            flash("Já existe outro carro cadastrado com essa placa.", "danger")
            return redirect(url_for("editar_carro", car_id=car_id))

        car["fabricante"] = fabricante
        car["modelo"] = modelo
        car["ano"] = ano
        car["placa"] = placa
        car["cor"] = cor
        car["link"] = link
        car["combustivel"] = combustivel

        save_cars(cars)
        flash("Carro atualizado com sucesso.", "success")
        return redirect(url_for("index"))

    return render_template(
        "form.html",
        title="Editar carro",
        button_text="Atualizar",
        car=car,
    )


@app.route("/excluir/<car_id>", methods=["POST"])
def excluir_carro(car_id: str):
    cars = load_cars()
    new_cars = [c for c in cars if c["id"] != car_id]

    if len(new_cars) == len(cars):
        flash("Carro não encontrado.", "danger")
    else:
        save_cars(new_cars)
        flash("Carro excluído com sucesso.", "success")

    return redirect(url_for("index"))


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True)