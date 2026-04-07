from flask import Flask, render_template, request, redirect, url_for, json
import os

app = Flask(__name__)
JSON_FILE = 'landscapes.json'

def load_data():
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    query = request.args.get('query', '').strip().lower()
    all_landmarks = load_data()
    
    if query:
        filtered = [item for item in all_landmarks if query in item['landmark'].lower()]
    else:
        filtered = all_landmarks
        
    return render_template('index.html', landmarks=filtered, query=query)

@app.route('/add', methods=['POST'])
def add_landmark():
    # Coleta os dados do formulário
    new_entry = {
        "city": request.form.get('city'),
        "country": request.form.get('country'),
        "landmark": request.form.get('landmark'),
        "image_url": request.form.get('image_url')
    }
    
    # Validação simples
    if all(new_entry.values()):
        data = load_data()
        data.append(new_entry)
        save_data(data)
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)