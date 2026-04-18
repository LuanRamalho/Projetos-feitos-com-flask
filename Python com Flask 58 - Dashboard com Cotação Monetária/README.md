# Dashboard Financeiro em Tempo Real

Painel em Flask com:
- cotação de moedas;
- variação diária;
- conversor rápido;
- métricas do sistema com `psutil`;
- atualização automática por polling, sem WebSocket.

A fonte de câmbio usada aqui é o Frankfurter, que fornece taxas diárias e não exige API key.

## Requisitos

- Python 3.10 ou superior

## Instalação

### Windows
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Linux / macOS
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Acesso

Abra:
`http://127.0.0.1:5000`

## Configurações opcionais

- `FX_BASE`: moeda base do painel, por padrão `EUR`
- `FX_QUOTES`: lista de moedas separadas por vírgula
- `CACHE_TTL_SECONDS`: tempo de cache do backend
- `FX_API_BASE`: endpoint da API de câmbio

Exemplo:
```bash
set FX_BASE=USD
set FX_QUOTES=BRL,EUR,GBP,JPY,CHF
python app.py
```

ou no Linux/macOS:
```bash
export FX_BASE=USD
export FX_QUOTES=BRL,EUR,GBP,JPY,CHF
python app.py
```
