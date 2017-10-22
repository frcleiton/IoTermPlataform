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

def enviar_email(_mensagem):
	#Define o servidor de e-mail
	server=smtplib.SMTP()
	smtpserver="sharedrelay-cluster.mandic.net.br"
	#smtpserver="177.70.110.120"
	server.connect(smtpserver,587)
	server.login('ticimed@shared.mandic.net.br','cimed@2015')
	mail_from = 'pi@ioterm.com.br'
	mail_to = 'cleitonrferreira@gmail.com'

	msg = MIMEMultipart()
	msg["From"] = mail_from
	msg["To"] = mail_to
	msg['Date']  = formatdate(localtime=True)
	msg["Subject"] = "Alertas"
	texto = 'Email de IoTerm\n'
	part1 = MIMEText(texto + _mensagem, 'plain')
	msg.attach(part1)
	try:
		server.sendmail(mail_from, mail_to, msg.as_string())
		print 'email enviado com sucesso'
		print msg
	except Exception, e:
		errorMsg = "Error: %s" % str(e)
		print errorMsg

def main():
	#Conectando ao banco MongoDB
	cliente = MongoClient('localhost', 27017)
	banco = cliente.iotdata
	collection_alarmes = banco.alarmes
	collection_contatos = banco.contatos
	alarmes = collection_alarmes.find()
	contatos = collection_contatos.find( {'enviado': False} )
	if alarmes.count():
		enviar_email(dumps(alarmes, indent=4, sort_keys=True))
	if contatos.count():
		enviar_email(dumps(contatos, indent=4, sort_keys=True))
		collection_contatos.update_many({ 'enviado': False },{ '$set': { 'enviado' : True }} )

if __name__ == '__main__':
    main()
