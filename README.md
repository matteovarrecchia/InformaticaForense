# Flight Forensics - Documentazione

## Panoramica

**Flight Forensics** è un'applicazione web sviluppata utilizzando **Flask**, **Python**, **JavaScript**, **CSS** e **HTML** che permette agli utenti di analizzare le rotte di volo e i log di volo. L'app offre diverse funzionalità avanzate per appassionati di aviazione, professionisti e chiunque sia interessato a tracciare e analizzare voli in modo dettagliato.

Questa applicazione consente agli utenti di cercare un volo specifico tramite il numero del volo e la data (entro un periodo massimo di tre mesi) e visualizzare la rotta del volo. Inoltre, è possibile caricare i log di volo in formato CSV per un'analisi più approfondita.

Oltre alla visualizzazione delle rotte, l'app fornisce informazioni sull'altitudine, sulla velocità, sull'orario e sulla direzione dell'aereo, con la possibilità di filtrare i log per ora e visualizzare questi dati sia graficamente che in formato tabellare. L'app integra anche una API meteo che fornisce informazioni sul meteo, la velocità del vento e altre condizioni atmosferiche lungo il percorso del volo.

## Funzionalità

### 1. **Ricerca Volo e Visualizzazione della Rotta**

- L'app consente di cercare un volo specifico inserendo il numero del volo e la data (entro un massimo di tre mesi dalla data attuale).
- Una volta inseriti i criteri di ricerca, l'app recupera i dati del volo e mostra la rotta seguita dall'aereo su una mappa.
- Questa visualizzazione aiuta gli utenti ad analizzare il percorso esatto seguito dall'aereo durante il volo selezionato.

### 2. **Caricamento Manuale dei Log e Analisi**

- Gli utenti possono caricare i log di volo in formato **CSV**. Dopo aver cliccato sul pulsante "Invia", i log vengono elaborati e analizzati.
- Questa funzionalità permette agli utenti di analizzare i propri log di volo manualmente, sia per dati personali che per log provenienti da altre fonti.

### 3. **Legenda Basata sull'Altitudine con Codifica a Colori**

- L'app include una legenda che rappresenta visivamente l'altitudine dell'aereo durante il volo. In base all'altitudine, la rotta è colorata per dare agli utenti una comprensione intuitiva del comportamento verticale dell'aereo.
- Questa funzionalità è particolarmente utile per tracciare i cambiamenti di altitudine e comprendere il profilo verticale del volo.

### 4. **Analisi Dettagliata dei Dati GPS**

- Per ogni punto GPS registrato, l'app fornisce le seguenti informazioni:
  - **Velocità (km/h)**
  - **Altitudine**
  - **Ora**
  - **Direzione**
- Gli utenti possono cliccare su qualsiasi punto GPS sulla rotta per visualizzare questi dettagli. Questo è particolarmente utile per analizzare segmenti specifici del volo in modo approfondito.

### 5. **Filtraggio Basato sull'Ora**

- Gli utenti possono filtrare i log di volo in base a una determinata fascia oraria. Questo consente di esaminare in modo più dettagliato i dati del volo in un periodo specifico, utile per risolvere problemi o analizzare fasi particolari del volo.

### 6. **Visualizzazione dei Log in Modalità Tabellare**

- Oltre alla visualizzazione grafica della rotta, gli utenti possono anche visualizzare i log di volo in formato **tabellare**. Questa vista mostra tutti i dati grezzi in una tabella, con colonne come:
  - Timestamp
  - Latitudine e Longitudine
  - Velocità
  - Altitudine
  - Direzione
- La visualizzazione tabellare è utile per gli utenti che preferiscono lavorare con i dati grezzi o che necessitano di esportare le informazioni.

### 7. **Informazioni Meteo tramite API**

- L'app integra una API meteo che fornisce informazioni sulle condizioni atmosferiche lungo la rotta del volo.
- Sono disponibili informazioni su **velocità del vento**, **temperatura**, **precipitazioni** e altre condizioni meteo, che aiutano gli utenti a capire le condizioni che l'aereo ha incontrato durante il volo.
- Questa funzionalità è utile per professionisti e appassionati di aviazione che sono interessati a capire come le condizioni meteorologiche influenzano le rotte di volo.

## Tecnologie Utilizzate

- **Flask**: Un micro-framework per Python utilizzato per gestire la logica backend, il routing e l'elaborazione dei dati.
- **Python**: Il linguaggio principale utilizzato per l'elaborazione dei dati e la logica del backend.
- **JavaScript**: Utilizzato per l'interattività del frontend, in particolare per gestire il contenuto dinamico e la visualizzazione delle rotte di volo.
- **CSS**: Linguaggio di stile utilizzato per progettare e stilizzare l'interfaccia utente dell'applicazione.
- **HTML**: Il linguaggio di markup di base utilizzato per creare la struttura delle pagine web.


## Istruzioni per l'Installazione

### Clonare il Repository

Clonare questo repository sul proprio computer utilizzando Git:

```bash
git clone https://github.com/matteovarrecchia/InformaticaForense.git
```

### Installare le Dipendenze

Sarà necessario installare le librerie Python richieste. Si consiglia di utilizzare un ambiente virtuale per l'installazione. Esegui il comando seguente per installare le dipendenze:

```bash
pip install -r requirements.txt
```

### Avviare l'Applicazione

Una volta installate le dipendenze, è possibile avviare il server di sviluppo di Flask:

```bash
python app.py
```

### Accedere all'App

Apri il tuo browser e vai su `http://127.0.0.1:5000` per iniziare a utilizzare l'app.

### Caricamento dei Log

I log di volo devono essere caricati nella cartella **flightCSV** per poter essere utilizzati nell'applicazione. Tuttavia, se il volo viene cercato tramite la funzione di ricerca automatica, non è necessario caricare manualmente i log, poiché l'app recupererà i dati direttamente dal sistema.

