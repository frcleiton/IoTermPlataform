import paho.mqtt.client as mqtt
from pymongo import MongoClient
from datetime import datetime
import json

def on_connect(self, mosq, obj, rc):
    print("conectado: " + str(rc))

def on_message(mosq, obj, msg):
    #global message
    store_on_mongo(msg)

def on_publish(mosq, obj, mid):
    print("publicando: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscrito: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    print(string)
	
def grava_alarme(_alarme):
	cliente = MongoClient('localhost', 27017)
	banco = cliente.iotdata
	alarmes = banco.alarmes
	historico = banco.historico
	print 'gravando alarme e historico:'
	print _alarme
	alarmes.save(_alarme)
	historico.save(_alarme)
	
def store_on_mongo(_msg):
	#print(_msg.topic + " " + str(_msg.qos) + " " + str(_msg.payload))
	cliente = MongoClient('localhost', 27017)
	banco = cliente.iotdata
	leituras = banco.leituras

	#Store as date in Mongodb for sort()
	data = json.loads(_msg.payload)
	data['topic'] = _msg.topic
	str_mqtt_datetime = data[u't'] 
	datetime_object = datetime.strptime(str_mqtt_datetime, '%d-%m-%Y %H:%M:%S')
	data[u't'] = datetime_object

	#verifica parametros e dispara alarmes
	configuracoes = banco.configuracoes
	sensor = _msg.topic.split('/')[0]
	confs = configuracoes.find_one( {'sensor': sensor.upper() } )
	evt_alarme = {}
	if (_msg.topic.split('/')[1][:3]=='tem'):
		ctempmin = int(confs['tempmin'])
		dvalue   = int(data['value'])
		ctempmax = int(confs['tempmax'])
		if not ctempmin <= dvalue <= ctempmax:
			evt_alarme['descricao'] = 'Alerta de temperatura'
			evt_alarme['sensor']    = _msg.topic
			evt_alarme['createdAt'] = datetime.now()
			evt_alarme['minima']    = confs['tempmin']
			evt_alarme['maxima']    = confs['tempmax']
			evt_alarme['leitura']   = data['value']
			evt_alarme['mail']      = confs['email']
			grava_alarme(evt_alarme)
	if (_msg.topic.split('/')[1][:3]=='hum'):
		chummin = int(confs['hummin'])
		dvalue  = int(data['value'])
		chummax = int(confs['hummax'])
		if not chummin <= dvalue <= chummax:
			evt_alarme['descricao'] = 'Alerta de umidade'
			evt_alarme['sensor']    = _msg.topic
			evt_alarme['createdAt'] = datetime.now()
			evt_alarme['minima']    = confs['hummin']
			evt_alarme['maxima']    = confs['hummax']
			evt_alarme['leitura']   = data['value']
			evt_alarme['mail']      = confs['email']
			grava_alarme(evt_alarme)
			
	print 'Store in mongodb: ' + str(data)
	print leituras.insert_one(data).inserted_id
		
mqttc = mqtt.Client()
# Assign event callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
# Uncomment to enable debug messages
#mqttc.on_log = on_log

# Connect
mqttc.username_pw_set('ticleiton','ti@cleiton')
mqttc.connect("localhost",8883,60)

# Start subscribe, with QoS level 0
mqttc.subscribe("+/temperature", 1)
mqttc.subscribe("+/humidity", 1)

mqttc.loop_forever()



