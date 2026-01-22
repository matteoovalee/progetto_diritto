import streamlit as st
import time
import pandas as pd
import datetime
import uuid
from iot_simulator import generate_smart_home_data, generate_wearable_data
from privacy_engine import apply_privacy_rules, PrivacyAuditor, calculate_integrity_hash

# --- Configurazione Pagina ---
st.set_page_config(
    page_title="IoT Privacy Simulator", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Personalizzato (Toni professionali) ---
st.markdown("""
<style>
    .stMetric { background-color: #0e1117; border: 1px solid #303030; }
    .reportview-container .main .block-container { max-width: 1200px; }
    .pipeline-card {
        background-color: #262730;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #4CAF50;
        margin-bottom: 10px;
        font-size: 0.9em;
    }
    .pipeline-card.warning { border-left: 4px solid #FFA726; } /* Arancione standard */
    .pipeline-card.error { border-left: 4px solid #EF5350; } /* Rosso spento */
    .pipeline-card.anon { border-left: 4px solid #9C27B0; background-color: #2e1a2e; }
    .pipeline-card.alert { border-left: 4px solid #FF9800; background-color: #332b00; } 
</style>
""", unsafe_allow_html=True)

# --- Inizializzazione Stato ---
if "sim_active" not in st.session_state: st.session_state.sim_active = False
if "is_paused" not in st.session_state: st.session_state.is_paused = False
if "last_raw_packet" not in st.session_state: st.session_state.last_raw_packet = None
if "packet_counter" not in st.session_state: st.session_state.packet_counter = 0
if "history" not in st.session_state: st.session_state.history = []
if "show_tutorial" not in st.session_state: st.session_state.show_tutorial = True
if "session_id" not in st.session_state: st.session_state.session_id = str(uuid.uuid4())[:8].upper()

# --- Sidebar ---
with st.sidebar:
    st.header("🎛️ Pannello Controllo")
    st.caption(f"Session ID: {st.session_state.session_id}")
    
    scenario_options = ["🏠 Smart Home (Dati Comuni)", "❤️ Wearable Health (Art. 9 GDPR)"]
    selected_scenario = st.selectbox(
        "Scenario Dati", 
        scenario_options, 
        index=0,
        help="Selezionare il tipo di dispositivo IoT da simulare."
    )

    if "current_scenario" not in st.session_state: st.session_state.current_scenario = selected_scenario
    
    # --- LOGICA RESET FORZATO AL CAMBIO SCENARIO ---
    if st.session_state.current_scenario != selected_scenario:
        st.session_state.last_raw_packet = None
        st.session_state.current_scenario = selected_scenario
        st.session_state.sim_active = False
        st.session_state.is_paused = False
        
        # Reset: Impostiamo esplicitamente a False tutte le chiavi dei checkbox
        keys_to_reset = ["chk_pseudo", "chk_ip", "chk_geo", "chk_anon"]
        for key in keys_to_reset:
            st.session_state[key] = False
            
        st.rerun()
    
    st.divider()
    
    # --- LOGICA CONFIGURAZIONE ---
    st.subheader("Configurazione Privacy")
    st.caption("Privacy by Design & Default (Art. 25)")
    
    is_health = "Health" in selected_scenario
    
    # 1. Checkbox ANONIMIZZAZIONE (Solo per Health)
    cfg_anonymize = False
    if is_health:
        st.warning("⚠️ Rilevati Dati Sanitari (Art. 9)")
        cfg_anonymize = st.checkbox(
            "Anonimizzazione", 
            value=False,
            key="chk_anon",
            help="Rimuove irreversibilmente gli identificativi."
        )
    
    # 2. Checkbox PSEUDONIMIZZAZIONE (Disabilitate se Anonimizzazione è attiva)
    disable_standard = cfg_anonymize 
    
    cfg_pseudo = st.checkbox(
        "Pseudonimizzazione PII", 
        value=False,
        key="chk_pseudo",
        disabled=disable_standard,
        help="Trasforma i dati identificativi in hash (Art. 32 GDPR)."
    )
    cfg_mask_ip = st.checkbox(
        "Mascheramento ID Tecnici", 
        value=False,
        key="chk_ip",
        disabled=disable_standard,
        help="Oscura parzialmente l'indirizzo IP."
    )
    cfg_drop_geo = st.checkbox(
        "Minimizzazione Geo-Loc", 
        value=False,
        key="chk_geo",
        disabled=disable_standard,
        help="Rimuove coordinate GPS non necessarie (Art. 5.1.c)."
    )

    # Configurazione finale passata al motore
    current_config = {
        'pseudo': cfg_pseudo, 
        'mask_ip': cfg_mask_ip, 
        'drop_geo': cfg_drop_geo, 
        'mask_sensitive_dates': False, 
        'anonymize_art9': cfg_anonymize 
    }
    
    st.divider()
    st.metric("Pacchetti Processati", st.session_state.packet_counter)
    
    # --- EXPORT CSV (VISIBILE SOLO IN PAUSA) ---
    st.divider()
    st.subheader("📂 Accountability")
    
    if st.session_state.is_paused and len(st.session_state.history) > 0:
        csv_data = pd.DataFrame(st.session_state.history).to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📄 Scarica Audit Log",
            data=csv_data,
            file_name=f'gdpr_audit_{st.session_state.session_id}_{int(time.time())}.csv',
            mime='text/csv',
            key='audit_download',
            help="File pronto per il download."
        )
    elif len(st.session_state.history) > 0:
        st.info("⏸️ Mettere in PAUSA per scaricare il log.")
    else:
        st.caption("Nessun dato registrato.")

