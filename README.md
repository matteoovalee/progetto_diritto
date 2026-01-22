# IoT Privacy Simulator

**Progetto didattico per il corso di Informatica, Diritto e Società**  
*Università degli Studi di Udine - Anno Accademico 2025/2026*

L'applicazione simula un **middleware software** che intercetta flussi di dati provenienti da dispositivi **IoT** (Smart Home e Wearable) e applica tecniche di trasformazione **in tempo reale** per garantire la conformità al **GDPR**, secondo i principi di **Privacy by Design**.

---

## Obiettivo del progetto

Dimostrare concretamente come i requisiti normativi di protezione dei dati personali (GDPR) possano essere tradotti in **logiche algoritmiche**, garantendo la sicurezza del trattamento senza compromettere l'integrità e l'utilità del dato scientifico.

---

## Funzionalità e riferimenti normativi

Il simulatore implementa le seguenti tecniche di protezione, mappate sui relativi articoli del **Regolamento UE 2016/679 (GDPR)**:

| Funzionalità Software | Riferimento GDPR | Descrizione tecnica |
|----------------------|-----------------|---------------------|
| **Pseudonimizzazione** | **Art. 32 & 4(5)** | I dati identificativi diretti (es. nome, email) vengono trasformati tramite hashing **SHA-256 con salt crittografico**, impedendo l'identificazione diretta dell'interessato. |
| **Minimizzazione dei dati** | **Art. 5(1)(c)** | I dati non pertinenti alla finalità del trattamento (es. coordinate GPS precise per il monitoraggio energetico) vengono rimossi automaticamente dal payload. |
| **Mascheramento IP** | **Privacy by Design** | Gli indirizzi IP vengono generalizzati (subnet masking) per impedire la geo-localizzazione puntuale e ridurre il rischio di identificazione indiretta. |
| **Tutela dei dati particolari** | **Art. 9** | Rilevamento automatico di categorie particolari di dati (es. parametri sanitari/biometrici) con oscuramento della data di nascita per ridurre il rischio di re-identificazione. |
| **Audit Log (Accountability)** | **Art. 5(2)** | Generazione di un registro delle operazioni scaricabile in formato **CSV**, che traccia le policy applicate e la verifica di integrità senza memorizzare dati personali in chiaro. |
| **Controllo di integrità** | **Sicurezza (CIA)** | Verifica tramite hash **MD5** che il payload scientifico (es. battito cardiaco, temperatura) rimanga inalterato dopo le operazioni di anonimizzazione. |

---

## Struttura del repository

    .
    ├── app.py
    ├── privacy_engine.py
    ├── iot_simulator.py
    └── requirements.txt

- **app.py** – Frontend (Streamlit) per la visualizzazione della dashboard, gestione dello stato e calcolo in tempo reale delle trasformazioni  
- **privacy_engine.py** – Motore logico per la classificazione dei dati (PII / Sensitive) e l’applicazione delle regole di privacy  
- **iot_simulator.py** – Modulo di generazione di dati sintetici verosimili (basato sulla libreria Faker)  
- **requirements.txt** – Elenco delle dipendenze Python necessarie

---

## Installazione e avvio

### Prerequisiti

- Python 3.8 o superiore

### Setup

1. Clonare il repository o scaricare i file in una cartella locale  
2. Installare le dipendenze necessarie:

    pip install -r requirements.txt

### Esecuzione

Avviare l’applicazione tramite Streamlit:

    streamlit run app.py

L’interfaccia web si aprirà automaticamente nel browser all’indirizzo:

    http://localhost:8501

---

## Guida all’utilizzo

Il simulatore opera in modalità **interattiva**:

1. **Selezione scenario**  
   - Smart Home → Dati personali comuni  
   - Wearable Health → Dati particolari (Art. 9 GDPR)

2. **Configurazione delle misure di protezione**  
   Utilizzare il pannello laterale per attivare:
   - Pseudonimizzazione  
   - Minimizzazione  
   - Mascheramento IP  
   - Tutela dati sensibili  

3. **Ispezione (Pausa)**  
   Premere il tasto **PAUSA** per bloccare il flusso dati e visualizzare la **Pipeline di Trasformazione**, che spiega la logica applicata al singolo pacchetto.

4. **Verifica dell’accountability**  
   Scaricare il file **Audit Log (CSV)** per verificare la tracciatura delle operazioni di conformità.

---

## Autore

**Matteo Vale**, matricola 172019
