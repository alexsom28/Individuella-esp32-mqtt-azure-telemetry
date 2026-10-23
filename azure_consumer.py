import os
from azure.eventhub import EventHubConsumerClient, TransportType
from common import validate, display

def received(partition_context, event):
    if event is None:
        return
    try:
        display('AZURE', validate(event.body_as_str(encoding='UTF-8')))
    except (ValueError, UnicodeError):
        print('Avvisade ett ogiltigt Azure-meddelande', flush=True)

if __name__ == '__main__':
    connection = os.environ.get('EVENTHUB_CONNECTION_STRING', '')
    if not connection.startswith('Endpoint=sb://') or 'EntityPath=' not in connection:
        raise SystemExit('Ange Event Hubs-kompatibel anslutningssträng med EntityPath i .env')
    client = EventHubConsumerClient.from_connection_string(
        conn_str=connection,
        consumer_group=os.getenv('EVENTHUB_CONSUMER_GROUP', '$Default'),
        transport_type=TransportType.AmqpOverWebsocket,
    )
    print('Lyssnar på NYA meddelanden från Azure. Låt ESP32 och gateway fortsätta köra.', flush=True)
    try:
        with client:
            client.receive(on_event=received, starting_position='@latest')
    except KeyboardInterrupt:
        pass