# --- Layout Principale ---

if st.session_state.show_tutorial:
    with st.expander("📘 Guida Rapida - Dashboard", expanded=True):
        st.markdown("""
        **Middleware Privacy Simulator**
        1. **Input:** Dati grezzi simulati.
        2. **Processing:**
           - *Smart Home:* Pseudonimizzazione (Sicurezza).
           - *Health:* Anonimizzazione.
        3. **Output:** Dato trattato pronto per il cloud.
        """)
        if st.button("Chiudi guida"):
            st.session_state.show_tutorial = False
            st.rerun()

st.title("🛡️ IoT Privacy Simulator")
st.markdown(f"**Scenario:** `{selected_scenario}`")

col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1, 1, 3])

with col_ctrl1:
    btn_label = "⏹️ STOP" if st.session_state.sim_active else "▶️ AVVIA"
    btn_type = "primary" if not st.session_state.sim_active else "secondary"
    if st.button(btn_label, type=btn_type):
        st.session_state.sim_active = not st.session_state.sim_active
        st.session_state.is_paused = False 
        st.rerun()

with col_ctrl2:
    pause_label = "▶️ RIPRENDI" if st.session_state.is_paused else "⏸️ PAUSA"
    if st.button(pause_label, disabled=not st.session_state.sim_active):
        st.session_state.is_paused = not st.session_state.is_paused
        st.rerun()

st.divider()

status_area = st.empty()
if not st.session_state.sim_active:
    status_area.info("Premere 'AVVIA' per iniziare la simulazione.")
elif st.session_state.sim_active and st.session_state.last_raw_packet is None:
    status_area.info("Inizializzazione sistema in corso...")
else:
    status_area.empty()

c_raw, c_audit, c_clean = st.columns([2, 1.5, 2])

