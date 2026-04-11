import json
from flask import Flask, render_template

app = Flask(__name__)

def carregar_planetas():
    with open('planetas.json', 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/')
def index():
    planetas = carregar_planetas()
    return render_template('index.html', planetas=planetas)

if __name__ == '__main__':
    app.run(debug=True)