#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      frcleiton
#
# Created:     24/09/2017
# Copyright:   (c) frcleiton 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from flask import Flask, request, Response, render_template
#import time
from datetime import datetime
from email.Utils import formatdate
from pymongo import MongoClient
import pymongo

def main():
	cliente = MongoClient('localhost', 27017)
	banco = cliente.iotdata
	leituras = banco.leituras
	registros = []

	cont=0
	for registro in leituras.find( {'topic':'RP01/temperature'} ).sort('t', pymongo.DESCENDING ).limit(1440):
	   cont+=1
	   if (cont % 10) == 0:
		   registros.append([registro['t'].strftime("%d-%m-%Y %H:%M"),registro['value']])
	   	   print registro

if __name__ == '__main__':
	main()
