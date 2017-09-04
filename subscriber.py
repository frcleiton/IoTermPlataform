import paho.mqtt.client as mqtt

def on_connect(self, mosq, obj, rc):
    print("rc: " + str(rc))

def on_message(mosq, obj, msg):
    global message
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    message = msg.payload

def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    print(string)

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
mqttc.connect("ubuntuIoTServer",8883,60)

# Start subscribe, with QoS level 0
mqttc.subscribe("MG/TI/RP01", 0)

mqttc.loop_forever()

# Publish a message
#mqttc.publish("hello/world", "my message")

# Continue the network loop, exit when an error occurs
#rc = 0
#while rc == 0:
#   rc = mqttc.loop()
#   mqttc.publish("MG/TI/RP01",message)
#print("rc: " + str(rc))