from datetime import date, datetime, timedelta
import json
import urllib.parse
import urllib.request
import asyncio
from gmqtt import Client as MQTTClient

# MQTT-Konfiguration
BROKER_HOST = 'YOUR_BROKER'
USERNAME = 'YOUR_USERNAME'
PASSWORD = 'YOUR_PASSWORD'
TOPIC = 'doctolib/availability'

DOCTORS = [
    {
        'BOOKING_URL': 'https://www.doctolib.de/',
        'AVAILABILITIES_URL': '',
        'APPOINTMENT_NAME': 'Herr Dr. med. Mustermann',
        'MOVE_BOOKING_URL': ''
    },
    # Beispiel für weiteren Arzt:
    # {
    #     'BOOKING_URL': 'https://www.doctolib.de/',
    #     'AVAILABILITIES_URL': '',
    #     'APPOINTMENT_NAME': 'Dr. Mustermann',
    #     'MOVE_BOOKING_URL': ''
    # },
]

UPCOMING_DAYS = 15
MAX_DATETIME_IN_FUTURE = datetime.today() + timedelta(days=UPCOMING_DAYS)
NOTIFY_HOURLY = False

STOP = asyncio.Event()

def on_connect(client, flags, rc, properties):
    print("✅ Verbunden mit MQTT Broker")

def on_disconnect(client, packet, exc=None):
    print("🔌 Verbindung getrennt")
    STOP.set()

def on_publish(client, mid):
    print("📤 JSON-Nachricht veröffentlicht")

async def send_mqtt_json(payload: dict):
    client = MQTTClient("doctolib-json-client")
    client.set_auth_credentials(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish

    await client.connect(BROKER_HOST)
    client.publish(TOPIC, json.dumps(payload), qos=1)
    await asyncio.sleep(1)
    await client.disconnect()

async def main():
    for doctor in DOCTORS:
        url = doctor.get('AVAILABILITIES_URL')
        if not url:
            continue

        parsed = urllib.parse.urlparse(url)
        query = dict(urllib.parse.parse_qsl(parsed.query))
        query.update({
            'limit': UPCOMING_DAYS,
            'start_date': date.today().isoformat(),
        })
        final_url = parsed._replace(query=urllib.parse.urlencode(query)).geturl()

        req = urllib.request.Request(final_url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))

        slots_total = data.get('total', 0)
        slot_found = False
        next_slot = None

        for day in data.get('availabilities', []):
            if not day['slots']:
                continue
            dt = datetime.fromisoformat(day['date']).replace(tzinfo=None)
            if dt < MAX_DATETIME_IN_FUTURE:
                slot_found = True
                next_slot = dt.date().isoformat()
                break

        is_on_the_hour = datetime.now().minute == 0
        notify_due = is_on_the_hour and NOTIFY_HOURLY

        if not (slot_found or notify_due):
            continue

        payload = {
            "doctor": doctor.get('APPOINTMENT_NAME'),
   			"available": slot_found,
            "slots": slots_total,
            "next_slot": next_slot,
            "booking_url": doctor.get('BOOKING_URL'),
            "move_booking_url": doctor.get('MOVE_BOOKING_URL'),
        }

        await send_mqtt_json(payload)

if __name__ == '__main__':
    asyncio.run(main())
