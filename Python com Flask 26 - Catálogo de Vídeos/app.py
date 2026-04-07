from flask import Flask, render_template, request, redirect, url_for
import json
import os
import re

app = Flask(__name__)
DATA_FILE = 'videos.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"videos_video": []}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_embed_url(url):
    """Converte links normais do YouTube em links de embed."""
    if not url: return ""
    video_id = ""
    if "youtu.be/" in url:
        video_id = url.split("/")[-1].split("?")[0]
    elif "youtube.com/watch" in url:
        video_id = re.search(r"v=([^&]+)", url).group(1)
    elif "youtube.com/embed/" in url:
        return url
    
    return f"https://www.youtube.com/embed/{video_id}" if video_id else url

@app.route('/')
def index():
    search_query = request.args.get('search', '').lower()
    data = load_data()
    videos = data.get("videos_video", [])
    
    if search_query:
        videos = [v for v in videos if search_query in v['titulo'].lower()]
    
    # Prepara os links para exibição
    for v in videos:
        v['embed_link'] = get_embed_url(v['link'])
        
    return render_template('index.html', videos=videos, search=search_query)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = load_data()
        videos = data.get("videos_video", [])
        
        new_id = max([v['id'] for v in videos], default=0) + 1
        new_video = {
            "id": new_id,
            "titulo": request.form['titulo'],
            "descricao": request.form['descricao'],
            "link": request.form['link']
        }
        
        videos.append(new_video)
        data["videos_video"] = videos
        save_data(data)
        return redirect(url_for('index'))
    return render_template('form.html', action="Adicionar")

@app.route('/edit/<int:video_id>', methods=['GET', 'POST'])
def edit(video_id):
    data = load_data()
    videos = data.get("videos_video", [])
    video = next((v for v in videos if v['id'] == video_id), None)
    
    if request.method == 'POST':
        video['titulo'] = request.form['titulo']
        video['descricao'] = request.form['descricao']
        video['link'] = request.form['link']
        save_data(data)
        return redirect(url_for('index'))
    
    return render_template('form.html', video=video, action="Editar")

@app.route('/delete/<int:video_id>')
def delete(video_id):
    data = load_data()
    data["videos_video"] = [v for v in data["videos_video"] if v['id'] != video_id]
    save_data(data)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)