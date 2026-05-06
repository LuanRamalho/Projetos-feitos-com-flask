from flask import Flask, render_template, request, jsonify, session
import feedparser
import json
import os
import time
import re
from datetime import datetime
from dateutil import parser as dateparser

app = Flask(__name__)
app.secret_key = "newsfeed_secret_2024"

# ─── Default news sources with RSS feeds ──────────────────────────────────────
DEFAULT_SOURCES = [
    {"name": "G1 - Globo", "url": "https://g1.globo.com/rss/g1/", "icon": "📰", "color": "#e8382a"},
    {"name": "UOL Notícias", "url": "https://rss.uol.com.br/feed/noticias.xml", "icon": "🔵", "color": "#0066cc"},
    {"name": "Terra", "url": "https://www.terra.com.br/rss/", "icon": "🌍", "color": "#00a651"},
    {"name": "Tecnoblog", "url": "https://tecnoblog.net/feed/", "icon": "💻", "color": "#7952b3"},
    {"name": "TecMundo", "url": "https://rss.tecmundo.com.br/feed", "icon": "⚡", "color": "#ff6600"},
    {"name": "Folha de S.Paulo", "url": "https://feeds.folha.uol.com.br/folha/emcimadahora/rss091.xml", "icon": "🗞️", "color": "#c00"},
    {"name": "Estadão", "url": "https://www.estadao.com.br/rss/ultimas.xml", "icon": "📋", "color": "#003f8a"},
]

