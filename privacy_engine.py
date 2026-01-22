import hashlib
import json
import copy

class PrivacyAuditor:
    # Keywords configuration
    SENSITIVE_KEYWORDS = ['name', 'email', 'owner', 'user', 'fullname']
    TECHNICAL_KEYWORDS = ['ip', 'mac', 'device', 'serial']
    GEO_KEYWORDS = ['gps', 'lat', 'lon', 'location']
    SPECIAL_KEYWORDS = ['heart', 'blood', 'health', 'dob', 'ssn'] # Art. 9 GDPR

    @staticmethod
    def scan_packet(data):
        report = {
            "contains_pii": False,
            "contains_geo": False,
            "contains_special": False,
            "fields_detected": []
        }
        
        flat_data = {**data.get('payload', {}), **data.get('metadata', {})}
        
        for key in flat_data.keys():
            k = key.lower()
            tag = "GENERIC"
            
            if any(x in k for x in PrivacyAuditor.SPECIAL_KEYWORDS):
                report["contains_special"] = True
                tag = "SPECIAL (Art. 9)"
            elif any(x in k for x in PrivacyAuditor.SENSITIVE_KEYWORDS):
                report["contains_pii"] = True
                tag = "PII (Identificativo)"
            elif any(x in k for x in PrivacyAuditor.GEO_KEYWORDS):
                report["contains_geo"] = True
                tag = "GEO (Ubicazione)"
            elif any(x in k for x in PrivacyAuditor.TECHNICAL_KEYWORDS):
                tag = "TECH (Identificativo Indiretto)"
            
            report["fields_detected"].append(f"{key} -> {tag}")
            
        return report

def calculate_integrity_hash(payload):
    """Calcola hash MD5 del payload per verifica integrità scientifica."""
    payload_str = json.dumps(payload, sort_keys=True).encode()
    return hashlib.md5(payload_str).hexdigest()

def apply_privacy_rules(data_packet, config):
    """Applica le policy di Data Protection configurate."""
    
    processed = copy.deepcopy(data_packet)
    meta = processed['metadata']
    SALT = "PROJECT_SECRET_KEY_2026" 

    # --- MODALITÀ 1: ANONIMIZZAZIONE (Statistica / Art. 9) ---
    if config.get('anonymize_art9'):
        # 1. Cancellazione Identificativi Diretti
        for field in ['owner_name', 'user_fullname', 'owner_email', 'health_id', 'device_serial', 'device_id']:
            meta.pop(field, None)
        
        # 2. Cancellazione Identificativi Tecnici/Geo
        for field in ['ip_address', 'mac_address', 'gps_lat', 'gps_lon', 'location_city']:
            meta.pop(field, None)
            
        # 3. Generalizzazione Data Nascita (Solo Anno)
        if 'user_dob' in meta:
             meta['user_dob'] = meta['user_dob'].split('-')[0] # Solo YYYY

    # --- MODALITÀ 2: PSEUDONIMIZZAZIONE (Standard / Art. 32) ---
    else:
        # Pseudonimizzazione
        if config['pseudo']:
            for field in ['owner_name', 'user_fullname', 'owner_email', 'health_id']:
                if field in meta:
                    raw_value = f"{meta[field]}{SALT}".encode()
                    meta[field] = f"PSEUDO_{hashlib.sha256(raw_value).hexdigest()[:12]}"

        # Mascheramento IP
        if config['mask_ip']:
            if 'ip_address' in meta:
                parts = meta['ip_address'].split('.')
                meta['ip_address'] = f"{parts[0]}.{parts[1]}.xxx.xxx"
            if 'device_serial' in meta:
                 meta['device_serial'] = meta['device_serial'][:4] + "****"

        # Minimizzazione Geo
        if config['drop_geo']:
            for field in ['gps_lat', 'gps_lon', 'location_city']:
                meta.pop(field, None)

    return {"clean": processed, "payload": processed['payload']}