# --- Logica di Rendering ---
if st.session_state.last_raw_packet:
    raw_packet_data = st.session_state.last_raw_packet["raw"]
    
    report = PrivacyAuditor.scan_packet(raw_packet_data)
    clean_packet_result = apply_privacy_rules(raw_packet_data, current_config)
    
    raw_hash = calculate_integrity_hash(raw_packet_data['payload'])
    clean_hash = calculate_integrity_hash(clean_packet_result['payload'])
    integrity_check = (raw_hash == clean_hash)
    
    with c_raw:
        st.subheader("🔴 Input (Sensore)")
        st.json(raw_packet_data) 
        if st.session_state.is_paused:
            st.info("Visualizzazione statica")

    with c_audit:
        st.subheader("⚙️ Processing")
        st.markdown("**Pipeline di Trasformazione:**")

        # --- AVVISO NORMATIVO ART. 9 (Se Health + NO Anonimizzazione) ---
        if report["contains_special"] and not current_config['anonymize_art9']:
             st.markdown(
                """<div class="pipeline-card alert">
                <b>⚠️ Rilevamento Art. 9 GDPR</b><br>
                <small>Categorie Particolari di Dati (Salute).</small><br>
                <small>Richiesta base giuridica specifica (es. Consenso o Anonimizzazione).</small>
                </div>""", unsafe_allow_html=True
            )

        # --- BRANCH 1: ANONIMIZZAZIONE (Health) ---
        if current_config['anonymize_art9']:
             st.markdown(
                """<div class="pipeline-card anon">
                <b>ANONIMIZZAZIONE</b><br>
                <small>Mode: <i>Irreversibile</i></small><br>
                <small>Action: <b>Rimozione Identificativi</b></small>
                </div>""", unsafe_allow_html=True
            )
             st.markdown(
                """<div class="pipeline-card anon">
                <b>Generalizzazione Data</b><br>
                <small>Action: <i>Solo Anno (Aggregazione)</i></small>
                </div>""", unsafe_allow_html=True
            )

        # --- BRANCH 2: PSEUDONIMIZZAZIONE (Standard) ---
        else:
            # 1. Pseudonimizzazione
            if current_config['pseudo'] and report["contains_pii"]:
                st.markdown(
                    """<div class="pipeline-card">
                    <b>1. Pseudonimizzazione</b><br>
                    <small>Logic: <code>SHA-256 + Salt</code></small><br>
                    <small>Ref: <i>Art. 32 GDPR</i></small>
                    </div>""", unsafe_allow_html=True
                )
            elif report["contains_pii"]:
                    st.markdown("""<div class="pipeline-card error"><b>1. Pseudonimizzazione</b><br>❌ DISATTIVATA (Rischio Alto)</div>""", unsafe_allow_html=True)

            # 2. Mascheramento IP
            if any("TECH" in x for x in report["fields_detected"]):
                if current_config['mask_ip']:
                    st.markdown(
                        """<div class="pipeline-card">
                        <b>2. Generalizzazione IP</b><br>
                        <small>Logic: <code>Subnet Masking</code></small>
                        </div>""", unsafe_allow_html=True
                    )
                else:
                    st.markdown("""<div class="pipeline-card warning"><b>2. Generalizzazione IP</b><br>⚠️ DISATTIVATA</div>""", unsafe_allow_html=True)

            # 3. Minimizzazione
            if report["contains_geo"]:
                if current_config['drop_geo']:
                    st.markdown(
                        """<div class="pipeline-card">
                        <b>3. Minimizzazione</b><br>
                        <small>Action: <b>DROP FIELD</b></small><br>
                        <small>Ref: <i>Art. 5.1.c</i></small>
                        </div>""", unsafe_allow_html=True
                    )
                else:
                    st.markdown("""<div class="pipeline-card warning"><b>3. Minimizzazione</b><br>⚠️ GPS Trasmesso</div>""", unsafe_allow_html=True)

        # Integrità (Comune a entrambi)
        if integrity_check:
            st.markdown(
                f"""<div class="pipeline-card">
                <b>Controllo Integrità</b><br>
                <small>Hash: <code>{raw_hash[:10]}...</code></small><br>
                <small>Status: ✅ <b>INALTERATO</b></small>
                </div>""", unsafe_allow_html=True
            )

    with c_clean:
        st.subheader("🟢 Output (Cloud)")
        st.json(clean_packet_result["clean"])
        if st.session_state.is_paused:
            st.success("Pronto per invio")

if st.session_state.sim_active and not st.session_state.is_paused:
    if "Home" in selected_scenario:
        full_raw = generate_smart_home_data()
        system_code = "SMART_HOME"
    else:
        full_raw = generate_wearable_data()
        system_code = "WEARABLE_HEALTH"
    
    raw_packet_state = {
        "raw": full_raw, 
        "payload": full_raw["payload"],
        "metadata": full_raw["metadata"]
    }

    clean_packet_log = apply_privacy_rules(full_raw, current_config)
    hash_log = calculate_integrity_hash(full_raw['payload'])
    integrity_log = (hash_log == calculate_integrity_hash(clean_packet_log['payload']))

    log_entry = {
        "Log_UUID": str(uuid.uuid4()),
        "Timestamp": datetime.datetime.now().isoformat(),
        "Session_ID": st.session_state.session_id,
        "System_Context": system_code,
        "Integrity_Status": "PASS" if integrity_log else "FAIL",
        "Data_Hash": hash_log,
        "Mode": "ANONYMIZED" if current_config.get('anonymize_art9') else "PSEUDONYMIZED",
        **clean_packet_log['payload']
    }
    st.session_state.history.append(log_entry)
    
    st.session_state.last_raw_packet = raw_packet_state
    st.session_state.packet_counter += 1
    
    time.sleep(1.5)
    st.rerun()