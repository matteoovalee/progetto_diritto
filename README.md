# IoT Privacy Simulator

**Progetto didattico per il corso di Informatica, Diritto e Società**
*Università degli Studi di Udine - Anno Accademico 2025/2026*

L'applicazione simula un middleware software che intercetta flussi di dati provenienti da dispositivi IoT (Smart Home e Wearable) e applica tecniche di trasformazione in tempo reale per garantire la conformità al GDPR (Pseudonimizzazione) o per fini statistici (Anonimizzazione).

## Obiettivo del progetto

Dimostrare concretamente la differenza tra le misure di sicurezza per i dati personali e le tecniche di anonimizzazione irreversibile, come richiesto per il trattamento di dati particolari (es. sanitari) per fini statistici.

## Strategie di Protezione Implementate

Il simulatore adotta due strategie distinte in base alla tipologia di dato:

### 1. Dati Comuni (Smart Home) -> Pseudonimizzazione
Viene applicata la **Sicurezza del Trattamento (Art. 32)**. I dati restano personali ma protetti.
* **Hash + Salt:** Nomi e email vengono offuscati (reversibili solo dal titolare).
* **Minimizzazione:** Rimozione dati GPS inutili.

### 2. Dati Particolari (Health Wearable) -> Anonimizzazione
Viene applicata una trasformazione irreversibile per l'utilizzo statistico.
* **Rimozione Identificatori:** Nome, Email, IP, ID Dispositivo vengono rimossi dal payload.
* **Generalizzazione:** La data di nascita viene ridotta al solo anno per impedire la re-identificazione.
* **Finalità:** Il dataset risultante è utilizzabile per analisi aggregate.

## Funzionalità Tecniche

| Funzione | Descrizione Tecnica |
| :--- | :--- |
| **Pseudonimizzazione** | Hashing SHA-256 con Salt crittografico. |
| **Minimizzazione** | Rimozione selettiva chiavi JSON (es. `gps_lat`). |
| **Anonimizzazione** | Cancellazione massiva di tutti i campi `metadata` identificativi. |
| **Integrity Check** | Verifica MD5 sul payload scientifico (es. `heart_rate`) per garantire che la pulizia non alteri il dato utile. |
| **Audit Log** | Export CSV per tracciare le operazioni eseguite (Accountability). |

## Avvio Rapido

1. Installare le dipendenze: `pip install -r requirements.txt`
2. Avviare l'app: `streamlit run app.py`
3. Selezionare lo scenario:
   * **Smart Home:** Provare le checkbox standard.
   * **Health:** Attivare la spunta "Anonimizzazione" per visualizzare la rimozione totale degli identificativi.

---
**Autore:** Matteo Vale
