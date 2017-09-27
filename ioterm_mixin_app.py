from flask import Flask, request, Response, render_template, abort, redirect, url_for
#import time
from datetime import date, datetime, timedelta
from email.Utils import formatdate
from pymongo import MongoClient
import pymongo
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user

app = Flask(__name__)

# config
app.config.update(
    DEBUG = True,
    SECRET_KEY = 'i0t3rm!@#$%',
)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# silly user model
class User(UserMixin):
 	def __init__(self, id):
		self.id = id
		self.name = "user" + str(id)
		self.password = self.name + "_secret"

	def __repr__(self):
		return "%d/%s/%s" % (self.id, self.name, self.password)

# Test user
#users = [User(id) for id in range(1, 21)]
#users.append(User(21))
#users = []
#users.append(User(1))
#print users


@app.route("/")
@login_required
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
@login_required
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

	print registros

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
@login_required
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

# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'user1' and password == 'user1_secret':
            id = username.split('user')[1]
            print id
            user = User(id)
            login_user(user)
            return redirect(request.args.get("next") or url_for("index"))
        else:
            return abort(401)
    else:
		return render_template('login.html')

# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')


# callback to reload the user object
@login_manager.user_loader
def load_user(userid):
    return User(userid)

if __name__ == "__main__":
	app.run(host='0.0.0.0')
