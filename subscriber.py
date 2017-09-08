import paho.mqtt.client as mqtt
from pymongo import MongoClient
import json

def on_connect(self, mosq, obj, rc):
    print("rc: " + str(rc))

def on_message(mosq, obj, msg):
    global message
    store_on_mongo(msg)

def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    print(string)

def store_on_mongo(_msg):
    #print(_msg.topic + " " + str(_msg.qos) + " " + str(_msg.payload))
    cliente = MongoClient('localhost', 27017)
    banco = cliente.iotdata
    leituras = banco.leituras

    #JSON Data
    data = json.loads(_msg.payload)
    data['topic'] = _msg.topic

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
mqttc.username_pw_set('ticimed','cimed@2017')
mqttc.connect("localhost",8883,60)

# Start subscribe, with QoS level 0
mqttc.subscribe("MG/TI/RP01/#", 2)

mqttc.loop_forever()

# Publish a message
#mqttc.publish("hello/world", "my message")

