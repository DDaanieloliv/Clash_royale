from flask import Flask, jsonify, request
from pymongo import MongoClient
import pandas as pd
import csv
from datetime import datetime

# Conectar ao MongoDB
mongo_uri = "mongodb://admin:123@localhost:27017/"
client = MongoClient(mongo_uri)
db = client["DB_clash"]

# Coleções do MongoDB
batalhas_collection = db["batalhas"]
jogadores_collection = db["jogadores"]

# Função para carregar um CSV e inserir no MongoDB
def carregar_dataset_batalhas(csv_file):
    # Carregar o CSV usando pandas
    df = pd.read_csv(csv_file)
    
    # Converter as colunas necessárias para os tipos corretos
    df['tempo_de_batalha'] = df['tempo_de_batalha'].astype(float)
    df['torres_derrubadas_jogador1'] = df['torres_derrubadas_jogador1'].astype(int)
    df['torres_derrubadas_jogador2'] = df['torres_derrubadas_jogador2'].astype(int)
    df['trofeus_jogador1'] = df['trofeus_jogador1'].astype(int)
    df['trofeus_jogador2'] = df['trofeus_jogador2'].astype(int)

    # Inserir os dados no MongoDB
    batalhas_collection.insert_many(df.to_dict('records'))

def carregar_dataset_jogadores(csv_file):
    # Carregar o CSV usando pandas
    df = pd.read_csv(csv_file)
    
    # Converter as colunas necessárias para os tipos corretos
    df['tempo_de_jogo'] = df['tempo_de_jogo'].astype(float)
    df['trofeus'] = df['trofeus'].astype(int)
    df['nivel'] = df['nivel'].astype(int)

    # Inserir os dados no MongoDB
    jogadores_collection.insert_many(df.to_dict('records'))

# Carregar os datasets de batalhas e jogadores
carregar_dataset_batalhas('C:/Users/nielo/Documents/Clash_royale/mt_molecagem/batalhas_clash_royale.csv')  # Certifique-se de que o arquivo 'batalhas.csv' esteja no caminho correto
carregar_dataset_jogadores('C:/Users/nielo/Documents/Clash_royale/mt_molecagem/jogadores_clash_royale.csv')  # Certifique-se de que o arquivo 'jogadores.csv' esteja no caminho correto


# Configuração do Flask para expor APIs
app = Flask(__name__)

# 1. Calcular a porcentagem de vitórias e derrotas utilizando a carta X em um intervalo de timestamps
@app.route('/vitorias_derrotas_carta', methods=['GET'])
def calcular_porcentagem_vitorias_derrotas():
    """Calcula a porcentagem de vitórias e derrotas utilizando a carta X em um intervalo de timestamps"""
    carta = request.args.get('carta')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    # Converter os timestamps para o formato datetime
    inicio_dt = datetime.strptime(inicio, '%Y-%m-%d %H:%M:%S')
    fim_dt = datetime.strptime(fim, '%Y-%m-%d %H:%M:%S')

    # Buscar todas as batalhas no intervalo de timestamps
    batalhas = list(batalhas_collection.find({
        'timestamp': {'$gte': inicio_dt, '$lte': fim_dt},
        '$or': [{'cartas_vencedor': carta}, {'cartas_perdedor': carta}]
    }))

    vitorias = sum(1 for b in batalhas if carta in b['cartas_vencedor'])
    derrotas = sum(1 for b in batalhas if carta in b['cartas_perdedor'])

    total_batalhas = vitorias + derrotas
    porcentagem_vitorias = (vitorias / total_batalhas) * 100 if total_batalhas > 0 else 0
    porcentagem_derrotas = (derrotas / total_batalhas) * 100 if total_batalhas > 0 else 0

    return jsonify({
        'carta': carta,
        'vitorias': vitorias,
        'derrotas': derrotas,
        'porcentagem_vitorias': porcentagem_vitorias,
        'porcentagem_derrotas': porcentagem_derrotas
    })

GET /vitorias_derrotas_carta?carta=Mini%20P.E.K.K.A&inicio=2024-01-01%2000:00:00&fim=2024-12-31%2023:59:59



# 2. Listar os decks completos que produziram mais de X% de vitórias em um intervalo de timestamps
@app.route('/decks_vitorias', methods=['GET'])
def listar_decks_com_vitorias():
    """Lista decks que produziram mais de X% de vitórias em um intervalo de timestamps"""
    percentual_vitorias = float(request.args.get('percentual'))
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    # Converter os timestamps para o formato datetime
    inicio_dt = datetime.strptime(inicio, '%Y-%m-%d %H:%M:%S')
    fim_dt = datetime.strptime(fim, '%Y-%m-%d %H:%M:%S')

    # Buscar todas as batalhas no intervalo de timestamps
    batalhas = list(batalhas_collection.find({'timestamp': {'$gte': inicio_dt, '$lte': fim_dt}}))

    deck_vitorias = {}

    for b in batalhas:
        deck = tuple(b['cartas_vencedor'])  # Considerar o deck vencedor
        deck_vitorias[deck] = deck_vitorias.get(deck, {'vitorias': 0, 'total': 0})
        deck_vitorias[deck]['vitorias'] += 1
        deck_vitorias[deck]['total'] += 1

        deck_perdedor = tuple(b['cartas_perdedor'])  # Considerar o deck perdedor
        if deck_perdedor not in deck_vitorias:
            deck_vitorias[deck_perdedor] = {'vitorias': 0, 'total': 1}
        else:
            deck_vitorias[deck_perdedor]['total'] += 1

    decks_com_percentual_vitorias = {
        deck: data for deck, data in deck_vitorias.items()
        if (data['vitorias'] / data['total']) * 100 >= percentual_vitorias
    }

    return jsonify(decks_com_percentual_vitorias)

