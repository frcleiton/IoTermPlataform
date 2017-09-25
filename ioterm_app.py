from flask import Flask, request, Response, render_template
#import time
from datetime import date, datetime, timedelta
from email.Utils import formatdate
from pymongo import MongoClient
import pymongo
#from functools import wraps
#from flask.ext.login import LoginManager, UserMixin, login_required, login_user, logout_user

app = Flask(__name__)

@app.route("/")
def index():
	#Conectando ao banco MongoDB
	cliente = MongoClient('localhost', 27017)
	banco = cliente.iotdata
	leituras = banco.leituras

	#Busca o valor da ultima leitura por topico/dispositivo
	temperatures = []
	humidities = []
	strdatetime = []
	str_time = ''
	for ultima_leitura in leituras.find( {'topic':'RP01/temperature'} ).sort('t', pymongo.DESCENDING ).limit(1):
	   temperatures.append(ultima_leitura['value'])
	   strdatetime.append(ultima_leitura['t'].strftime("%d-%m-%Y %H:%M"))
	for ultima_leitura in leituras.find( {'topic':'RP01/humidity'} ).sort('t', pymongo.DESCENDING ).limit(1):
	   humidities.append(ultima_leitura['value'])
	for ultima_leitura in leituras.find( {'topic':'RP02/temperature'} ).sort('t', pymongo.DESCENDING ).limit(1):
	   temperatures.append(ultima_leitura['value'])
	   strdatetime.append(ultima_leitura['t'].strftime("%d-%m-%Y %H:%M"))
	for ultima_leitura in leituras.find( {'topic':'RP02/humidity'} ).sort('t', pymongo.DESCENDING ).limit(1):
	   humidities.append(ultima_leitura['value'])

	return render_template("sensors.html",temp=temperatures,hum=humidities,str_time=strdatetime,tmin=29,tmax=30)

@app.route("/hist/<sensor>")
def historico(sensor):
	msg = 'Sensor: ' +sensor

    #Conectando ao banco MongoDB
	cliente = MongoClient('localhost', 27017)
	banco = cliente.iotdata
	leituras = banco.leituras

	yesterday = datetime.now() - timedelta(days=1)

	topico = sensor.upper() + '/temperature'
	registros = []
	for registro in leituras.find( {'topic':topico, 't': {'$gte':yesterday}} ).sort('t', pymongo.DESCENDING ):
		registros.append([registro['t'],registro['value']])

	#if cont == 0:
	#	return '<H2>DADOS NAO ENCONTRADOS</H2>'

	from_date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
	to_date_str = datetime.now().strftime("%Y-%m-%d %H:%M")


	return render_template("historico.html",
							temp 			= registros,
							#hum 			= time_adjusted_humidities,
							from_date 		= from_date_str,
							to_date 		= to_date_str,
							query_string	= 'select ', #This query string is used
							#by the Plotly link
							sensorname      = sensor.upper())


@app.route("/conf/<sensor>")
def configuracao(sensor):
	msg = 'Sensor: ' +sensor

	paritens = ['15','30','20','50','alerta@ioterm.com.br']
	if request.method == 'GET':
		return render_template("settings.html",parametros=paritens,max=30,sensorname=sensor.upper())
##    if request.method == 'POST':
##        set_min = request.form['temp_min']
##        curs2.execute('UPDATE parametros SET valor = %d where parametro = %s' % (int(set_min),"'LIMITE_MIN_TEMP'"))
##        set_max = request.form['temp_max']
##        curs2.execute('UPDATE parametros SET valor = %d where parametro = %s' % (int(set_max),"'LIMITE_MAX_TEMP'"))
##        conn2.commit()
##        conn2.close()
##        return redirect('/lab_parametros')

def imprime():
    cont = 0




if __name__ == "__main__":
	app.run(debug=True,host='0.0.0.0')
