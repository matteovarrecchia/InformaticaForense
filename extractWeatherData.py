import requests

def main(latitude,longitude,date,hour):
    api_key = "f1e25842b59f4fe39d592808250601"  # Inserisci qui la tua chiave API
    url = f"http://api.weatherapi.com/v1/history.json?key={api_key}&q={latitude},{longitude}&dt={date}&hour={hour}"
    json_data = 'weather_data.json'
    try:
        # Per usare l'API di Weatherapi.com
        response = requests.get(url)
        response.raise_for_status()  # Lancia un'eccezione per errori HTTP
        data = response.json()


        # Per caricare i dati da file json
        #with open(json_data, 'r') as file:
            #data = json.load(file)


        # Estrai i dati necessari dal JSON
        temp_c = data["forecast"]["forecastday"][0]["hour"][0]["temp_c"]
        time = data["forecast"]["forecastday"][0]["hour"][0]["time"]
        location_name = data["location"]["name"]
        condition_text = data["forecast"]["forecastday"][0]["day"]["condition"]["text"]
        wind_speed = data["forecast"]["forecastday"][0]["hour"][0]["wind_kph"]
        direzioneVento = data["forecast"]["forecastday"][0]["hour"][0]["wind_dir"]
        percentualePioggia = data["forecast"]["forecastday"][0]["hour"][0]["chance_of_rain"]


        #print di prova
        #print("Location name: ", location_name)
        #print("Temperatura in c°", temp_c)
        #print("Data e ora: ", time)
        #print("Condizioni meteo: ", condition_text)

        #restituisce le variabili come json
        return {
            "Location name": location_name,
            "Temperatura c°": temp_c,
            "Data e ora": time,
            "Condizioni meteo": condition_text,
            "Velocita del vento (Kph)": wind_speed,
            "Direzione del vento": direzioneVento,
            "% Possibilita Di Pioggia": percentualePioggia
        }

        #restituisce direttamente i valori delle variabili
        #return location_name, temp_c, time, condition_text


    except requests.exceptions.RequestException as e:
        print(f"Errore durante la richiesta all'API: {e}")
        return None

if __name__ == "__main__":
    final = main(41.103241, 16.630615, "2024-01-01", 21)
    print("I dati meteo sono: ", final)