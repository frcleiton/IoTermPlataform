from flask import Flask, request, render_template
import time
import datetime
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
	
	#Preenche o array com os valores das ultimas leituras
	temperatures = []
	humidities = []
	for ultima_leitura in leituras.find( {'topic':'MG/TI/RP01/temperature'} ).sort('t', pymongo.DESCENDING ).limit(1):
		temperatures.append(ultima_leitura['value'])
	for ultima_leitura in leituras.find( {'topic':'MG/TI/RP01/humidity'} ).sort('t', pymongo.DESCENDING ).limit(1):
		humidities.append(ultima_leitura['value'])
	
	return render_template("sensors.html",temp=temperatures,hum=humidities,equipname='RPXX',equipsite='MGXX',tmin=10,tmax=30)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
