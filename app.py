from flask import Flask, jsonify 
# O Flask é um microframework web para Python.
# (ideal para construir APIs simples)

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
collection = db["royale_collection"]    

# Carregar dataset para MongoDB
dataset = pd.read_csv('info_cards.csv', sep=',')
dataset = dataset.dropna()

# Inserir dados no MongoDB
with open('cards.csv', 'r') as file:
    reader = csv.DictReader(file)
    data = list(reader)
    collection.insert_many(data)

print("Dados inseridos com sucesso!")

# Configuração do Flask para a API
app = Flask(__name__)

# Rota para buscar todos os cards
@app.route('/cards', methods=['GET'])
def get_all_cards():
    """Retorna todos os cards"""
    cards = list(collection.find({}, {'_id': 0}))  # Excluir '_id' para facilitar
    return jsonify(cards)

# Rota para buscar cards por raridade
@app.route('/cards/<rarity>', methods=['GET'])
def get_cards_by_rarity(rarity):
    """Retorna cards pela raridade"""
    cards = list(collection.find({"rarity": rarity}, {'_id': 0}))
    return jsonify(cards)

if __name__ == '__main__':
    app.run(debug=True, port=5000)



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