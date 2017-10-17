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

#Conectando ao banco MongoDB
cliente = MongoClient('localhost', 27017)
banco = cliente.iotdata
coll_conf = banco.configuracoes
coll_alarmes = banco.alarmes
configuracoes = coll_conf.find()


def get_ultima_leitura(sensor):
    topico_temp = sensor+'/temperature'
    topico_humi = sensor+'/humidity'
    coll_leituras = banco.leituras
    ultima_leitura_temp = coll_leituras.find( {'topic':topico_temp} ).sort('t', pymongo.DESCENDING).limit(1)
    ultima_leitura_humi = coll_leituras.find( {'topic':topico_humi} ).sort('t', pymongo.DESCENDING).limit(1)
    return (ultima_leitura_temp[0]['value'], ultima_leitura_humi[0]['value'])

def evento_alarme(sensor, msg, parametros, valor):
    evt_alarme = {}
    evt_alarme['descricao'] = msg
    evt_alarme['sensor']    = sensor
    evt_alarme['createdAt'] = datetime.now()
    coll_alarmes.save(evt_alarme)


def main():

    #gera um evento de alarme
    for c in configuracoes:
        sensor  = c['sensor']
        tempmin = int(c['tempmin'])
        tempmax = int(c['tempmax'])
        hummin  = int(c['hummin'])
        hummax  = int(c['hummax'])
        mail    = c['email']

        temp, humi = get_ultima_leitura(sensor)
        print type(temp)
        print temp
        print type(tempmin)
        print tempmin


        print humi
        if (tempmin < temp < tempmax):
            print 'alarme temp'
            evento_alarme(sensor, 'Temperatura fora dos parametros', c, temp)
        if (hummin < humi < hummax):
            print 'alarme umi'
            evento_alarme(sensor, 'Umidade fora dos parametros', c, humi)

if __name__ == '__main__':
    main()
