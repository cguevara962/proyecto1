import json
#import twilioclient_dia
# import flask dependencies
from flask import Flask
from flask import request
from flask import jsonify
import requests
import logging

import random
import argparse
import os
from collections import ChainMap

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

class DeepChainMap(ChainMap):
    'Variant of ChainMap that allows direct updates to inner scopes'

    def __setitem__(self, key, value):
        for mapping in self.maps:
            if key in mapping:
                mapping[key] = value
                return
        self.maps[0][key] = value

    def __delitem__(self, key):
        for mapping in self.maps:
            if key in mapping:
                del mapping[key]
                return
        raise KeyError(key)

global UsuarioPin 
UsuarioPin = DeepChainMap()

json_data = ''
user  = ''
header1 = {'X-Authy-API-Key': '0Vi2Sga5QoiwhFjjcB9uQEAcS8TziGKW'}
# initialize the flask app
app = Flask(__name__)

# default route

@app.route('/')
def index():
    return 'Hello World!'
# create a route for webhook



# create a route for webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    global user    
    global data
    global ret    
    # return response
    data = request.get_json(silent=True)
    session = data['session']
    #print(data)
    intent = data['queryResult']['intent']['displayName']
    print(intent)
    if intent == 'Valida usuario tel': 
        
        #indentificazione utente    
       print('identifica usuario 999')
       print(data)
       user = data['queryResult']['parameters']['UserID']
       print(user)
       session = data['session']
       print(session)
       r = requests.get("http://idesehp7.techedgegroup.co:8000/sap/bc/chguser", auth=('camilog', 'Techedge.2019'), params = {'operation': 'check_user_tel', 'user': user, 'sap-client':'800'})
# Imprimimos el resultado si el código de estado HTTP es 200 (OK):
       print(r.status_code)
       if r.status_code == 200:
              ret1 = r.headers['UserExistence']
              TelNo = r.headers['Telefono']
#              TelNo = '3015482085'
              print(ret1)
              if ret1 == 'OK':
                     context = session+'/contexts/UserIsValidatedTel'
                     context = "'outputContexts': [{ 'name': '"+context+"', 'lifespanCount': 5}]"
#                     message = 'L`utente esiste. Si inviará un codice SMS di verifica al '+TelNo+' inserisci il codice ricevuto'
                     message = 'Por favor complete el numero de telefono: '+TelNo
##                     ret =  "{ 'fulfillmentText':'L`utente esiste si inviará un codice SMS di verifica al ' , TelNo, ' inserisci il codice ricevuto','outputContexts': [{ 'name': '"+context+"', 'lifespanCount': 5}] }"
                     ret =  "{ 'fulfillmentText' : '" +  message + "'," + context + " }"
