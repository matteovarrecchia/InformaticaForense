from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime
import csv


def find_flight_history_url(flight_number, target_date):
    # Impostare le opzioni per il driver in modalità headless (senza aprire il browser)
    global filename
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Esegui senza apertura della finestra del browser
    chrome_options.add_argument("--disable-gpu")  # Disabilita l'uso della GPU (utile su alcune macchine)

    # Inizializzare il driver di Selenium con le opzioni per headless
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Costruire l'URL per la pagina di storia del volo
    base_url = f"https://it.flightaware.com/live/flight/{flight_number}/history"
    print(f"URL di base: {base_url}")
    driver.get(base_url)

    # Attendere che la pagina venga caricata completamente
    time.sleep(5)  # Puoi aumentare il tempo di attesa se necessario

    try:
        # Ottieni il codice sorgente della pagina
        page_source = driver.page_source

        # Costruire il pattern per trovare l'URL con la data specificata (nel formato trovato, es. data-target)
        date_str = target_date.replace("/", "")  # Rimuovere i separatori dalla data (es. 18/dic/2024 -> 20241218)
        pattern = rf'data-target="(/live/flight/{flight_number}/history/{date_str}[^\"]*)"'

        # Cercare l'URL corrispondente nel codice sorgente
        match = re.search(pattern, page_source)

        if match:
            # Se il pattern viene trovato, costruire l'URL completo
            relative_url = match.group(1)
            full_url = f"https://it.flightaware.com{relative_url}"  # Costruire l'URL completo
            tracklog_url = f"{full_url}/tracklog"  # Aggiungi '/tracklog' all'URL trovato

            # Stampare gli URL trovati
            print(f"Trovato URL corrispondente: {full_url}")
            print(f"URL con tracklog: {tracklog_url}")

            # Passa al parsing della tabella tracklog
            filename = extract_tracklog_data(flight_number, driver, tracklog_url, target_date)
        else:
            # Nessun match trovato
            print(f"Nessun URL trovato corrispondente alla data {target_date} per il volo {flight_number}.")
            return None
    except Exception as e:
        print(f"Errore durante la ricerca dell'URL: {e}")
        return None
    finally:
        # Chiudere il driver
        driver.quit()
        return filename