# ─── Category keyword mapping ──────────────────────────────────────────────────
CATEGORY_KEYWORDS = {
    "tecnologia": [
        "tecnologia","tech","software","hardware",
        "inteligência artificial","machine learning","deep learning",
        "startup","aplicativo","celular","smartphone","computador",
        "internet","digital","cibersegurança","segurança digital",
        "robô","robótica","drone","5g","chip","processador",
        "openai","chatgpt","google","microsoft","apple","samsung",
        "android","iphone","programação","desenvolvedor","developer",
        "amazon","meta","facebook","twitter","tiktok","youtube",
        "streaming de vídeo","nuvem","cloud computing","bitcoin",
        "criptomoeda","blockchain","web3","tecmundo","tecnoblog",
        "gadget","wearable","tablet","notebook","laptop","realidade virtual",
        "realidade aumentada","inteligência","algoritmo","dados","big data"
    ],
    "saude": [
        "saúde","medicina","médico","hospital","doença","vírus","vacina","remédio",
        "tratamento","câncer","diabetes","covid","pandemia","oms","sus","plano de saúde",
        "cirurgia","enfermagem","farmácia","pesquisa médica","bem-estar","mental",
        "nutrição","dieta","exercício","fitness","obesidade","hipertensão","alzheimer",
        "dengue","gripe","antibiótico","genética","stem cell","células-tronco"
    ],
    "automoveis": [
        "carro","automóvel","veículo automotor","moto","motocicleta","caminhão",
        "ônibus","tesla","volkswagen","fiat","ford","chevrolet","toyota",
        "honda","hyundai","bmw","mercedes-benz","audi","porsche","renault",
        "peugeot","citroën","jeep","ram","pickup","suv","sedan","hatch",
        "combustível","etanol","gasolina","motor a combustão","câmbio automático",
        "freio abs","pneu","concessionária","recall","detran","trânsito",
        "rodovia","autopeça","emplacamento","licenciamento","ipva","seguro auto",
        "quatro rodas","duas rodas","test drive","autonomia elétrica","carro elétrico",
        "moto elétrica","frota","montadora"
    ],
    "esportes": [
        "futebol","campeonato","copa","gol","time","clube","jogador","técnico",
        "treino","escalação","partida","jogo","rodada","série a","série b",
        "libertadores","champions","olimpíadas","atletismo","basquete","nba",
        "vôlei","tênis","nadal","federer","fórmula 1","f1","verstappen","hamilton",
        "mma","boxe","natação","ginástica","ciclismo","surfe","skate","handebol",
        "flamengo","corinthians","palmeiras","são paulo","santos","grêmio","inter",
        "cruzeiro","atlético","vasco","botafogo","fluminense","sport","recife"
    ],
    "entretenimento": [
        "filme","cinema","série","tv","televisão","netflix","disney","hbo","prime",
        "show","música","banda","cantor","álbum","streaming","globo","sbt","record",
        "novela","reality","bbb","masterchef","the voice","actor","atriz","diretor",
        "celebridade","famoso","red carpet","oscar","emmy","grammy","festival",
        "lollapalooza","rock in rio","turnê","show","videogame","game","playstation",
        "xbox","nintendo","animação","quadrinhos","livro","best-seller","literatura"
    ],
    "negocios": [
        "economia","negócio","empresa","mercado","bolsa","ações","investimento",
        "finanças","banco","taxa","juros","inflação","pib","dólar","euro","câmbio",
        "exportação","importação","comércio","varejo","indústria","fusão","aquisição",
        "ipo","startup","empreendedor","emprego","desemprego","salário","trabalhador",
        "sindicato","reforma","tributário","imposto","receita federal","bcb","selic",
        "b3","ibovespa","petrobras","vale","embraer","ambev","itaú","bradesco"
    ],
    "brasil": [
        "brasil","brasileira","brasileiro","brasileiros","lula","governo federal",
        "congresso nacional","senado federal","câmara dos deputados","planalto",
        "supremo tribunal","stf","stj","tse","eleição brasileira","partido político",
        "pt ","mdb"," pl ","psdb","pdt","psol","união brasil",
        "governador","prefeito","vereador","deputado federal","senador",
        "prefeitura","governo do estado","ibge","anatel","anvisa","inpe",
        "brasília","ministério da","ministério do","banco central do brasil",
        "petrobras","embrapa","vale s.a","embraer","ibovespa","b3 ",
        "selic","ipca","fgts","inss","sus ","bolsa família","bpc"
    ],
    "mundo": [
        "internacional","exterior","no exterior","fora do brasil",
        "guerra","conflito armado","ucrânia","rússia","china","taiwan",
        "eua","estados unidos","europa","união europeia","oriente médio",
        "israel","palestina","hamas","irã","iraque","síria","afeganistão",
        "onu","otan","nato","g7","g20","fmi","banco mundial","omc",
        "diplomacia","embaixada","tratado internacional","sanção internacional",
        "trump","biden","macron","putin","xi jinping","zelensky",
        "reino unido","grã-bretanha","japão","coreia","índia",
        "argentina","chile","colômbia","venezuela","bolívia","peru",
        "méxico","canadá","austrália","africa","nigéria","angola",
        "refugiado","crise global","imigração ilegal","fronteira internacional"
    ],
}

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"sources": DEFAULT_SOURCES, "local_city": ""}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def classify_article(title, summary, source_name, source_type="geral"):
    """
    Classifica um artigo em categorias com base no tipo da fonte e em palavras-chave.

    Regras:
    - Fontes 'local': sempre retornam apenas ["local"].
    - Fontes especializadas (tecnologia, saude, automoveis, negocios, esportes,
      entretenimento): retornam sua categoria própria + "brasil"/"mundo" se o
      conteúdo do artigo contiver palavras-chave correspondentes.
    - Fontes 'geral': classificação completa por palavras-chave no título,
      resumo e nome da fonte.
    """
    # Fontes locais: sempre e somente "local"
    if source_type == "local":
        return ["local"]

    text = (title + " " + summary).lower()

    # Fontes especializadas: forçam sua categoria; só adicionam brasil/mundo via conteúdo
    SPECIALIZED = {"tecnologia", "saude", "automoveis", "negocios", "esportes", "entretenimento"}
    if source_type in SPECIALIZED:
        matched = [source_type]
        if any(kw in text for kw in CATEGORY_KEYWORDS["brasil"]):
            matched.append("brasil")
        if any(kw in text for kw in CATEGORY_KEYWORDS["mundo"]):
            matched.append("mundo")
        return matched

    # Fontes gerais: classificação completa por palavras-chave
    full_text = (title + " " + summary + " " + source_name).lower()
    matched = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in full_text for kw in keywords):
            matched.append(cat)
    return matched if matched else ["geral"]

