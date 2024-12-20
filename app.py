from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import pandas as pd
from math import isnan

from download import find_flight_history_url
from extractWeatherData import *

app = Flask(__name__)

def altitude_to_color(altitude):
    if altitude < 1000:
        return 'green'
    elif altitude < 5000:
        return 'yellow'
    elif altitude < 10000:
        return 'orange'
    else:
        return 'red'


# Funzione per convertire nodi in km/h
def knots_to_kmh(knots):
    return knots * 1.852


@app.route('/')
def index():
    return render_template('index.html')


# Funzione per gestire il caso POST (carica il file CSV manualmente)
@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    # Controlla se la chiave 'csvfile' è presente nei files inviati
    if 'csvfile' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400

    file = request.files['csvfile']
    print(f"File ricevuto: {file.filename}")  # Aggiungi un log per il nome del file

    # Se il nome del file è vuoto, significa che l'utente non ha selezionato un file
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400

        # Definisci il percorso del file
    file_path = os.path.join("flightCSV/", file.filename)

    # Verifica se il file esiste
    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": f"File {file.filename} non trovato"}), 400

    # Verifica che il file sia un CSV
    if file and file.filename.endswith('.csv'):
        # Procedi con l'elaborazione del file CSV
        try:

            # Aggiungi un log per vedere il file che stai cercando di processare
            print(f"Elaborando il file: {file_path}")
            return process_csv(file_path)
        except Exception as e:
            # Se ci sono errori durante il processing, stampiamo l'errore completo
            print(f"Errore durante l'elaborazione del file: {str(e)}")  # Aggiungi un log per l'errore
            return jsonify({"status": "error", "message": f"Errore durante l'elaborazione del file: {str(e)}"}), 500
    else:
        return jsonify({"status": "error", "message": "File non valido, assicurati che sia un CSV"}), 400


def process_csv(file_path):
    try:
        print("PROCESS FILE", file_path)
        # Leggi il file CSV
        data = pd.read_csv(file_path)
        data[['latitude', 'longitude']] = data['Position'].str.split(',', expand=True)
        data['latitude'] = data['latitude'].astype(float)
        data['longitude'] = data['longitude'].astype(float)

        flight_data = []
        for index, row in data.iterrows():
            if not isnan(row["Direction"]):
                speed_kmh = knots_to_kmh(row["Speed"])  # Converti la velocità in km/h

                flight_data.append({
                    'callsign': row["Callsign"],
                    'latitude': row["latitude"],
                    'longitude': row["longitude"],
                    'altitude': row["Altitude"],
                    'speed': speed_kmh,
                    'direction': row["Direction"],
                    'timestamp': row["UTC"],
                })

        # Salva i dati come JSON
        with open("flight_data.json", "w") as json_file:
            json.dump(flight_data, json_file)

        # Calcola start_time ed end_time
        start_time = flight_data[0]['timestamp']
        end_time = flight_data[-1]['timestamp']

        # Restituisci i dati come JSON insieme ai timestamp
        return jsonify({
            "status": "success",
            "flightData": flight_data,
            "start_time": start_time,
            "end_time": end_time
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"Errore durante l'elaborazione del CSV: {str(e)}"}), 500


@app.route('/showFlightData', methods=['GET', 'POST'])
def show_flight_data():
    try:
        # Carica i dati dal file JSON
        with open('flight_data.json', 'r') as json_file:
            flight_data = json.load(json_file)

        # Controlla se flight_data è vuota
        if not flight_data:
            # Se vuota, reindirizza alla home page
            return redirect(url_for('index'))

        # Ordina i dati in base al timestamp
        flight_data.sort(key=lambda x: x['timestamp'])

        # Valori iniziali per il filtro
        start_time = flight_data[0]['timestamp']
        end_time = flight_data[-1]['timestamp']

        # Se riceviamo una richiesta POST, filtriamo i dati
        if request.method == 'POST':
            from_time = request.form.get('from', start_time)
            to_time = request.form.get('to', end_time)
        else:
            # Usare i valori dalla query string per mantenere il filtro
            from_time = request.args.get('from', start_time)
            to_time = request.args.get('to', end_time)

        # Filtra i dati
        filtered_data = [
            log for log in flight_data
            if from_time <= log['timestamp'] <= to_time
        ]

        # Paginazione
        page_size = 50
        page = request.args.get('page', 1, type=int)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paged_data = filtered_data[start_index:end_index]

        return render_template(
            'showFlightData.html',
            flight_data=paged_data,
            page=page,
            from_time=from_time,
            to_time=to_time,
            total_pages=(len(filtered_data) + page_size - 1) // page_size
        )
    except FileNotFoundError:
        # Se il file JSON non esiste, reindirizza alla home page
        return redirect(url_for('show_flight_data'))
    except Exception as e:
        # Gestione generica degli errori
        return redirect(url_for('show_flight_data'))


@app.route('/submit_flight_details', methods=['POST'])
def submit_flight_details():
    flight_code = request.form.get('flight_code')
    flight_date = request.form.get('flight_date')

    if flight_code and flight_date:
        # Elabora il codice volo (in maiuscolo) e la data (senza trattini)
        print(f"Codice volo: {flight_code}, Data: {flight_date}")
        url = find_flight_history_url(flight_code, flight_date)
        print(url)
        if url is not None:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error"}), 400

    return jsonify({"status": "error"}), 400


def send_csv_to_flask(csv_file_path):
    url = 'http://127.0.0.1:5000/upload_csv'  # URL della tua rotta Flask
    with open(csv_file_path, 'rb') as file:
        files = {'csvfile': file}
        response = requests.post(url, files=files)
        return response.json()


@app.route('/showWeatherData')
def show_weather_data():
    # Ottieni i parametri dalla query string
    latitude = request.args.get('lat')
    longitude = request.args.get('lng')
    date = request.args.get('date')  # Data nel formato 'YYYY-MM-DD'
    hour = request.args.get('hour')  # Ora come stringa 'HH'

    weatherData = main(latitude, longitude, date, hour)

    # Passa i dati al template
    return render_template('showWeatherData.html', weather_data=weatherData)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