#                     sendVerifyUser('camilo.guevara@techedgegroup.com','3015482085',57)
              else:
                     ret =  jsonify({ 'fulfillmentText': 'El usuario indicado no existe' })
              #print(ret)
              #return ret            
        
    elif intent == 'Valida telefono':
        
        print('Validar telefono')
        user = data['queryResult']['outputContexts'][0]['parameters']['UserID']
        telefono = data['queryResult']['parameters']['Telefono']
        print(user)
        print(telefono)
        r = requests.get("http://idesehp7.techedgegroup.co:8000/sap/bc/chguser", auth=('camilog', 'Techedge.2019'), params = {'operation': 'check_tel', 'user': user, 'telefono': telefono, 'sap-client':'800'})
        print(r.status_code)
        if r.status_code == 200:
                #print(r.headers)
                ret1 = r.headers['TelefonoValid']
                print(ret1)
                if ret1 == 'OK':
                    context = session+'/contexts/TelefonoValided'
                    context = "'outputContexts': [{ 'name': '"+context+"', 'lifespanCount': 5}]"
                    message = 'Se enviara un pin de validacion al numero: '+telefono+' ingrese el código recibido'
                    ret =  "{ 'fulfillmentText' : '" +  message + "'," + context + " }"
                    sendVerifyUser('camilo.guevara@techedgegroup.com',telefono,57)
                else:
                    ret =  jsonify({ 'fulfillmentText': 'El numero de telefono no es correcto' })
                #print(ret)
                #return ret    
      
    elif intent == 'Validar pin telefono':
        
        #Validación PIN
       print('Validar pin tel')
       ValidationPIN = data['queryResult']['parameters']['Pin']
       retPIN = verifyPIN_tel(ValidationPIN)
       print(retPIN)
       if retPIN == True:
       #el PIN è validato. Si resetta la pwd.
              print('PIN Validado')
              r = requests.get("http://idesehp7.techedgegroup.co:8000/sap/bc/chguser", auth=('camilog', 'Techedge.2019'), params = {'operation': 'reset', 'user': user, 'sap-client':'800'})
              print(r.status_code)
              if r.status_code == 200:
                    password = r.headers['NewPassword']
                    ret1 = r.headers['ret1']
                    if ret1 == 'OK':
                            context = session+'/contexts/PinValidated'
                            context = "'outputContexts': [{ 'name': '"+context+"', 'lifespanCount': 5}]"
                            message = 'Se a validado correctamente el pin, el password generado es   ' + password 
                            ret =  "{ 'fulfillmentText' : '" +  message + "'," + context + " }"
                    else:
                            ret =  jsonify({ 'fulfillmentText': 'El pin no es correcto' }) 
        
    elif intent == 'Valida usuario email': 
        
       print('indentificazione utente')
       user = data['queryResult']['parameters']['UserID']
       print(user)
       session = data['session']
       print(session)
       r = requests.get("http://idesehp7.techedgegroup.co:8000/sap/bc/chguser", auth=('camilog', 'Techedge.2019'), params = {'operation': 'check_user_mail', 'user': user, 'sap-client':'800'})
# Imprimimos el resultado si el código de estado HTTP es 200 (OK):
       print(r.status_code)
       if r.status_code == 200:
              ret1 = r.headers['UserExistence']
              email = r.headers['Email']
              print(ret1)
              if ret1 == 'OK':
                     context = session+'/contexts/UserIsValidatedMail'
                     context = "'outputContexts': [{ 'name': '"+context+"', 'lifespanCount': 5}]"
                     message = 'Por favor complete el Email: '+email
                     ret =  "{ 'fulfillmentText' : '" +  message + "'," + context + " }"
              else:
                     ret =  jsonify({ 'fulfillmentText': 'El usuario indicado no existe' })
        
    elif intent == 'Valida email':
        
        print('Validar email')
        print(data['queryResult']['outputContexts'])
        index = len(data['queryResult']['outputContexts'])
        print(index)
        #user = data['queryResult']['outputContexts'][0]['parameters']['UserID']
        default = 'null'

        for x in data['queryResult']['outputContexts']:
            y=x.get('parameters', default)
            if y != 'null':
                for z in y:
                    if z == 'UserID':                
                        user = y['UserID']
                        break        
        email = data['queryResult']['parameters']['Email']
        print(user)
        print(user)
        r = requests.get("http://idesehp7.techedgegroup.co:8000/sap/bc/chguser", auth=('camilog', 'Techedge.2019'), params = {'operation': 'check_mail', 'user': user, 'email': email, 'sap-client':'800'})
        print(r.status_code)
        if r.status_code == 200:
                #print(r.headers)
                ret1 = r.headers['EmailValid']
                print(ret1)
                if ret1 == 'OK':
                    print('random')
                    r = random.randint(100000,999999)         # add data 
                    print(r)
                    print(email)
                    UsuarioPin[user] = r
                    
                    enviaMail(email,r)
                    
                    context = session+'/contexts/EmailValidated'
                    context = "'outputContexts': [{ 'name': '"+context+"', 'lifespanCount': 5}]"
                    message = 'Ha sido enviado un pin de validación al Email: '+email+' ingrese el código recibido'
                    ret =  "{ 'fulfillmentText' : '" +  message + "'," + context + " }"
                else:
                    ret =  jsonify({ 'fulfillmentText': 'El Email no es correcto' })
                #print(ret)
                #return ret    
      
    elif intent == 'Valida pin email':
        
        #Validación PIN
       print('Validar pin email')
       ValidationPIN = data['queryResult']['parameters']['Pin']
       #user = data['queryResult']['outputContexts'][0]['parameters']['UserID'] 
       default = 'null'

       for x in data['queryResult']['outputContexts']:
            y=x.get('parameters', default)
            if y != 'null':
                for z in y:
                    if z == 'UserID':                
                        user = y['UserID']
                        break
       if ValidationPIN == UsuarioPin[user]:
       #el PIN è validato. Si resetta la pwd.
              del UsuarioPin[user]  
              print('PIN Validado mail')
              r = requests.get("http://idesehp7.techedgegroup.co:8000/sap/bc/chguser", auth=('camilog', 'Techedge.2019'), params = {'operation': 'reset', 'user': user, 'sap-client':'800'})
              print(r.status_code)
              if r.status_code == 200:
                    password = r.headers['NewPassword']
                    ret1 = r.headers['ret1']
                    print('paso1')
                    if ret1 == 'OK':
                            context = session+'/contexts/PinValidated'
                            context = "'outputContexts': [{ 'name': '"+context+"', 'lifespanCount': 5}]"
                            message = 'Se a validado correctamente el pin, el password generado es   ' + password 
                            ret =  "{ 'fulfillmentText' : '" +  message + "'," + context + " }"
                    else:
                            ret =  jsonify({ 'fulfillmentText': 'El pin no es correcto' }) 
                            
       else:
                    ret =  jsonify({ 'fulfillmentText': 'El pin no es correcto' })                    
        
    print(ret)
    return ret    
        