def fetch_feed(source):
    try:
        d = feedparser.parse(source["url"])
        articles = []
        for entry in d.entries[:20]:
            title = entry.get("title", "Sem título")
            summary = re.sub(r"<[^>]+>", "", entry.get("summary", ""))[:300]
            link = entry.get("link", "#")
            published = ""
            pub_raw = entry.get("published", entry.get("updated", ""))
            if pub_raw:
                try:
                    dt = dateparser.parse(pub_raw)
                    published = dt.strftime("%d/%m/%Y %H:%M")
                except Exception:
                    published = pub_raw[:16]

            image = ""
            if hasattr(entry, "media_content") and entry.media_content:
                image = entry.media_content[0].get("url", "")
            if not image and hasattr(entry, "enclosures") and entry.enclosures:
                image = entry.enclosures[0].get("href", "")
            if not image:
                img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', entry.get("summary", ""))
                if img_match:
                    image = img_match.group(1)

            source_type = source.get("type", "geral")
            categories = classify_article(title, summary, source["name"], source_type)
            articles.append({
                "title": title,
                "summary": summary,
                "link": link,
                "published": published,
                "image": image,
                "source": source["name"],
                "source_color": source.get("color", "#555"),
                "source_icon": source.get("icon", "📰"),
                "source_type": source_type,
                "categories": categories,
            })
        return articles
    except Exception as e:
        return []

@app.route("/")
def index():
    data = load_data()
    return render_template("index.html", sources=data["sources"], local_city=data.get("local_city", ""))

@app.route("/api/news")
def api_news():
    data = load_data()
    category = request.args.get("category", "")
    city = data.get("local_city", "").lower()

    all_articles = []

    for src in data["sources"]:
        articles = fetch_feed(src)

        # 🔹 FILTRO LOCAL
        if category == "local" and city:
            filtered = []
            for art in articles:
                text = (art["title"] + " " + art["summary"]).lower()

                if city in text or "rio de janeiro" in text or "rj" in text:
                    filtered.append(art)

            articles = filtered

        all_articles.extend(articles)

    all_articles.sort(key=lambda x: x["published"], reverse=True)

    return jsonify({
        "articles": all_articles,
        "total": len(all_articles)
    })

@app.route("/api/sources", methods=["GET"])
def get_sources():
    data = load_data()
    return jsonify(data["sources"])

@app.route("/api/sources", methods=["POST"])
def add_source():
    body = request.get_json()
    name = body.get("name", "").strip()
    url = body.get("url", "").strip()
    icon = body.get("icon", "📰")
    color = body.get("color", "#555555")
    if not name or not url:
        return jsonify({"error": "Nome e URL são obrigatórios"}), 400
    data = load_data()
    if any(s["url"] == url for s in data["sources"]):
        return jsonify({"error": "Fonte já existe"}), 409
    data["sources"].append({"name": name, "url": url, "icon": icon, "color": color})
    save_data(data)
    return jsonify({"ok": True})

@app.route("/api/sources/<int:idx>", methods=["DELETE"])
def delete_source(idx):
    data = load_data()
    if 0 <= idx < len(data["sources"]):
        data["sources"].pop(idx)
        save_data(data)
        return jsonify({"ok": True})
    return jsonify({"error": "Índice inválido"}), 404

@app.route("/api/city", methods=["POST"])
def set_city():
    body = request.get_json()
    city = body.get("city", "").strip()
    data = load_data()
    data["local_city"] = city
    save_data(data)
    return jsonify({"ok": True, "city": city})

if __name__ == "__main__":
    app.run(debug=True, port=5000)