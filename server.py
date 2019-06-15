#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect, url_for, request
import mysql.connector as mariadb
import requests
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

@app.route('/')
def index():
   return render_template('home.html')

@app.route('/success/<name>/<pwd>')
def success(name, pwd):
   return 'welcome %s %s' %(name, pwd) 

@app.route('/login',methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      login = request.form['login']
      password = request.form['password']
      if validasenha(login, password):      
         return redirect(url_for('success',name = login, pwd = password))
      else:
         return render_template('home.html', erro = True, login = login)   
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


      return redirect(url_for('success',name = login, pwd = cpassword))
   else:
      return render_template('home.html')

## DB ###############################################################


def validasenha(login, password):
   mariadb_connection = mariadb.connect(host=dbhost, port=dbport, user=dbuser, password=dbpwd, database=dbdata)
   cursor = mariadb_connection.cursor()
   
   cursor.execute("SELECT 1 FROM USUARIO WHERE LOGIN_USUARIO=%s AND SENHA_USUARIO=%s", (login, password))
   if cursor.fetchone():
      print("senha ok")
      ret = True
   else:
      print("senha invalida")
      ret = False
   
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
         payload = "{\n  \"query\" : \"create (usr1:USUARIO {id_usuario:'"+id+"', login_usuario:'"+login+"',nome_usuario:'"+name+"',dt_nascimento_usuario:'"+birthday+"',e_mail_usuario:'"+email+"',publicar:'S'})\",\n  \"params\" : { }\n}\n"   
      #insert no neo4j
      response = requests.request("POST", url, data=payload, headers=headers)
      print(response.text)

   mariadb_connection.close()
   return ret 

if __name__ == '__main__':
   app.run(debug = True)