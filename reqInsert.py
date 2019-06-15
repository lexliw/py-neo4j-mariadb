import requests

url = "http://localhost:7474/db/data/cypher"

id='119988'
login='teste123'
nome='TESTE1234'

payload = "{\n  \"query\" : \"create (usr1:USUARIO {id_usuario:'"+id+"', login_usuario:'"+login+"',nome_usuario:'"+nome+"',dt_nascimento_usuario:'19/03/1992',e_mail_usuario:'tt0@tt.com.br',publicar:'S'})\",\n  \"params\" : { }\n}\n"
headers = {
    'Content-Type': "application/json",
    'Accept': "application/json; charset=UTF-8",
    'Authorization': "Basic bmVvNGo6bmVvNGoy",
    'cache-control': "no-cache",
    'Postman-Token': "cabdfe37-849c-4aac-9b1a-65be296af5bd"
    }

response = requests.request("POST", url, data=payload, headers=headers)

print(response.text)