#!/usr/bin/python
#-*- encoding: utf-8 -*-

import smtplib

from datetime import datetime
from email import Encoders
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.Utils import formatdate

from pymongo import MongoClient
import pymongo

#from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#Conectando ao banco MongoDB
cliente = MongoClient('localhost', 27017)
banco = cliente.iotdata
contatos = banco.contatos
contatos_ativos = contatos.find()

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
msg["Subject"] = "Email de contato"
texto = 'Email de contato\n'
part1 = MIMEText(texto, 'plain')
msg.attach(part1)

for t in contatos_ativos:
	linha1 = 'E-mail: ' + t['email'] + '\n'
	linha2 = 'Nome: : ' + t['nome'] + '\n'
	linha3 = t['msg']
	part2 = MIMEText(linha1+linha2+linha3, 'plain')
	msg.attach(part2)
	try:
		server.sendmail(mail_from, mail_to, msg.as_string())
	except Exception, e:
    		errorMsg = "Error: %s" % str(e)
    	print errorMsg

#libera recursos
server.close;




