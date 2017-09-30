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

USERS = (("user1", "pass1"),
		  ("cleiton", "teste")
		  )

# silly user model
#class User(UserMixin):
# 	def __init__(self, id):
#		self.id = id
#		self.name = "user" + str(id)
#		self.password = self.name + "_secret"
#
#	def __repr__(self):
#		return "%d/%s/%s" % (self.id, self.name, self.password)

class User(UserMixin):
	"""
	User Class for flask-Login
	"""
	def __init__(self, userid, password):
		self.id = userid
		self.password = password

	@staticmethod
	def get(userid):
		"""
		Static method to search the database and see if userid exists.  If it
		does exist then return a User Object.  If not then return None as
		required by Flask-Login.
		"""
		#For this example the USERS database is a list consisting of
		#(user,hased_password) of users.
		for user in USERS:
			if user[0] == userid:
				return User(user[0], user[1])
		return None

def hash_pass(password):
	"""
	Return the md5 hash of the password+salt
	"""
	salted_password = password + app.secret_key
	return md5.new(salted_password).hexdigest()

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
							sensorname	  = sensor.upper())


@app.route("/conf/<sensor>")
@login_required
def configuracao(sensor):
	msg = 'Sensor: ' +sensor

	paritens = ['15','30','20','50','alerta@ioterm.com.br']
	if request.method == 'GET':
		return render_template("settings.html",parametros=paritens,max=30,sensorname=sensor.upper())
##	if request.method == 'POST':
##		set_min = request.form['temp_min']
##		curs2.execute('UPDATE parametros SET valor = %d where parametro = %s' % (int(set_min),"'LIMITE_MIN_TEMP'"))
##		set_max = request.form['temp_max']
##		curs2.execute('UPDATE parametros SET valor = %d where parametro = %s' % (int(set_max),"'LIMITE_MAX_TEMP'"))
##		conn2.commit()
##		conn2.close()
##		return redirect('/lab_parametros')

# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == 'POST':
		#username = request.form['username']
		#password = request.form['password']
		user = User.get(request.form['username'])
		#print user.username
		if user and request.form['password'] == user.password:
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
	"""
	Flask-Login user_loader callback.
	The user_loader function asks this function to get a User Object or return
	None based on the userid.
	The userid was stored in the session environment by Flask-Login.
	user_loader stores the returned User object in current_user during every
	flask request.
	"""
	return User.get(userid)

if __name__ == "__main__":
	
	app.run(host='0.0.0.0')
