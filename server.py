#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect, url_for, request, make_response
import mysql.connector as mariadb
import json
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

@app.route('/filmes')
def filmes():

   dado = getCookies()
   dt = dado[2].split("/")
   niver = dt[2]+"-"+dt[1]+"-"+dt[0]
   
   idUser = dado[4]
   nmMovie = dado[5]
   yearMovie = dado[6]
   skip = "0"
   movies = listMovies(idUser, nmMovie, yearMovie, skip)
   recomMovies = recommendMovie(idUser)
   recomPeoples = recommendPeople(idUser)

   resp = make_response(render_template('filmes.html',clogin = dado[0], name = dado[1], birthday = niver, email = dado[3], movies = movies, recomMovies = recomMovies, recomPeoples = recomPeoples, nmMovie = nmMovie, yearMovie = yearMovie))
   return resp

@app.route('/filtro',methods = ['POST'])
def filtro():

   dado = getCookies()

   nmMovie = request.form['nmMovie']
   yearMovie = request.form['yearMovie']

   chunck = dado[0]+","+dado[1]+","+dado[2]+","+dado[3]+","+dado[4]+","+nmMovie+","+yearMovie
   resp = make_response(redirect(url_for('filmes')))
   resp.set_cookie('dd', encondeDD(chunck))
   return resp


@app.route('/updateuser/<login>',methods = ['POST', 'GET'])
def updateuser(login):
   if request.method == 'POST':
      dado = getCookies()
      name = request.form['name']
      birthday = request.form['birthday']
      email = request.form['email']

      if updateuserNOK(login, name, birthday, email):      
         return "Erro ao atualizar"

      print("Atualizado com sucesso")

      chunck = login+","+name+","+tdata(birthday)+","+email+","+dado[4]+","+","
      resp = make_response(redirect(url_for('filmes')))
      resp.set_cookie('dd', encondeDD(chunck))
      return resp
   else:
      return "Metodo invalido"

@app.route('/updatepass',methods = ['POST', 'GET'])
def updatepass():
   if request.method == 'POST':
      dado = getCookies()
      login = dado[0]
      password = request.form['password']
      cpassword = request.form['cpassword']
      ccpassword = request.form['ccpassword']

      dados = validasenha(login, password)

      if len(dados) == 0:      
         return "senha invalida"

      if cpassword <> ccpassword:      
         return "senha nova nao confere"

      #metodo atualizar senha
      if updatepassDbNOK(login, cpassword):
         return "falha na atualizacao da senha"

      print("Senha atualizada com sucesso! %s %s %s %s" % (login, password, cpassword, ccpassword))
      resp = make_response(redirect(url_for('filmes')))
      return resp
   else:
      return "Metodo invalido"



@app.route('/movie-avaliation',methods = ['POST', 'GET'])
def movieAvaliation():
   if request.method == 'POST':
      dado = getCookies()
      idUser = dado[4]
      idFilme = request.form['idFilme']
      nota = request.form['nota']
      resenha = request.form['resenha']
      dtIniAssistiu = request.form['dtIniAssistiu']
      dtFimAssistiu = request.form['dtFimAssistiu']

      print("entrada! %s - %s - %s - %s - %s - %s" % (idUser, idFilme, resenha, dtIniAssistiu, dtFimAssistiu, nota))

      if updateMovieAvalDB(idUser, idFilme, dtIniAssistiu, dtFimAssistiu, resenha, nota):      
         print("Filme Avaliado com sucesso! %s - %s - %s - %s - %s" % (nota, idFilme, resenha, dtIniAssistiu, dtFimAssistiu))

      resp = make_response(redirect(url_for('filmes')))
      return resp
   else:
      return "Metodo invalido"

