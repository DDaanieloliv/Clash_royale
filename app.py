from flask import Flask, jsonify 
# O Flask é um microframework web para Python.
# (ideal para construir APIs simples).

# O jsonify é uma função do Flask usada para converter dados do 
# Python (como listas e dicionários) para o formato JSON, que é 
# o formato padrão de resposta em APIs.

# Ao retornar os dados do MongoDB para o cliente (como no seu Dash app), 
# eles precisam ser serializados em formato JSON. jsonify faz isso 
# automaticamente.

from pymongo import MongoClient
# O MongoClient é o cliente MongoDB que você usa para se conectar ao 
# banco de dados MongoDB a partir de Python.

import pandas as pd
# O pandas é uma biblioteca poderosa para manipulação e análise de 
# dados, muito usada em ciência de dados.

import csv
# A biblioteca csv é uma biblioteca nativa do Python para ler e 
# escrever arquivos no formato CSV (Comma Separated Values).

# Embora o pandas também tenha suporte para CSV, a biblioteca csv é 
# útil quando você precisa manipular grandes quantidades de dados de forma 
# mais eficiente ou personalizada.



# Conectar ao MongoDB
mongo_uri = "mongodb://admin:123@localhost:27017/"  

client = MongoClient(mongo_uri)
# Criando uma instância de MongoClient e passando a URI de conexão (mongo_uri).

# O MongoClient é o objeto principal da biblioteca pymongo que gerencia a 
# conexão entre o código Python e o servidor MongoDB.

db = client["DB_clash"]
# O objeto client é uma conexão com o servidor MongoDB.
# Quando você usa client["DB_clash"], você está basicamente dizendo ao 
# MongoDB que quer acessar um banco de dados específico chamado DB_clash.
# Basicamente, isso prepara o Python para interagir com o banco de dados 
# DB_clash no lado do MongoDB, mas ainda não executa nenhuma operação.

collection = db["royale_collection"]    
# Quando você faz db["royale_collection"], você está acessando uma coleção 
# dentro deste banco de dados. Isso não realiza nenhuma operação de banco de 
# dados até que você faça algo como inserir, buscar ou modificar documentos 
# nessa coleção.


# Essas linhas acima preparam o acesso ao banco de dados DB_clash e à coleção 
# royale_collection. Mas até que você faça uma operação de inserção, consulta 
# ou qualquer outra interação, nada é criado no MongoDB.

# O MongoDB e o PyMongo permitem que você defina um banco de dados e uma coleção 
# "virtualmente", ou seja, você pode referenciar esses recursos sem que eles 
# realmente existam fisicamente no servidor MongoDB. Eles só serão criados quando 
# você realizar uma operação, como uma inserção de dados.


# Por que isso acontece?
# 
# MongoDB é um banco de dados NoSQL flexível e "schema-less", o que significa que 
# você não precisa definir explicitamente um esquema (como tabelas e campos) antes 
# de usar o banco. Os recursos são criados dinamicamente no momento em que uma 
# operação de escrita é feita.



# client é um objeto MongoClient diretamente, não apenas uma variável que "possui" 
# um objeto.

# Quando você faz client = MongoClient(mongo_uri), você está criando um objeto do 
# tipo MongoClient.

# A variável db é um objeto do tipo Database porque ela recebe o resultado de 
# client["DB_clash"]. db é um objeto Database, retornado por client["DB_clash"]. 
# Ele não é simplesmente um objeto porque o client é um objeto, mas sim porque esse 
# método (client["DB_clash"]) retorna um novo objeto que representa o banco de dados.

# A variável collection é um objeto do tipo Collection porque ela recebe o resultado 
# de db["royale_collection"]. collection é um objeto Collection, retornado por 
# db["royale_collection"]. De novo, ele é um objeto não só porque db é um objeto, mas 
# porque o acesso a uma coleção (db["colecao"]) retorna um objeto Collection.




# Carregar dataset para MongoDB
dataset = pd.read_csv('info_cards.csv', sep=',')
dataset = dataset.dropna()

# Inserir dados no MongoDB
with open('cards.csv', 'r') as file:
    reader = csv.DictReader(file)
    data = list(reader)
    collection.insert_many(data)

print("Dados inseridos com sucesso!")

# open('cards.csv', 'r'): Abre o arquivo cards.csv no modo de leitura ('r'), 
#   o que permite que o arquivo seja lido mas não modificado.
#
# with: O bloco with é usado para garantir que o arquivo seja automaticamente 
#   fechado após a operação, mesmo que haja algum erro durante a execução. Isso 
#   é uma boa prática em Python para evitar problemas de vazamento de recursos.
#
# as file: Aqui, a variável file contém o objeto do arquivo aberto.


