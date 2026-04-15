from flask import Flask, render_template, request, jsonify
import json
import os
import uuid
import requests

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'cities.json')


def load_cities():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_cities(cities):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(cities, f, indent=2, ensure_ascii=False)


def geocode_city(city_name):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        'name': city_name,
        'count': 1,
        'language': 'pt',
        'format': 'json'
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if 'results' not in data or not data['results']:
            return None
        r = data['results'][0]
        return {
            'name': r.get('name', city_name),
            'country': r.get('country', ''),
            'country_code': r.get('country_code', '').lower(),
            'admin1': r.get('admin1', ''),
            'latitude': r['latitude'],
            'longitude': r['longitude'],
            'timezone': r.get('timezone', 'UTC'),
            'population': r.get('population', 0)
        }
    except Exception as e:
        return None


def fetch_weather(lat, lon, timezone):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': lat,
        'longitude': lon,
        'current': (
            'temperature_2m,relative_humidity_2m,apparent_temperature,'
            'is_day,precipitation,weather_code,wind_speed_10m,'
            'wind_direction_10m,surface_pressure,visibility,cloud_cover'
        ),
        'hourly': (
            'temperature_2m,relative_humidity_2m,apparent_temperature,'
            'precipitation_probability,precipitation,weather_code,'
            'wind_speed_10m,wind_direction_10m,uv_index,visibility,cloud_cover'
        ),
        'daily': (
            'weather_code,temperature_2m_max,temperature_2m_min,'
            'apparent_temperature_max,apparent_temperature_min,'
            'sunrise,sunset,precipitation_sum,precipitation_probability_max,'
            'wind_speed_10m_max,wind_direction_10m_dominant,'
            'uv_index_max,rain_sum,showers_sum,snowfall_sum,'
            'precipitation_hours,wind_gusts_10m_max'
        ),
        'timezone': timezone,
        'forecast_days': 16,
        'wind_speed_unit': 'kmh'
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        return resp.json()
    except Exception as e:
        return {'error': str(e)}


@app.route('/')
def index():
    cities = load_cities()
    return render_template('index.html', cities=cities)


@app.route('/api/add_city', methods=['POST'])
def add_city():
    data = request.get_json()
    city_name = (data or {}).get('city', '').strip()
    if not city_name:
        return jsonify({'error': 'Nome da cidade é obrigatório'}), 400

    geo = geocode_city(city_name)
    if not geo:
        return jsonify({'error': 'Cidade não encontrada. Verifique o nome e tente novamente.'}), 404

    cities = load_cities()
    for c in cities:
        if abs(c['latitude'] - geo['latitude']) < 0.01 and abs(c['longitude'] - geo['longitude']) < 0.01:
            return jsonify({'error': f"{geo['name']} já foi adicionada!"}), 409

    city_id = str(uuid.uuid4())[:8]
    city_data = {'id': city_id, **geo}
    cities.append(city_data)
    save_cities(cities)
    return jsonify(city_data)


@app.route('/api/delete_city/<city_id>', methods=['DELETE'])
def delete_city(city_id):
    cities = load_cities()
    cities = [c for c in cities if c['id'] != city_id]
    save_cities(cities)
    return jsonify({'success': True})


@app.route('/api/weather/<city_id>')
def weather_api(city_id):
    cities = load_cities()
    city = next((c for c in cities if c['id'] == city_id), None)
    if not city:
        return jsonify({'error': 'Cidade não encontrada'}), 404
    weather = fetch_weather(city['latitude'], city['longitude'], city['timezone'])
    return jsonify({'city': city, 'weather': weather})


@app.route('/city/<city_id>')
def city_detail(city_id):
    cities = load_cities()
    city = next((c for c in cities if c['id'] == city_id), None)
    if not city:
        return render_template('404.html'), 404
    return render_template('detail.html', city=city)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