def extract_tracklog_data(flight_number, driver, tracklog_url, target_date):
    try:
        driver.get(tracklog_url)
        time.sleep(5)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        table = soup.find('table', {'class': 'prettyTable'})

        if not table:
            print("Tabella del tracklog non trovata.")
            return

        rows = table.find_all('tr')
        print("Timestamp, UTC, Callsign, Position, Altitude, Speed, Direction")

        data = []

        for row in rows[1:]:
            cols = row.find_all('td')
            cols = [col.text.strip() for col in cols]

            if len(cols) >= 7:
                orario = cols[0]
                latitudine = cols[1]
                longitudine = cols[2]
                rotta = cols[3]
                velocita_kn = cols[4]
                altitudine = cols[6]

                # Controlliamo che tutti i campi siano pieni
                if not all([orario, latitudine, longitudine, rotta, velocita_kn, altitudine]):
                    continue  # Salta la riga se uno dei campi è vuoto

                formatted_orario = format_orario(orario)
                utc = f"{target_date[:4]}-{target_date[4:6]}-{target_date[6:8]}T{formatted_orario}Z"

                timestamp_ms = get_timestamp_milliseconds(utc)
                if timestamp_ms is None:
                    continue  # Salta questa riga se il timestamp non è valido

                # Limita le decimali per latitudine e longitudine
                latitudine = latitudine[:latitudine.index('.') + 5] if '.' in latitudine else latitudine
                longitudine = longitudine[:longitudine.index('.') + 5] if '.' in longitudine else longitudine
                latitudine = latitudine[:7]
                longitudine = longitudine[:7]

                # Gestione dell'altitudine
                altitudine = altitudine.replace('.', '')
                if not altitudine:  # Se è vuoto o None
                    continue  # Salta la riga se l'altitudine è vuota
                else:
                    try:
                        altitudine = int(altitudine)
                    except ValueError:
                        continue  # Se l'altitudine non è un numero valido, salta questa riga

                altitudine = remove_repetition(str(altitudine))  # Aggiungi str() per sicurezza
                position = f"{latitudine},{longitudine}"

                formatted_rotta = format_rotta(rotta)

                # Aggiungiamo il record ai dati
                data.append({
                    "Timestamp": timestamp_ms,
                    "UTC": utc,
                    "Callsign": flight_number,
                    "Position": position,
                    "Altitude": altitudine,
                    "Speed": velocita_kn,  # Manteniamo come stringa per evitare errori di conversione
                    "Direction": formatted_rotta
                })

        # Lista finale dei dati che superano i controlli
        valid_data = []

        # Controllo delle altitudini e raccolta solo dei dati validi
        for i in range(len(data)):
            if i == 0 or i == len(data) - 1:  # Stampa il primo e l'ultimo elemento senza controllo
                valid_data.append(data[i])  # Aggiungi il record valido alla lista
            else:
                # Converti le altitudini in interi
                try:
                    prev_altitude = int(data[i - 1]['Altitude'])
                    curr_altitude = int(data[i]['Altitude'])
                    next_altitude = int(data[i + 1]['Altitude'])
                except ValueError:
                    continue  # Se c'è un errore nel convertire l'altitudine, salta questa riga

                # Calcola la media tra i valori precedente e successivo
                average_altitude = (prev_altitude + next_altitude) / 2

                # Condizioni per considerare valida l'altitudine corrente
                is_valid_altitude = (
                        abs(curr_altitude - prev_altitude) < 400 and  # Differenza plausibile con il valore precedente
                        abs(curr_altitude - next_altitude) < 400 and  # Differenza plausibile con il valore successivo
                        min(prev_altitude, next_altitude) <= curr_altitude <= max(prev_altitude, next_altitude)
                )

                # Se l'altitudine è valida, aggiungiamo il dato alla lista
                if is_valid_altitude:
                    valid_data.append(data[i])

        # Stampa i dati validi a schermo
        for entry in valid_data:
            print(
                f"{entry['Timestamp']},{entry['UTC']},{entry['Callsign']},{entry['Position']},{entry['Altitude']},"
                f"{entry['Speed']},{entry['Direction']}")

        # Scrittura dei dati validi nel file CSV
        # Creazione del nome del file CSV
        filename = f"flightCSV/{flight_number}_{target_date}.csv"

        # Apertura del file CSV in modalità scrittura
        with open(filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["Timestamp", "UTC", "Callsign", "Position", "Altitude", "Speed",
                                                      "Direction"])
            writer.writeheader()  # Scrive l'intestazione nel CSV
            for entry in valid_data:
                writer.writerow(entry)  # Scrive i dati nel file CSV

        print(f"I dati validi sono stati scritti nel file {filename}")
        return filename

    except Exception as e:
        print(f"Errore durante l'estrazione dei dati del tracklog: {e}")


# Funzione per ottenere il timestamp in millisecondi
def get_timestamp_milliseconds(utc_time):
    try:
        dt_obj = datetime.strptime(utc_time, "%Y-%m-%dT%H:%M:%SZ")
        timestamp_ms = int(dt_obj.timestamp() * 1000)
        return int(str(timestamp_ms)[:10])
    except ValueError:
         return None  # Ritorna None se ci sono errori di formattazione


# Formattazione della rotta
def format_rotta(rotta):
    rotta_number = re.sub(r'[^\d.-]', '', rotta)
    return rotta_number


def remove_repetition(value):
    n = len(value)
    for i in range(1, n // 2 + 1):
        if i >= 2 and value[:i] == value[i:i + i]:
            return value[:i]
    return value


# Funzione per formattare l'orario
def format_orario(orario):
    orario = orario.split(" ")[-1]
    parts = orario.split(":")
    if len(parts) >= 3:
        seconds = parts[2][:2]
        return f"{parts[0]}:{parts[1]}:{seconds}"
    return orario