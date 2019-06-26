# py-neo4j-mariadb

Esta aplicação é uma POC do Neo4j. Se trata de um sistema de recomendação simples onde um usuário se cadastra no sistema e ao avaliar filme ou seriados que assistiu, o sistema informa outras pessoal que assistiram os mesmos filmes que ele avaliou e indica outros filmes para ele assistir.

## Estrutura
- Front-end: Materialize 
- Black-end: Python Flask 
- BD: Mariadb e Neo4j


## Pre requisitos:

Instalar:
- [x] docker
- [x] docker-compose
- [x] python 2.7
- [x] python-pip

executar na pasta */py-neo4j-mariadb/asset* o comando:

```
docker-compose up -d

Ele irá subir as imagens dos bancos de dados e dar carga na mariaDB.
```

executar na pasta */py-neo4j-mariadb/* o comando:

```
pip3 install -r requirements.txt

python3 server.py

Ele irá subir a aplicação.
```
Acessar http://locahost:5000 para aplicação

Acessar http://locahost:8080 interface do banco **mariadb** usuario *root* senha *example*

Acessar http://localhost:7474 e dar carga no **neo4j**. Os arquivos .csv da pasta ./asset precisam estar na pasta ***import*** do container.

executar os comandos:
```
using periodic commit load csv with headers from "file:///USUARIOS.CSV" as row merge (usr:USUARIO {id_usuario:toInteger(row.id_usuario), login_usuario:row.login_usuario, nome_usuario:row.nome_usuario, dt_nascimento_usuario:row.dt_nascimento_usuario, e_mail_usuario:row.e_mail_usuario, publicar:row.publicar})

using periodic commit load csv with headers from "file:///FILMES_SERIES.CSV" as row merge (filmes:FILMES_SERIES {id_filme:toInteger(row.id_filme), nome_filme:row.nome_filme, ano_lanc_filme:row.ano_lanc_filme, ano_fim_filme:row.ano_fim_filme, descricao_filme:row.descricao_filme})

using periodic commit load csv with headers from "file:///USUARIO_ASSISTIU.CSV" as row match (usr:USUARIO {id_usuario:toInteger(row.id_usuario)}),(filme:FILMES_SERIES {id_filme:toInteger(row.id_filme)}) merge (usr)-[:ASSISTIU {dt_ini_assistido:row.dt_ini_assistido, dt_fim_assistido:row.dt_fim_assistido, resenha:row.resenha, nota:toInteger(row.nota)}]->(filme)
```
