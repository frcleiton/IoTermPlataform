from flask import Flask, request, Response, render_template
from flask import session, redirect, url_for, escape
from datetime import datetime
from email.Utils import formatdate
from pymongo import MongoClient
import pymongo

app = Flask(__name__)

@app.route("/")
def index():
	usulogado = 'Nao logado ainda'
	if not 'username' in session:
		return redirect(url_for('login'))
	else:
		username = session['username']
		print 'logado como ' + username
		usulogado = username

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
	   strdatetime = ultima_leitura['t'].strftime("%d-%m-%Y %H:%M")
	for ultima_leitura in leituras.find( {'topic':'RP01/humidity'} ).sort('t', pymongo.DESCENDING ).limit(1):
	   humidities.append(ultima_leitura['value'])
	for ultima_leitura in leituras.find( {'topic':'RP02/temperature'} ).sort('t', pymongo.DESCENDING ).limit(1):
	   temperatures.append(ultima_leitura['value'])
	   strdatetime = ultima_leitura['t'].strftime("%d-%m-%Y %H:%M")
	for ultima_leitura in leituras.find( {'topic':'RP02/humidity'} ).sort('t', pymongo.DESCENDING ).limit(1):
	   humidities.append(ultima_leitura['value'])
	#renderiza o template HTML
	return render_template("sensors.html",temp=temperatures,hum=humidities,str_time=strdatetime,tmin=29,tmax=30, user=usulogado)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		if request.form['username'] == 'frcleiton':
			session['username'] = request.form['username']
			return redirect(url_for('index'))
	return render_template("login.html",msg='Usuario ou senha invalidos')

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   return redirect(url_for('index'))

if __name__ == "__main__":
	app.secret_key = 'XuysasdfagfdgfdfsgsdnnvdkjdtasdfrejmN]LWX/,?RT'
	app.run(debug=True,host='0.0.0.0')
