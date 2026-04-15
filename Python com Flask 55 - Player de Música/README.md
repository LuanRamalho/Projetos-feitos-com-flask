# Player de Música com Flask

Projeto em Flask com banco JSON para cadastro, edição, exclusão, busca, player embutido e download.

## Estrutura

player_musica_flask/
├─ app.py
├─ musicas.json
├─ downloads/
├─ static/
│  └─ css/
│     └─ style.css
└─ templates/
   ├─ index.html
   └─ 404.html

## Como executar

```bash
pip install -r requirements.txt
python app.py
```

Abra no navegador:

```bash
http://127.0.0.1:5000
```

## Observação sobre o player e download

O player funciona melhor com links diretos para arquivos de áudio, como:
- .mp3
- .wav
- .ogg
- .m4a
- .aac
- .flac

Se o link apontar para uma página comum do YouTube ou de outro serviço, o player e o download podem não funcionar corretamente.