# csv.DictReader(file): A função csv.DictReader lê o arquivo CSV e converte cada 
#   linha em um dicionário Python, onde:
#
# As chaves do dicionário são os nomes das colunas do arquivo CSV (a primeira linha 
# do CSV geralmente contém esses nomes).
# 
# Os valores do dicionário são os dados de cada linha subsequente do arquivo.
#
# Exemplo: Se o CSV tem o seguinte formato:
#
# name,elixir,rarity,type
# Knight,3,Common,Troop
# Archers,3,Common,Troop
#
# O DictReader irá transformar cada linha em algo assim:
#
# {"name": "Knight", "elixir": 3, "rarity": "Common", "type": "Troop"}
# {"name": "Archers", "elixir": 3, "rarity": "Common", "type": "Troop"}
#
# 
# list(reader): Transforma o objeto DictReader (que é um iterador) em uma lista 
#   de dicionários. Cada dicionário corresponde a uma linha do CSV, representando um
#   conjunto de valores para as colunas.
# 
# Exemplo de como a variável data ficará após a conversão:
#
# [
#   {"name": "Knight", "elixir": 3, "rarity": "Common", "type": "Troop"},
#   {"name": "Archers", "elixir": 3, "rarity": "Common", "type": "Troop"}
# ]
#
# 
# insert_many(data): Este método da coleção MongoDB insere vários documentos 
#   de uma vez. Aqui, data é uma lista de dicionários (cada dicionário é um 
#   "documento" no MongoDB), então todos os dicionários da lista serão inseridos na 
#   coleção royale_collection.
#
# Se data contém 100 dicionários (linhas do CSV), o MongoDB irá inserir 100 
# documentos na coleção royale_collection.



# Configuração do Flask para a API
app = Flask(__name__)
# Cria uma nova aplicação Flask. O argumento __name__ é passado para ajudar o 
# Flask a localizar arquivos estáticos e templates corretamente. Basicamente, 
# o Flask usa essa variável para definir o contexto da aplicação.

# Rota para buscar todos os cards
@app.route('/cards', methods=['GET'])
def get_all_cards():
    """Retorna todos os cards"""
    cards = list(collection.find({}, {'_id': 0}))  # Excluir '_id' para facilitar
    return jsonify(cards)
# Esta função será executada sempre que a rota /cards for acessada.
# Converte o resultado da consulta (um cursor) em uma lista Python.
# Faz uma busca (consulta) no banco de dados MongoDB.

# Rota para buscar cards por raridade
@app.route('/cards/<rarity>', methods=['GET'])
def get_cards_by_rarity(rarity):
    """Retorna cards pela raridade"""
    cards = list(collection.find({"rarity": rarity}, {'_id': 0}))
    return jsonify(cards)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

# Esta linha verifica se o arquivo Python está sendo executado diretamente 
# (como um script) ou se está sendo importado como um módulo por outro arquivo.

# Em Python, cada arquivo tem um atributo especial chamado __name__. Se o arquivo 
# está sendo executado diretamente, o valor de __name__ será '__main__'**. Caso 
# contrário, se o arquivo estiver sendo importado, o valor de **name` será o 
# nome do módulo (ou seja, o nome do arquivo).

# Portanto, if __name__ == '__main__': verifica se o arquivo está sendo executado 
# diretamente. Se estiver, o bloco de código dentro dessa verificação será 
# executado. Caso contrário, o código não será executado.

# import logging
# from dash import Dash, dcc, html
# from dash.dependencies import Input, Output

# # Configurar logging
# logging.basicConfig(level=logging.DEBUG)

# app = Dash(__name__)

# app.layout = html.Div([
#     dcc.Dropdown(
#         id='bar-chart-dropdown',
#         options=[
#             {'label': 'Cartas', 'value': '_id'},
#         ],
#         value='_id'
#     ),
#     dcc.Graph(id='bar-chart')
# ])

# @app.callback(
#     Output('bar-chart', 'figure'),
#     Input('bar-chart-dropdown', 'value')
# )
# def update_bar_chart(selected_column):
#     logging.debug(f'Atualizando gráfico para coluna: {selected_column}')
#     # Código do gráfico aqui...
#     pass

# if __name__ == '__main__':
#     logging.debug('Iniciando servidor Dash...')
#     app.run(debug=True)