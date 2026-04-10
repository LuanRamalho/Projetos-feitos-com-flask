from flask import Flask, render_template
from geopy.geocoders import Nominatim

app = Flask(__name__)

def obter_coordenadas(endereco):
    # Inicializa o geolocalizador (User_agent é obrigatório pela política da API)
    geolocator = Nominatim(user_agent="mapa_mundi_app")
    location = geolocator.geocode(endereco)
    
    if location:
        return [location.latitude, location.longitude]
    return [0, 0]  # Retorna centro do mapa caso não encontre

@app.route('/')
def index():
    # Aqui o algoritmo atribui o endereço desejado
    endereco_alvo = "Rio de Janeiro"
    coordenadas = obter_coordenadas(endereco_alvo)
    
    return render_template('index.html', coords=coordenadas, local=endereco_alvo)

if __name__ == '__main__':
    app.run(debug=True)