from flask import Flask
import paho.mqtt.client as mqtt

app = Flask(__name__)

topic = 'RP01'
topic2 = 'SERVER'

port = 5000

def on_connect(self, client, userdata, rc):
    client.subscribe(topic)
    client.publish(topic2, "STARTING SERVER")
    client.publish(topic2, "CONNECTED")

def on_message(client, userdata, msg):
    client.publish(topic2, "MESSAGE")

@app.route('/')
def hello_world():
    return 'Hello World! I am running on port ' + str(port)

if __name__ == '__main__':
    client = mqtt.Client()
    #client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect('localhost')
    client.loop_start()

    app.run(host='0.0.0.0', port=port)