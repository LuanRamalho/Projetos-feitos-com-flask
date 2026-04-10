from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = "biblioteca_secret"
DATA_FILE = 'books.json'
PER_PAGE = 12  # Itens por página

def load_books():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_books(books):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(books, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    query = request.args.get('search', '').lower()
    page = int(request.args.get('page', 1))
    
    all_books = load_books()
    
    # Filtragem por Nome ou Autor
    filtered_books = [
        b for b in all_books 
        if query in b['title'].lower() or query in b['author'].lower()
    ]

    # Paginação
    total = len(filtered_books)
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    paginated_books = filtered_books[start:end]
    total_pages = (total + PER_PAGE - 1) // PER_PAGE

    return render_template('index.html', 
                           books=paginated_books, 
                           page=page, 
                           total_pages=total_pages, 
                           query=query)

@app.route('/add', methods=['POST'])
def add_book():
    new_book = {
        "author": request.form['author'],
        "title": request.form['title'],
        "year": int(request.form['year'])
    }
    books = load_books()
    books.insert(0, new_book) # Adiciona no topo
    save_books(books)
    flash("Livro adicionado com sucesso!")
    return redirect(url_for('index'))

@app.route('/edit/<int:book_idx>', methods=['POST'])
def edit_book(book_idx):
    books = load_books()
    # Atualiza os dados com base no formulário do Modal
    books[book_idx]['title'] = request.form['title']
    books[book_idx]['author'] = request.form['author']
    books[book_idx]['year'] = int(request.form['year'])
    save_books(books)
    flash("Livro atualizado com sucesso!")
    return redirect(url_for('index'))

@app.route('/delete/<int:book_idx>')
def delete_book(book_idx):
    books = load_books()
    if 0 <= book_idx < len(books):
        books.pop(book_idx)
        save_books(books)
        flash("Livro removido!")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)