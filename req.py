import requests

url = "http://localhost:7474/db/data/cypher"

payload = "{\n  \"query\" : \"match (filmedest:FILMES_SERIES)<-[:ASSISTIU]-(usrdest:USUARIO)-[:ASSISTIU]->(filmeori:FILMES_SERIES)<-[:ASSISTIU]-(usr:USUARIO) where usr.id_usuario = 12 and not exists ((usr:USUARIO)-[:ASSISTIU]->(filmedest:FILMES_SERIES)) return distinct filmedest\",\n  \"params\" : { }\n}\n"
headers = {
    'Content-Type': "application/json",
    'Accept': "application/json; charset=UTF-8",
    'Authorization': "Basic bmVvNGo6bmVvNGoy"
    }

response = requests.request("POST", url, data=payload, headers=headers)
data = response.json() 

for x in data['data']:
    for y in x:
        print(y['data']['nome_filme']+" ano: "+ y['data']['ano_lanc_filme'])
