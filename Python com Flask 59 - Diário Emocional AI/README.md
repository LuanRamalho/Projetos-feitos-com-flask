# Diário Emocional com IA

Projeto em **Python + Flask** com armazenamento local em **JSON** (estilo documento/NoSQL), análise de sentimento, classificador de textos e chatbot pessoal baseado no histórico do usuário.

## Recursos
- Cadastro de registros emocionais
- Análise automática de sentimento com Hugging Face / Transformers
- Classificador simples de textos para identificar spam, suporte, emoção e neutro
- Chatbot que responde usando os próprios registros salvos
- Histórico com busca, filtro, edição e exclusão
- Interface colorida, moderna e responsiva

## Estrutura
- `app.py` — aplicação Flask principal
- `data/entries.json` — banco local em JSON
- `templates/` — telas HTML
- `static/style.css` — visual do sistema

## Instalação
```bash
pip install -r requirements.txt
```

## Execução
```bash
python app.py
```

Depois, abra:

```bash
http://127.0.0.1:5000
```

## Observações
- O projeto usa **JSON local** como armazenamento, sem SQLite.
- A análise com **Transformers** tenta carregar um modelo pré-treinado.
- Se o modelo não estiver disponível no ambiente, o app usa um fallback local para continuar funcionando.
- O chatbot aqui é baseado no histórico salvo, para manter o projeto leve e fácil de portar.

## Ideia de portfólio
Esse projeto mostra:
- Flask
- CRUD local
- armazenamento em JSON
- integração com IA
- interface moderna
- análise de dados do usuário
