# -*- coding: utf-8 -*-
from flask import Flask, render_template
app = Flask(__name__)

#
#sudo docker run  --publish=7474:7474 --publish=7687:7687 -v $HOME/neo4j/data:/data -v $HOME/neo4j/import:/import  neo4j


@app.route('/')
def index():
   return render_template('home.html')

if __name__ == '__main__':
   app.run(debug = True)