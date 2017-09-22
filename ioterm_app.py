from flask import Flask, request, render_template
import time
from datetime import datetime
from email.Utils import formatdate
from pymongo import MongoClient
import pymongo

app = Flask(__name__)

@app.route("/")
def read_temp_database():
	#Conectando ao banco MongoDB
	cliente = MongoClient('localhost', 27017)
	banco = cliente.iotdata
	leituras = banco.leituras
	
	#Busca o valor da ultima leitura por topico/dispositivo
	temperatures = []
	humidities = []
	str_time = ''
	for ultima_leitura in leituras.find( {'topic':'RP01/temperature'} ).sort('t', pymongo.DESCENDING ).limit(1):
		temperatures.append(ultima_leitura['value'])
		#print ultima_leitura['t']
		#strdatetime = datetime.now().strftime("%d-%m-%Y %H:%M")
		strdatetime = ultima_leitura['t'].strftime("%d-%m-%Y %H:%M")
	for ultima_leitura in leituras.find( {'topic':'RP01/humidity'} ).sort('t', pymongo.DESCENDING ).limit(1):
		humidities.append(ultima_leitura['value']))
	
	return render_template("sensors.html",temp=temperatures,hum=humidities,str_time=strdatetime,tmin=29,tmax=30)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
