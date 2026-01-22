import random
from faker import Faker
import datetime

fake = Faker('it_IT')

def generate_smart_home_data():
    return {
        "source_type": "SMART_HOME_HUB",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "payload": {
            "temperature": round(random.uniform(18.0, 24.0), 2),
            "humidity": random.randint(30, 60),
            "energy_consumption": round(random.uniform(0.5, 2.5), 2)
        },
        "metadata": {
            "device_id": f"home_{random.randint(1000,9999)}",
            "owner_name": fake.name(),
            "owner_email": fake.email(),
            "ip_address": fake.ipv4(),
            "gps_lat": float(fake.latitude()),
            "gps_lon": float(fake.longitude())
        }
    }

def generate_wearable_data():
    return {
        "source_type": "HEALTH_WEARABLE",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "payload": {
            "heart_rate": random.randint(60, 140),
            "blood_oxygen": random.randint(95, 100),
            "steps": random.randint(0, 100)
        },
        "metadata": {
            "device_serial": f"wear_{random.randint(1000,9999)}",
            "user_fullname": fake.name(),
            "user_dob": fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%Y-%m-%d"),
            "health_id": fake.ssn(), 
            "location_city": fake.city()
        }
    }