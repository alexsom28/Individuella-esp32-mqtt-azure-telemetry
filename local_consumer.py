from common import local_client, validate, display

def received(client, userdata, msg):
    try:
        display('LOKALT', validate(msg.payload, msg.topic))
    except (ValueError, UnicodeError):
        print('Avvisade ett ogiltigt meddelande', flush=True)

if __name__ == '__main__':
    client = local_client('local-consumer', received)
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        client.disconnect()
