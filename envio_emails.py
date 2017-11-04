#!/usr/bin/python
#-*- encoding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      frcleiton
#
# Created:     17/10/2017
# Copyright:   (c) frcleiton 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import smtplib
from datetime import datetime
from email import Encoders
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.Utils import formatdate
from email.mime.text import MIMEText
from pymongo import MongoClient
import pymongo
from bson.json_util import dumps
import ConfigParser

def enviar_email(alarm):
	config = ConfigParser.ConfigParser()
	config.read('email.cfg')
	SMTP_SERVER     = config.get('config','smtpserver')
	SMTP_USER       = config.get('config','smtpuser')
	SMTP_PASS       = config.get('config','smtppass')
	_MAIL_FROM		= config.get('config','mailfrom')
	
	#Define o servidor de e-mail
	server=smtplib.SMTP()
	smtpserver=SMTP_SERVER
	server.connect(smtpserver,587)
	server.login(SMTP_USER, SMTP_PASS)
	mail_from = _MAIL_FROM
	mail_to = alarm['mail']

	msg = MIMEMultipart()
	msg["From"] = mail_from
	msg["To"] = mail_to
	msg['Date']  = formatdate(localtime=True)
	msg["Subject"] = "Alarme sensor " + alarm['sensor']
	texto = alarm['descricao'] + '\n\n'
	texto += 'Nome do sensor:   ' + alarm['sensor'] + '\n'
	texto += 'Data de criacao:  ' + alarm['createdAt'].strftime("%Y-%m-%d %H:%M") + '\n'
	texto += 'Parametro minimo: ' + alarm['minima'] + '\n'
	texto += 'Parametro maximo: ' + alarm['maxima'] + '\n'
	texto += 'Valor lido:       ' + str(alarm['leitura']) + '\n'
	part1 = MIMEText(texto, 'plain')
	msg.attach(part1)
	try:
		server.sendmail(mail_from, mail_to, msg.as_string())
		print 'email enviado com sucesso'
		print msg
	except Exception, e:
		errorMsg = "Error: %s" % str(e)
		print errorMsg
	server.close()

def main():
	#Conectando ao banco MongoDB
	cliente = MongoClient('localhost', 27017)
	banco = cliente.iotdata
	collection_alarmes = banco.alarmes
	collection_contatos = banco.contatos
	alarmes = collection_alarmes.find()
	contatos = collection_contatos.find( {'enviado': False} )
	for alarm in alarmes:
		enviar_email(alarm)
		

if __name__ == '__main__':
    main()