GET /decks_vitorias?percentual=60&inicio=2024-01-01%2000:00:00&fim=2024-12-31%2023:59:59



# 3. Calcular a quantidade de derrotas usando um combo de cartas (X1, X2, ...) em um intervalo de timestamps
@app.route('/derrotas_combo', methods=['GET'])
def calcular_derrotas_combo():
    """Calcula a quantidade de derrotas utilizando um combo de cartas (X1, X2, ...) em um intervalo de timestamps"""
    cartas = request.args.getlist('cartas')  # Espera receber várias cartas como parâmetros
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    # Converter os timestamps para o formato datetime
    inicio_dt = datetime.strptime(inicio, '%Y-%m-%d %H:%M:%S')
    fim_dt = datetime.strptime(fim, '%Y-%m-%d %H:%M:%S')

    # Buscar batalhas onde o perdedor usou o combo de cartas especificado
    derrotas = batalhas_collection.count_documents({
        'timestamp': {'$gte': inicio_dt, '$lte': fim_dt},
        'cartas_perdedor': {'$all': cartas}
    })

    return jsonify({
        'cartas': cartas,
        'derrotas': derrotas
    })

GET /derrotas_combo?cartas=Mini%20P.E.K.K.A,Golem&inicio=2024-01-01%2000:00:00&fim=2024-12-31%2023:59:59



# 4. Calcular vitórias com carta X nos casos com regras específicas
@app.route('/vitorias_regras', methods=['GET'])
def calcular_vitorias_com_regras():
    """Calcula vitórias envolvendo a carta X, considerando regras adicionais"""
    carta = request.args.get('carta')
    diferenca_trofeus = float(request.args.get('diferenca_trofeus'))
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    # Converter os timestamps para o formato datetime
    inicio_dt = datetime.strptime(inicio, '%Y-%m-%d %H:%M:%S')
    fim_dt = datetime.strptime(fim, '%Y-%m-%d %H:%M:%S')

    # Buscar batalhas onde a carta foi usada e obedecem às regras
    vitorias = list(batalhas_collection.find({
        'timestamp': {'$gte': inicio_dt, '$lte': fim_dt},
        'cartas_vencedor': carta,
        'trofeus_vencedor': {'$lte': {'$subtract': ['$trofeus_perdedor', diferenca_trofeus]}},
        'duracao': {'$lt': 120},  # Duração menor que 2 minutos
        'torres_perdedor': {'$gte': 2}  # O perdedor derrubou ao menos duas torres
    }))

    return jsonify({'vitorias': len(vitorias)})

GET /vitorias_regras?carta=Mini%20P.E.K.K.A&diferenca_trofeus=200&inicio=2024-01-01%2000:00:00&fim=2024-12-31%2023:59:59



# 5. Listar o combo de cartas que produziram mais de Y% de vitórias
@app.route('/combo_vitorias', methods=['GET'])
def listar_combo_vitorias():
    """Lista o combo de cartas de tamanho N que produziu mais de Y% de vitórias"""
    tamanho_combo = int(request.args.get('tamanho'))
    percentual_vitorias = float(request.args.get('percentual'))
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    # Converter os timestamps para o formato datetime
    inicio_dt = datetime.strptime(inicio, '%Y-%m-%d %H:%M:%S')
    fim_dt = datetime.strptime(fim, '%Y-%m-%d %H:%M:%S')

    # Buscar batalhas no intervalo de timestamps
    batalhas = list(batalhas_collection.find({'timestamp': {'$gte': inicio_dt, '$lte': fim_dt}}))

    combo_vitorias = {}

    for b in batalhas:
        combo = tuple(sorted(b['cartas_vencedor'][:tamanho_combo]))
        combo_vitorias[combo] = combo_vitorias.get(combo, {'vitorias': 0, 'total': 0})
        combo_vitorias[combo]['vitorias'] += 1
        combo_vitorias[combo]['total'] += 1

        combo_perdedor = tuple(sorted(b['cartas_perdedor'][:tamanho_combo]))
        if combo_perdedor not in combo_vitorias:
            combo_vitorias[combo_perdedor] = {'vitorias': 0, 'total': 1}
        else:
            combo_vitorias[combo_perdedor]['total'] += 1

    combos_com_percentual_vitorias = {
        combo: data for combo, data in combo_vitorias.items()
        if (data['vitorias'] / data['total']) * 100 >= percentual_vitorias
    }

    return jsonify(combos_com_percentual_vitorias)

GET /combo_vitorias?tamanho=3&percentual=70&inicio=2024-01-01%2000:00:00&fim=2024-12-31%2023:59:59



if __name__ == '__main__':
    app.run(debug=True, port=5000)
