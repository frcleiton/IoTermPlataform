# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import json
import random
from datetime import datetime

MQTT_ADDRESS = 'localhost'
# descomente esta linha para usar o servidor da Fundação Eclipse.
# MQTT_ADDRESS = 'iot.eclipse.org'
MQTT_PORT = 1883
# descomente esta linha caso seu servidor possua autenticação.
# MQTT_AUTH = Auth('login', 'senha')
MQTT_TIMEOUT = 60


def send_message():
    client = mqtt.Client()
    # descomente esta linha caso seu servidor possua autenticação.
    # client.username_pw_set(MQTT_AUTH.user, MQTT_AUTH.pwd)
    client.connect(MQTT_ADDRESS, MQTT_PORT, MQTT_TIMEOUT)
    humidity = random.randint(1,100)
    temperature = random.randint(0,40)
    time = str( datetime.now() )
    send_msg = {
        'datahora': time,
		'temperatura': temperature,
		'umidade': humidity
    }

    result, mid = client.publish('MG/TI/RP01', payload=json.dumps(send_msg), qos=1)
    print('Mensagem enviada ao canal: %d' % mid)

if __name__ == '__main__':
    send_message()
