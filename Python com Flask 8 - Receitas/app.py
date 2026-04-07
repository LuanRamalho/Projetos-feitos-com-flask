from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
DATA_FILE = 'recipes.json'

def load_recipes():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_recipes(recipes):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(recipes, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    search = request.args.get('search', '').lower()
    recipes = load_recipes()
    if search:
        recipes = [r for r in recipes if search in r['nome'].lower()]
    return render_template('index.html', recipes=recipes, search=search)

@app.route('/add', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        recipes = load_recipes()
        new_recipe = {
            "nome": request.form['nome'],
            "ingredientes": request.form['ingredientes'],
            "preparo": request.form['preparo'],
            "tempo": request.form['tempo'],
            "porcoes": request.form['porcoes'],
            "categoria": request.form['categoria'],
            "url_imagem": request.form['url_imagem']
        }
        recipes.append(new_recipe)
        save_recipes(recipes)
        return redirect(url_for('index'))
    return render_template('recipe_form.html', action="Adicionar")

@app.route('/edit/<nome>', methods=['GET', 'POST'])
def edit_recipe(nome):
    recipes = load_recipes()
    recipe = next((r for r in recipes if r['nome'] == nome), None)
    
    if request.method == 'POST':
        recipe.update({
            "nome": request.form['nome'],
            "ingredientes": request.form['ingredientes'],
            "preparo": request.form['preparo'],
            "tempo": request.form['tempo'],
            "porcoes": request.form['porcoes'],
            "categoria": request.form['categoria'],
            "url_imagem": request.form['url_imagem']
        })
        save_recipes(recipes)
        return redirect(url_for('index'))
    
    return render_template('recipe_form.html', recipe=recipe, action="Editar")

@app.route('/delete/<nome>')
def delete_recipe(nome):
    recipes = load_recipes()
    recipes = [r for r in recipes if r['nome'] != nome]
    save_recipes(recipes)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)