@app.route('/del-movie-avaliation/<idFilme>',methods = ['POST', 'GET'])
def delMovieAvaliation(idFilme):
   if request.method == 'POST':
      dado = getCookies()
      idUser = dado[4]

      print("DELETAR: U %s - F %s " % (idUser, idFilme))

      if delMovieAvaliationDB(idUser, idFilme):      
         print("Avaliacao deletada com sucesso! %s - %s" % (idUser, idFilme))

      resp = make_response(redirect(url_for('filmes')))
      return resp
   else:
      return "Metodo invalido"


@app.route('/login',methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      login = request.form['login']
      password = request.form['password']

      dados = validasenha(login, password)

      if len(dados) > 0:      
         chunck = dados+","+","
         resp = make_response(redirect(url_for('filmes')))
         resp.set_cookie('dd', encondeDD(chunck))
         return resp
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

      idUser = adduserDB(login, name, birthday, email, cpassword)
      if len(idUser) == 0:
         return render_template('home.html', erroadd = True, clogin = login, name=name, birthday=birthday, email=email, cpassword=cpassword, ccpassword=ccpassword)

      chunck = login+","+name+","+tdata(birthday)+","+email+","+idUser+","+","
      resp = make_response(redirect(url_for('filmes')))
      resp.set_cookie('dd', encondeDD(chunck))
      return resp
   else:
      return render_template('home.html')

## DB ###############################################################


def validasenha(login, password):
   mariadb_connection = mariadb.connect(host=dbhost, port=dbport, user=dbuser, password=dbpwd, database=dbdata)
   cursor = mariadb_connection.cursor()
   ret = ""

   cursor.execute("SELECT LOGIN_USUARIO,NOME_USUARIO,DT_NASCIMENTO_USUARIO,E_MAIL_USUARIO,ID_USUARIO FROM USUARIO WHERE LOGIN_USUARIO=%s AND SENHA_USUARIO=%s", (login, password))
   
   for LOGIN_USUARIO, NOME_USUARIO, DT_NASCIMENTO_USUARIO, E_MAIL_USUARIO, ID_USUARIO in cursor:
      ret = LOGIN_USUARIO+","+NOME_USUARIO+","+DT_NASCIMENTO_USUARIO.strftime('%m/%d/%Y')+","+E_MAIL_USUARIO+","+intToStr(ID_USUARIO)
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

def adduserDB(login, name, birthday, email, cpassword):
   mariadb_connection = mariadb.connect(host=dbhost, port=dbport, user=dbuser, password=dbpwd, database=dbdata)
   cursor = mariadb_connection.cursor()
   ret = ''
   #insert na mariadb
   try:
      cursor.execute("INSERT INTO USUARIO (LOGIN_USUARIO,NOME_USUARIO,DT_NASCIMENTO_USUARIO,E_MAIL_USUARIO,SENHA_INI,SENHA_USUARIO,PUBLICAR) VALUES (%s,%s,%s,%s,%s,%s,%s)", (login, name, birthday, email, 'S',cpassword,'S'))
   except mariadb.Error as error:
      print("Error: {}".format(error))

   mariadb_connection.commit()
   print "The last inserted id was: ", cursor.lastrowid   

   cursor.execute("SELECT ID_USUARIO FROM USUARIO WHERE LOGIN_USUARIO=%s", (login,))
   for ID_USUARIO in cursor:
      idUser= intToStr(ID_USUARIO)
      ret = idUser
      #insert no neo4j
      payload = "{\n  \"query\" : \"create (usr1:USUARIO {id_usuario:"+idUser+", login_usuario:'"+login+"',nome_usuario:'"+name+"',dt_nascimento_usuario:'"+tdata(birthday)+"',e_mail_usuario:'"+email+"',publicar:'S'})\",\n  \"params\" : { }\n}\n"   
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

def updatepassDbNOK(login, cpassword):
   mariadb_connection = mariadb.connect(host=dbhost, port=dbport, user=dbuser, password=dbpwd, database=dbdata)
   cursor = mariadb_connection.cursor()
   ret = False
   #update na mariadb
   try:
      cursor.execute("UPDATE USUARIO SET SENHA_USUARIO = %s WHERE LOGIN_USUARIO = %s", (cpassword, login))
   except mariadb.Error as error:
      print("Error: {}".format(error))
      ret = True

   mariadb_connection.commit()
   mariadb_connection.close()
   return ret

def listMovies(idUser, nmMovie, yyMovie, skip):
   mariadb_connection = mariadb.connect(host=dbhost, port=dbport, user=dbuser, password=dbpwd, database=dbdata)
   cursor = mariadb_connection.cursor()

   ret = "["
   query="SELECT F.ID_FILME, NOME_FILME, ANO_LANC_FILME, NOTA FROM FILME_SERIE F LEFT JOIN ( SELECT * FROM USUARIO_ASSISTIU WHERE ID_USUARIO = %s) AS U ON F.ID_FILME = U.ID_FILME WHERE F.NOME_FILME LIKE '%%%s%%' AND ANO_LANC_FILME LIKE '%%%s%%'  ORDER BY F.NOME_FILME" % (idUser, nmMovie, yyMovie)
   #query="SELECT F.ID_FILME, NOME_FILME, ANO_LANC_FILME, NOTA FROM FILME_SERIE F LEFT JOIN ( SELECT * FROM USUARIO_ASSISTIU WHERE ID_USUARIO = %s ) AS U ON F.ID_FILME = U.ID_FILME WHERE F.NOME_FILME LIKE '%%%s%%' AND ANO_LANC_FILME LIKE '%%%s%%' ORDER BY F.NOME_FILME LIMIT %s, 10" % (idUser, nmMovie, yyMovie, skip)

   cursor.execute(query)
   for ID_FILME, NOME_FILME, ANO_LANC_FILME, NOTA in cursor:
      if ret <> "[":
         ret += "," 

      notaa = intToStr(NOTA)
      delete = "delete"
      if NOTA is None:
         notaa = ""  
         delete = ""
      ret += "{\"idFilme\":\""+intToStr(ID_FILME)+"\",\"nome\":\""+NOME_FILME+"\",\"ano\":\""+intToStr(ANO_LANC_FILME)+"\",\"nota\":\""+notaa+"\",\"delete\":\""+delete+"\"}"
   
   ret += "]"
   #print(ret)    
   mariadb_connection.close()
   return json.loads(ret) 

def updateMovieAvalDB(idUser, idFilme, dtIniAssistiu, dtFimAssistiu, resenha, nota):      
   mariadb_connection = mariadb.connect(host=dbhost, port=dbport, user=dbuser, password=dbpwd, database=dbdata)
   cursor = mariadb_connection.cursor()
   ret = True
   #insert na mariadb
   try:
      cursor.execute("INSERT INTO USUARIO_ASSISTIU (ID_USUARIO,ID_FILME,DT_INI_ASSISTIDO,DT_FIM_ASSISTIDO,RESENHA,NOTA)VALUES(%s,%s,%s,%s,%s,%s)", (idUser, idFilme, dtIniAssistiu, dtFimAssistiu, resenha, nota))
   except mariadb.Error as error:
      print("Error: {}".format(error))
      ret = False

   mariadb_connection.commit()
   print "The last inserted id was: ", cursor.lastrowid   

   #Inclui relacionamento no neo4j
   payload = "{\n  \"query\" : \"match (usr:USUARIO {id_usuario:%s}),(filme:FILMES_SERIES {id_filme:%s}) merge (usr)-[:ASSISTIU {dt_ini_assistido:'%s', dt_fim_assistido:'%s', resenha:'%s', nota:%s}]->(filme)\",\n  \"params\" : { }\n}\n"  % (idUser, idFilme, tdata(dtIniAssistiu), tdata(dtFimAssistiu), resenha, nota)
   response = requests.request("POST", url, data=payload, headers=headers)
   print(response.text)

   mariadb_connection.close()
   return ret 

def delMovieAvaliationDB(idUser, idFilme):      
   mariadb_connection = mariadb.connect(host=dbhost, port=dbport, user=dbuser, password=dbpwd, database=dbdata)
   cursor = mariadb_connection.cursor()
   ret = True
   #eclui na mariadb
   try:
      cursor.execute("DELETE FROM USUARIO_ASSISTIU WHERE ID_USUARIO = %s AND ID_FILME =%s", (idUser, idFilme))
   except mariadb.Error as error:
      print("Error: {}".format(error))
      ret = False

   mariadb_connection.commit()
   print "The last inserted id was: ", cursor.lastrowid   

   #exclui relacionamento no neo4j
   payload = "{\n  \"query\" : \"match (usr1:USUARIO {id_usuario:%s})-[r:ASSISTIU]->(filme1:FILMES_SERIES {id_filme:%s}) delete r\",\n  \"params\" : { }\n}\n" % (idUser, idFilme)
   response = requests.request("POST", url, data=payload, headers=headers)
   print(response.text)

   mariadb_connection.close()
   return ret 

def recommendMovie(idUser):
   payload = "{\n  \"query\" : \"match (filmedest:FILMES_SERIES)<-[:ASSISTIU]-(usrdest:USUARIO)-[:ASSISTIU]->(filmeori:FILMES_SERIES)<-[:ASSISTIU]-(usr:USUARIO) where usr.id_usuario = %s and not exists ((usr:USUARIO)-[:ASSISTIU]->(filmedest:FILMES_SERIES)) return distinct filmedest\",\n  \"params\" : { }\n}\n" % (idUser)

   response = requests.request("POST", url, data=payload, headers=headers)
   data = response.json() 
   ret = "["

   for x in data['data']:
      for y in x:
         if ret <> "[":
            ret += ","
         ret += "{\"nmFilme\":\"%s\", \"dtFilme\":\"%s\"}" % (y['data']['nome_filme'],y['data']['ano_lanc_filme'])

   ret += "]"
   return json.loads(ret) 

def recommendPeople(idUser):
   payload = "{\n  \"query\" : \"match (usrdest:USUARIO)-[rdest:ASSISTIU]->(filme:FILMES_SERIES)<-[r:ASSISTIU]-(usr:USUARIO) with usrdest, [x in split(usrdest.dt_nascimento_usuario,'/') | toInteger(x)] as parts where usr.id_usuario = %s return distinct usrdest.nome_usuario as nome, usrdest.e_mail_usuario as e_mail, duration.between(date({day: parts[0], month: parts[1], year: parts[2]}), date()).years AS idade, count(usrdest) as ranking order by count(usrdest) desc\",\n  \"params\" : { }\n}\n" % (idUser)

   response = requests.request("POST", url, data=payload, headers=headers)
   data = response.json() 
   ret = "["

   for x in data['data']:
      if ret <> "[":
         ret += ","
      ret += "{\"nome\":\"%s\",\"email\":\"%s\",\"idade\":\"%s\",\"rank\":\"%s\"}" % (x[0],x[1],str(x[2]),str(x[3]))

   ret += "]"
   return json.loads(ret) 


## AUX ###############################################################

def tdata(data):
   dt = data.split("-")
   datat = dt[2]+"/"+dt[1]+"/"+dt[0]
   return datat

def encondeDD(chunck):
   if (len(chunck)%16!=0):
      chunck+= ' ' * (16-len(chunck)%16)         
   encoded = pybase64.urlsafe_b64encode(cipher.encrypt(chunck))
   return encoded

def intToStr(intDB):
   return str(intDB).replace("(","").replace(",)","")

def getCookies():
   data = request.cookies.get('dd')
   decoded = cipher.decrypt(pybase64.urlsafe_b64decode(data))
   return decoded.strip().split(",")


if __name__ == '__main__':
   app.run(debug = True)