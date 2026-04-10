from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

# Rota principal que carrega a interface (Frontend)
@app.route('/')
def index():
    return render_template('index.html')

# Rota da API que envia o JSON com os nomes dos países
@app.route('/api/countries')
def get_countries():
    # Carrega o arquivo JSON e o retorna para o frontend
    json_path = os.path.join(app.root_path, 'countries.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        countries_data = json.load(f)
    return jsonify(countries_data)

if __name__ == '__main__':
    app.run(debug=True)