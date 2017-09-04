import paho.mqtt.client

def _on_connect(client, userdata, flags, rc):
    if rc == 0:
        for msg in userdata:
            client.publish(*msg)


def _on_publish(client, userdata, mid):
    client.disconnect()


def main():
    msgs = []
    for _ in range(21):
        msgs.append((
            'topic',
            b'payload',
            1,  # QoS == 1
            False,  # don't retain
        ))

    client = paho.mqtt.client.Client(userdata=msgs)
    client.on_publish = _on_publish
    client.on_connect = _on_connect
    client.connect('127.0.0.1', 1883, 60)
    client.loop_forever()


if __name__ == '__main__':
    main()