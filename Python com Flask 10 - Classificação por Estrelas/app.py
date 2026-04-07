from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
DATA_FILE = 'data.json'

# Função para carregar os dados no estilo NoSQL (sem IDs, apenas chaves e valores)
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

# Função para salvar o estado atual dos votos
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vote', methods=['POST'])
def vote():
    star = request.form.get('star')
    if star in ["1", "2", "3", "4", "5"]:
        data = load_data()
        data[star] += 1
        save_data(data)
    return redirect(url_for('results'))

@app.route('/results')
def results():
    data = load_data()
    total_votes = sum(data.values())
    
    stats = {}
    total_score = 0
    
    # Calcula as porcentagens e a média
    for star_str, count in data.items():
        star_int = int(star_str)
        total_score += star_int * count
        percentage = (count / total_votes * 100) if total_votes > 0 else 0
        stats[star_int] = {
            'count': count,
            'percentage': round(percentage, 2)
        }
        
    average = (total_score / total_votes) if total_votes > 0 else 0
    
    return render_template('results.html', stats=stats, total=total_votes, average=round(average, 1))

if __name__ == '__main__':
    # O debug=True facilita o desenvolvimento com reload automático
    app.run(debug=True)