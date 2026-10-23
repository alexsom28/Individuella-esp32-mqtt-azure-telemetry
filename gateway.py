"""Lokal MQTT -> beständig SQLite-kö -> Azure IoT Hub via HTTPS."""
import base64
import hashlib
import hmac
import json
import os
import sqlite3
import threading
import time
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from common import local_client, validate, display

DB = Path(__file__).with_name('outbox.sqlite3')

def connection_parts(text):
    parts = dict(part.split('=', 1) for part in text.split(';') if '=' in part)
    if not all(parts.get(k) for k in ('HostName', 'DeviceId', 'SharedAccessKey')):
        raise ValueError('Ange gateway-enhetens anslutningssträng i .env')
    if not parts['HostName'].endswith('.azure-devices.net'):
        raise ValueError('Förväntade ett Azure IoT Hub-värdnamn')
    base64.b64decode(parts['SharedAccessKey'], validate=True)
    return parts

def sas_token(parts):
    resource = quote(parts['HostName'] + '/devices/' + parts['DeviceId'], safe='')
    expires = str(int(time.time()) + 3600)
    signature = base64.b64encode(hmac.new(
        base64.b64decode(parts['SharedAccessKey']),
        (resource + '\n' + expires).encode(), hashlib.sha256).digest()).decode()
    return 'SharedAccessSignature ' + urlencode({'sr': parts['HostName'] + '/devices/' + parts['DeviceId'], 'sig': signature, 'se': expires})

def send(parts, payload):
    url = ('https://' + parts['HostName'] + '/devices/' + quote(parts['DeviceId'], safe='')
           + '/messages/events?api-version=2021-04-12')
    request = Request(url, data=payload.encode('utf-8'), method='POST', headers={
        'Authorization': sas_token(parts),
        'Content-Type': 'application/json; charset=utf-8',
        'iothub-contenttype': 'application/json',
        'iothub-contentencoding': 'utf-8',
    })
    with urlopen(request, timeout=20) as response:
        if response.status != 204:
            raise RuntimeError('Oväntad HTTP-status från Azure')

def worker(parts, stop):
    with sqlite3.connect(DB, timeout=10) as db:
        while not stop.is_set():
            row = db.execute('SELECT id, payload FROM outbox ORDER BY id LIMIT 1').fetchone()
            if row is None:
                stop.wait(0.5)
                continue
            try:
                send(parts, row[1])
            except HTTPError as error:
                print(f'Azure HTTP {error.code}; behåller meddelandet och försöker igen om 15 s', flush=True)
                stop.wait(15)
                continue
            except (URLError, TimeoutError, OSError, RuntimeError):
                print('Azure kunde inte nås; försöker igen om 15 s', flush=True)
                stop.wait(15)
                continue
            db.execute('DELETE FROM outbox WHERE id=?', (row[0],))
            db.commit()
            display('AZURE SKICKAT', json.loads(row[1]))

def received(client, userdata, msg):
    try:
        data = validate(msg.payload, msg.topic)
    except (ValueError, UnicodeError):
        print('Avvisade ogiltigt MQTT-meddelande', flush=True)
        return
    payload = json.dumps(data, ensure_ascii=False, allow_nan=False)
    with sqlite3.connect(DB, timeout=10) as db:
        db.execute('INSERT INTO outbox(payload) VALUES (?)', (payload,))
    display('LOKALT', data)

def main():
    parts = connection_parts(os.environ.get('AZURE_DEVICE_CONNECTION_STRING', ''))
    with sqlite3.connect(DB) as db:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('CREATE TABLE IF NOT EXISTS outbox(id INTEGER PRIMARY KEY, payload TEXT NOT NULL)')
    stop = threading.Event()
    thread = threading.Thread(target=worker, args=(parts, stop))
    thread.start()
    client = local_client('pi-gateway', received)
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()
        stop.set()
        thread.join()

if __name__ == '__main__':
    main()
