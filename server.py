#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect, url_for, request, make_response
import mysql.connector as mariadb
import requests
import datetime
from Crypto.Cipher import AES
import pybase64

app = Flask(__name__)

#
#sudo docker run  --publish=7474:7474 --publish=7687:7687 -v $HOME/neo4j/data:/data -v $HOME/neo4j/import:/import  neo4j
dbuser='root'
dbpwd='example'
dbhost='localhost'
dbport='8084'
dbdata='imdbfriends'
url = "http://localhost:7474/db/data/cypher"
headers = {
      'Content-Type': "application/json",
      'Accept': "application/json; charset=UTF-8",
      'Authorization': "Basic bmVvNGo6bmVvNGoy",
      'cache-control': "no-cache",
      'Postman-Token': "cabdfe37-849c-4aac-9b1a-65be296af5bd"
      }
salt = '!%F=-?Jc3301'
key32 = "{: <32}".format(salt).encode("utf-8")
cipher = AES.new(key32, AES.MODE_ECB)

@app.route('/')
def index():
   return render_template('home.html')

@app.route('/filmes/<data>')
def filmes(data):

   decoded = cipher.decrypt(pybase64.urlsafe_b64decode(data))
   dado = decoded.strip().split(",")

   dt = dado[2].split("/")
   niver = dt[2]+"-"+dt[1]+"-"+dt[0]
   

   resp = make_response(render_template('filmes.html',clogin = dado[0], name = dado[1], birthday = niver, email = dado[3] ))
   resp.set_cookie('login', dado[0])
   resp.set_cookie('name', dado[1])
   resp.set_cookie('birthday', dado[2])
   resp.set_cookie('email', dado[3])
   return resp
   # return 'welcome %s %s' %(dado[3], dado[1]) 


@app.route('/updateuser/<login>',methods = ['POST', 'GET'])
def updateuser(login):
   if request.method == 'POST':
      name = request.form['name']
      birthday = request.form['birthday']
      email = request.form['email']

      if updateuserNOK(login, name, birthday, email):      
         return "Erro ao atualizar"

      print("Atualizado com sucesso")

      chunck = login+","+name+","+tdata(birthday)+","+email

      print(chunck)

      if (len(chunck)%16!=0):
         chunck+= ' ' * (16-len(chunck)%16)         
      encoded = pybase64.urlsafe_b64encode(cipher.encrypt(chunck))
      return redirect(url_for('filmes',data = encoded))
   else:
      return "Metodo invalido"



