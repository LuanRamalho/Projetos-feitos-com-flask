# WeatherAtlas 🌍

Aplicativo de previsão do tempo global com Flask e Open-Meteo API (gratuita, sem chave de API).

## Estrutura

```
weather_app/
├── app.py                  # Servidor Flask + API Open-Meteo
├── requirements.txt        # Dependências
├── data/
│   └── cities.json         # Banco de dados JSON (gerado automaticamente)
└── templates/
    ├── index.html          # Página principal com cards de cidades
    └── detail.html         # Página de detalhes com 3 abas
```

## Instalação e execução

1. **Criar ambiente virtual (recomendado):**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

2. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Executar:**
   ```bash
   python app.py
   ```

4. **Abrir no navegador:** http://localhost:5000

## Funcionalidades

### Página Principal
- Busca de cidade por nome (qualquer cidade do mundo)
- Cards com: cidade, país, temperatura atual, condição do tempo, horário local
- Botão ✕ para remover cidade
- Clique no card abre a janela de detalhes

### Janela de Detalhes (3 abas)
- **Próximas Horas** — próximas 36h com temperatura, precipitação, vento, UV, umidade
- **Hoje** — nascer/pôr do sol, duração do dia, mín/máx, chuva (mm), neve, vento, rajadas, pressão, UV, visibilidade
- **15 Dias** — previsão diária com condição, mín/máx, chuva, vento, nascer/pôr do sol

## APIs utilizadas
- **Geocoding:** https://geocoding-api.open-meteo.com (gratuita)
- **Meteorologia:** https://api.open-meteo.com (gratuita, sem chave)
