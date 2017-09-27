from flask import Flask, request, Response, render_template, abort, redirect
#import time
from datetime import date, datetime, timedelta
from email.Utils import formatdate
from pymongo import MongoClient
import pymongo
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from werkzeug.security import check_password_hash

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

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


class User():
    def __init__(self, username):
        self.username = username
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return self.username
    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)

class LoginForm(FlaskForm):
    """Login form to access writing and settings pages"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


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

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = app.config['USERS_COLLECTION'].find_one({"_id": form.username.data})
        if user and User.validate_login(user['password'], form.password.data):
            user_obj = User(user['_id'])
            login_user(user_obj)
            flash("Logged in successfully!", category='success')
            return redirect(request.args.get("next") or url_for("write"))
        flash("Wrong username or password!", category='error')
    return render_template('login.html', title='login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/write', methods=['GET', 'POST'])
@login_required
def write():
    return render_template('write.html')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')


@login_manager.user_loader
def load_user(username):
    u = app.config['USERS_COLLECTION'].find_one({"_id": username})
    if not u:
        return None
    return User(u['_id'])

if __name__ == "__main__":
	app.run(host='0.0.0.0')
