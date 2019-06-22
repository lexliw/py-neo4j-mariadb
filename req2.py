import requests

def intToStr(intDB):
   return str(intDB).replace("(","").replace(",)","")

url = "http://localhost:7474/db/data/cypher"

payload = "{\n  \"query\" : \"match (usrdest:USUARIO)-[rdest:ASSISTIU]->(filme:FILMES_SERIES)<-[r:ASSISTIU]-(usr:USUARIO) with usrdest, [x in split(usrdest.dt_nascimento_usuario,'/') | toInteger(x)] as parts where usr.id_usuario = 1 return distinct usrdest.nome_usuario as nome, usrdest.e_mail_usuario as e_mail, duration.between(date({day: parts[0], month: parts[1], year: parts[2]}), date()).years AS idade, count(usrdest) as ranking order by count(usrdest) desc\",\n  \"params\" : { }\n}\n"
headers = {
    'Content-Type': "application/json",
    'Accept': "application/json; charset=UTF-8",
    'Authorization': "Basic bmVvNGo6bmVvNGoy"
    }

response = requests.request("POST", url, data=payload, headers=headers)
data = response.json() 

for x in data['data']:
    print(x[0])+" - "+x[1]+" - "+str(x[2])+" - "+str(x[3])