# Fin de Webhook 

        
# deifinicion de funciones 

def enviaMail(email,pin):
    MY_ADDRESS = "camilo.guevara@thecedgegroup.com"
    PASSWORD = "mirandohaciaadelante2204"
    print ('message:')
    
    message = """From: From Python
To: To """ + email + """
Subject: Python: validacion de pin DialogFlow

Saludos,

Este es el pin de validacion """ + str(pin)
    
    print(message)
    
    s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    s.login("camilo.guevara@techedgegroup.com", "mirandohaciaadelante2204")
    s.sendmail(
      MY_ADDRESS,  #from
      email,             #to
      message )
    s.quit()

def sendVerifyUser(email,cellphone,country_code):
    global json_data   
    global header1
    url = 'https://api.authy.com/protected/json/users/new'

    

    payload = {'user[email]': email, 'user[cellphone]': cellphone, 'user[country_code]': country_code}
    r = requests.post(url, headers=header1, data=payload)
    json_data = json.loads(r.text)
    print(json_data)
    print(json_data["user"]["id"])


    url_sms =  'https://api.authy.com/protected/json/sms/' + str(json_data["user"]["id"] )
    url_sms =  url_sms + '?force=true' 
    print('url')
    print(url_sms)
    r1 = requests.get(url_sms, headers=header1) 
    json_data1 = json.loads(r1.text)
    print(json_data1)


def verifyPIN_tel(token):
    print('Validando pin tel')
    global json_data   
    global header1
    url_verify = 'https://api.authy.com/protected/json/verify/' +str(token)
    url_verify =  url_verify + '/'
    url_verify =  url_verify + str(json_data["user"]["id"] )

#    print('url verify')
#    print(url_verify)
    r2 = requests.get(url_verify, headers=header1) 

    json_data2 = json.loads(r2.text)
    
#    print(json_data2)
    if  json_data2['success'] == 'true':
       return True
    else:
       return False


def results():
    # build a request object
    req = request.get_json(force=True)
    # fetch action from json
    action = req.get('queryResult').get('action')
    # return a fulfillment response
    return {'fulfillmentText': 'This is a response from webhook.'}

if __name__ == '__main__':
  LOG_FILENAME = 'D:\camilog\documentos\Techedge\Dialogflow\errores.log'
  logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
  app.run()