@app.route('/login',methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      login = request.form['login']
      password = request.form['password']

      dados = validasenha(login, password)

      if len(dados) > 0:      
         chunck = dados
         if (len(chunck)%16!=0):
            chunck+= ' ' * (16-len(chunck)%16)         
         encoded = pybase64.urlsafe_b64encode(cipher.encrypt(chunck))
         return redirect(url_for('filmes',data = encoded))
      else:
         return render_template('filmes.html', erro = True, login = login)   
   else:
      return render_template('home.html')

@app.route('/adduser',methods = ['POST', 'GET'])
def adduser():
   if request.method == 'POST':
      login = request.form['clogin']
      name = request.form['name']
      birthday = request.form['birthday']
      email = request.form['email']
      cpassword = request.form['cpassword']
      ccpassword = request.form['ccpassword']

      if login_invalido(login):
         return render_template('home.html', errologin = True, clogin = login, name=name, birthday=birthday, email=email, cpassword=cpassword, ccpassword=ccpassword)

      if cpassword <> ccpassword:
         return render_template('home.html', erropasswd = True, clogin = login, name=name, birthday=birthday, email=email, cpassword=cpassword, ccpassword=ccpassword)

      if adduserNOK(login, name, birthday, email, cpassword):
         return render_template('home.html', erroadd = True, clogin = login, name=name, birthday=birthday, email=email, cpassword=cpassword, ccpassword=ccpassword)

      # resp = make_response(render_template('filmes.html'))
      # resp.set_cookie('login', login)
      # resp.set_cookie('name', name)
      # resp.set_cookie('birthday', birthday)
      # resp.set_cookie('email', email)

      return redirect(url_for('filmes',login = login, name = name, birthday = birthday,email = email ))
   else:
      return render_template('home.html')

## DB ###############################################################


def validasenha(login, password):
   mariadb_connection = mariadb.connect(host=dbhost, port=dbport, user=dbuser, password=dbpwd, database=dbdata)
   cursor = mariadb_connection.cursor()
   ret = ""

   cursor.execute("SELECT LOGIN_USUARIO,NOME_USUARIO,DT_NASCIMENTO_USUARIO,E_MAIL_USUARIO FROM USUARIO WHERE LOGIN_USUARIO=%s AND SENHA_USUARIO=%s", (login, password))
   
   for LOGIN_USUARIO, NOME_USUARIO, DT_NASCIMENTO_USUARIO, E_MAIL_USUARIO in cursor:
      ret = LOGIN_USUARIO+","+NOME_USUARIO+","+DT_NASCIMENTO_USUARIO.strftime('%m/%d/%Y')+","+E_MAIL_USUARIO
      print("senha ok")      
    
   mariadb_connection.close()
   return ret   

def login_invalido(login):
   mariadb_connection = mariadb.connect(host=dbhost, port=dbport, user=dbuser, password=dbpwd, database=dbdata)
   cursor = mariadb_connection.cursor()
   
   cursor.execute("SELECT 1 FROM USUARIO WHERE LOGIN_USUARIO=%s", (login,))
   if cursor.fetchone():
      print(login + " ja existe")
      ret = True
   else:
      print("login valido")
      ret = False
   
   mariadb_connection.close()
   return ret 

def adduserNOK(login, name, birthday, email, cpassword):
   mariadb_connection = mariadb.connect(host=dbhost, port=dbport, user=dbuser, password=dbpwd, database=dbdata)
   cursor = mariadb_connection.cursor()
   ret = False
   #insert na mariadb
   try:
      cursor.execute("INSERT INTO USUARIO (LOGIN_USUARIO,NOME_USUARIO,DT_NASCIMENTO_USUARIO,E_MAIL_USUARIO,SENHA_INI,SENHA_USUARIO,PUBLICAR) VALUES (%s,%s,%s,%s,%s,%s,%s)", (login, name, birthday, email, 'S',cpassword,'S'))
   except mariadb.Error as error:
      print("Error: {}".format(error))
      ret = True

   mariadb_connection.commit()
   print "The last inserted id was: ", cursor.lastrowid   

   if ret == False:
      cursor.execute("SELECT ID_USUARIO FROM USUARIO WHERE LOGIN_USUARIO=%s", (login,))
      for ID_USUARIO in cursor:
         id=str(ID_USUARIO).replace("(","").replace(",)","")
         #insert no neo4j
         payload = "{\n  \"query\" : \"create (usr1:USUARIO {id_usuario:'"+id+"', login_usuario:'"+login+"',nome_usuario:'"+name+"',dt_nascimento_usuario:'"+tdata(birthday)+"',e_mail_usuario:'"+email+"',publicar:'S'})\",\n  \"params\" : { }\n}\n"   
      response = requests.request("POST", url, data=payload, headers=headers)
      print(response.text)

   mariadb_connection.close()
   return ret 

def updateuserNOK(login, name, birthday, email):
   mariadb_connection = mariadb.connect(host=dbhost, port=dbport, user=dbuser, password=dbpwd, database=dbdata)
   cursor = mariadb_connection.cursor()
   ret = False
   #update na mariadb
   try:
      cursor.execute("UPDATE USUARIO SET NOME_USUARIO = %s, DT_NASCIMENTO_USUARIO = %s, E_MAIL_USUARIO = %s WHERE LOGIN_USUARIO=%s", (name, birthday, email, login))
   except mariadb.Error as error:
      print("Error: {}".format(error))
      ret = True

   mariadb_connection.commit()
   print "The last inserted id was: ", cursor.lastrowid   

   if ret == False:
      #update no neo4j
      payload = "{\n  \"query\" : \"match (u:USUARIO{login_usuario:'"+login+"'}) WITH u, u {.*} as snapshot SET u.nome_usuario = '"+name+"' SET u.dt_nascimento_usuario = '"+tdata(birthday)+"' SET u.e_mail_usuario = '"+email+"' RETURN snapshot\",\n  \"params\" : { }\n}\n"
      response = requests.request("POST", url, data=payload, headers=headers)
      print(response.text)

   mariadb_connection.close()
   return ret 

def tdata(data):
   dt = data.split("-")
   datat = dt[2]+"/"+dt[1]+"/"+dt[0]
   return datat


if __name__ == '__main__':
   app.run(debug = True)