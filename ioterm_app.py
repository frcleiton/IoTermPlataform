from flask import Flask, request, Response, render_template, abort, redirect, url_for, flash, session
import time
from datetime import date, datetime, timedelta
from email.Utils import formatdate
from pymongo import MongoClient
import pymongo
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from bson.objectid import ObjectId

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

USERS = (("cleiton", "teste"),
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
@app.route("/home")
def home():
	return render_template("home.html")

@app.route("/dashboard")
def index():
	#Conectando ao banco MongoDB
	cliente = MongoClient('localhost', 27017)
	banco = cliente.iotdata
	leituras = banco.leituras
	alarmes = banco.alarmes

	#Busca o valor da ultima leitura por topico/dispositivo
	temperatures = []
	humidities = []
	strdatetime = []
	str_time = []
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
	alarmes_ativos = alarmes.find().count()
	
	if (len(temperatures) > 0):
		return render_template("sensors.html",temp=temperatures,hum=humidities,str_time=strdatetime,nalert=alarmes_ativos)
	else:
		return abort(404)

@app.route("/hist/<sensor>", methods=['GET'])
def historico(sensor):
	msg = 'Sensor: ' +sensor

	#Conectando ao banco MongoDB
	cliente = MongoClient('localhost', 27017)
	banco = cliente.iotdata
	leituras = banco.leituras

	yesterday = datetime.now() - timedelta(days=1)
	today = datetime.now()

	if request.args.has_key('from'):
	   from_date_str = request.args.get('from',time.strftime("%Y-%m-%d 00:00")) #Get the from date value from the URL
	   to_date_str 	= request.args.get('to',time.strftime("%Y-%m-%d %H:%M"))   #Get the to date value from the URL
	   yesterday = datetime.strptime(from_date_str, '%Y-%m-%d %H:%M')
	   today = datetime.strptime(to_date_str, '%Y-%m-%d %H:%M')
	else:
	   from_date_str = yesterday.strftime("%Y-%m-%d %H:%M")
	   to_date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

	topico = sensor.upper() + '/temperature'
	intervalo_leituras = leituras.find( {'topic': topico, 't': {'$gte':yesterday, '$lte':today}} ).sort('t', pymongo.DESCENDING )
	registros = []
	i = 0
	for registro in intervalo_leituras:
		d = registro['t']
		js_formato = int(time.mktime(d.timetuple())) * 1000
		if (i % 5 == 0):
			registros.append([js_formato,registro['t'],registro['value']])
		i += 1

	return render_template("historico.html",
							temp 			= registros,
							from_date 		= from_date_str,
							to_date 		= to_date_str,
							sensorname	  	= sensor.upper(),
							cont = len(registros))



							
@app.route("/roconf/<sensor>", methods=["GET"])
def roconfiguracao(sensor):
	msg = 'Sensor: ' +sensor
	
	if current_user.is_authenticated:
		return redirect('/conf/'+sensor)
	
	#Conectando ao banco MongoDB
	cliente = MongoClient('localhost', 27017)
	banco = cliente.iotdata
	configuracoes = banco.configuracoes
	
	#le as configuracoes
	confs = configuracoes.find_one( {'sensor': sensor.upper() } )
	return render_template("rosettings.html",parametros=confs,max=30,sensorname=sensor.upper())
								
@app.route("/conf/<sensor>", methods=["GET", "POST"])
@login_required
def configuracao(sensor):
	msg = 'Sensor: ' +sensor
	
	#Conectando ao banco MongoDB
	cliente = MongoClient('localhost', 27017)
	banco = cliente.iotdata
	configuracoes = banco.configuracoes
	
	#le as configuracoes ou instancia uma nova
	confs = configuracoes.find_one( {'sensor': sensor.upper() } )
	if not confs:
		confs = { 'sensor':sensor }

	if request.method == 'GET':
		return render_template("settings.html",parametros=confs,max=30,sensorname=sensor.upper())
	if request.method == 'POST':
		confs['tempmin'] = request.form['temp_min']
		confs['tempmax'] = request.form['temp_max']
		confs['hummin']  = request.form['umid_min']
		confs['hummax']  = request.form['umid_max']
		confs['email'] 	 = request.form['emailAlerta']
		configuracoes.save(confs)
		flash('Parametros atualizados','success')
		return redirect('/conf/'+sensor)
		
@app.route("/alarmes", methods=["GET", "POST"])
def alarmes():
	#Conectando ao banco MongoDB
	cliente = MongoClient('localhost', 27017)
	banco = cliente.iotdata
	alarmes = banco.alarmes
	
	#le os alarmes ativos
	alarmes_ativos = alarmes.find()
	
	if request.method == 'GET':
		return render_template("alarmes.html",alarmes=alarmes_ativos)
	
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
			return redirect(request.args.get('next') or url_for('index'))
		else:
			return abort(401)
	else:
		return render_template('login.html')

# somewhere to logout
@app.route("/logout")
@login_required
def logout():
	logout_user()
	session.clear()
	return redirect(url_for('index'))
	
# handle login failed
@app.errorhandler(401)
def login_failed(e):
	return Response('<p>Login failed</p>')

# handle data not found
@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404


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
