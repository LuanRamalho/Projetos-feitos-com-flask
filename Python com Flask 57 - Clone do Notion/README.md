# Clone do Notion

Projeto em **Python + Flask** com banco em **JSON**, login/cadastro e um editor simples inspirado no Notion.

## Recursos

* Login
* Cadastro
* Esqueci senha
* Logout
* Dashboard com sidebar
* Criar, editar, excluir e buscar páginas
* Editor de blocos
* Banco de dados em JSON

## Estrutura

* `app.py`
* `users.json`
* `pages.json`
* `templates/`
* `static/style.css`

## Como executar

```bash
pip install -r requirements.txt
python app.py
```

Depois acesse:

```bash
http://127.0.0.1:5000
```

## Observação

Este projeto usa senha em texto puro e recuperação simples por nome de usuário porque foi pedido como arquitetura lite. Em produção, o ideal é usar hash de senha e recuperação com token.

