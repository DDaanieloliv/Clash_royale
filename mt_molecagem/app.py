from flask import Flask, jsonify, request
from pymongo import MongoClient
import pandas as pd
from datetime import datetime

# Configurar a conexão com o MongoDB
client = MongoClient('mongodb://admin:123@localhost:27017/')
db = client['clash_royale']
jogadores_collection = db['jogadores']
batalhas_collection = db['batalhas']

# Função para converter a string de deck para lista
def converter_deck(deck_str):
    # Remove as aspas e transforma a string em lista
    return [carta.strip() for carta in deck_str.split(',')]

# Função para converter a data de string para objeto datetime
def converter_data(data_str):
    return datetime.strptime(data_str, '%Y-%m-%d %H:%M:%S.%f')

# Função para importar CSV de jogadores e salvar no MongoDB
def importar_jogadores(csv_path):
    # Leitura do CSV usando pandas
    df_jogadores = pd.read_csv(csv_path)
    
    # Para cada jogador no DataFrame
    for _, row in df_jogadores.iterrows():
        jogador = {
            "nickname": row['nickname'],
            "tempo_de_jogo": row['tempo_de_jogo'],
            "trofeus": row['trofeus'],
            "nivel": row['nivel'],
            "deck": converter_deck(row['deck'])  # Convertendo deck para lista
        }
        # Inserir ou atualizar o jogador no MongoDB
        jogadores_collection.update_one(
            {"nickname": jogador["nickname"]}, 
            {"$set": jogador}, 
            upsert=True
        )

# Função para importar CSV de batalhas e salvar no MongoDB
def importar_batalhas(csv_path):
    # Leitura do CSV usando pandas
    df_batalhas = pd.read_csv(csv_path)
    
    # Para cada batalha no DataFrame
    for _, row in df_batalhas.iterrows():
        batalha = {
            "id_batalha": row['id_batalha'],
            "data": converter_data(row['data']),  # Convertendo string para datetime
            "tempo_de_batalha": row['tempo_de_batalha'],
            "torres_derrubadas_jogador1": row['torres_derrubadas_jogador1'],
            "torres_derrubadas_jogador2": row['torres_derrubadas_jogador2'],
            "vencedor": row['vencedor'],
            "deck_jogador1": converter_deck(row['deck_jogador1']),  # Convertendo deck para lista
            "deck_jogador2": converter_deck(row['deck_jogador2']),  # Convertendo deck para lista
            "trofeus_jogador1": row['trofeus_jogador1'],
            "trofeus_jogador2": row['trofeus_jogador2']
        }
        # Inserir ou atualizar a batalha no MongoDB
        batalhas_collection.update_one(
            {"id_batalha": batalha["id_batalha"]}, 
            {"$set": batalha}, 
            upsert=True
        )

# Exemplo de como usar as funções
if __name__ == '__main__':
    # Substitua pelos caminhos reais dos arquivos CSV
    jogadores_csv_path = 'jogadores.csv'
    batalhas_csv_path = 'batalhas.csv'
    
    # Importa os dados dos CSVs para o MongoDB
    importar_jogadores(jogadores_csv_path)
    importar_batalhas(batalhas_csv_path)

    print("Importação concluída!")

app = Flask(__name__)

# Função para converter a string de data para objeto datetime
def converter_data_api(data_str):
    return datetime.strptime(data_str, '%Y-%m-%d %H:%M:%S')

# API para calcular a porcentagem de vitórias e derrotas utilizando a carta X em um intervalo de timestamps
@app.route('/porcentagem_vitorias_derrotas', methods=['GET'])
def porcentagem_vitorias_derrotas():
    carta = request.args.get('carta')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    # Converte as datas
    data_inicio = converter_data_api(inicio)
    data_fim = converter_data_api(fim)

    # Filtra as batalhas no intervalo de tempo
    batalhas = batalhas_collection.find({
        "data": {"$gte": data_inicio, "$lte": data_fim},
        "$or": [
            {"deck_jogador1": carta},
            {"deck_jogador2": carta}
        ]
    })

    total_batalhas = 0
    vitorias = 0
    derrotas = 0

    for batalha in batalhas:
        total_batalhas += 1
        if carta in batalha['deck_jogador1'] and batalha['vencedor'] == batalha['deck_jogador1']:
            vitorias += 1
        elif carta in batalha['deck_jogador2'] and batalha['vencedor'] == batalha['deck_jogador2']:
            vitorias += 1
        else:
            derrotas += 1

    if total_batalhas > 0:
        porcentagem_vitorias = (vitorias / total_batalhas) * 100
        porcentagem_derrotas = (derrotas / total_batalhas) * 100
    else:
        porcentagem_vitorias = 0
        porcentagem_derrotas = 0

    return jsonify({
        "carta": carta,
        "total_batalhas": total_batalhas,
        "vitorias": vitorias,
        "derrotas": derrotas,
        "porcentagem_vitorias": porcentagem_vitorias,
        "porcentagem_derrotas": porcentagem_derrotas
    })

# API para listar os decks completos que produziram mais de X% de vitórias em um intervalo de timestamps
@app.route('/decks_vitoriosos', methods=['GET'])
def decks_vitoriosos():
    porcentagem_minima = float(request.args.get('porcentagem'))
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    # Converte as datas
    data_inicio = converter_data_api(inicio)
    data_fim = converter_data_api(fim)

    # Filtra as batalhas no intervalo de tempo
    batalhas = batalhas_collection.find({
        "data": {"$gte": data_inicio, "$lte": data_fim}
    })

    deck_vitorias = {}

    for batalha in batalhas:
        vencedor = batalha['vencedor']
        if vencedor == batalha['deck_jogador1']:
            deck = tuple(batalha['deck_jogador1'])
        else:
            deck = tuple(batalha['deck_jogador2'])

        if deck not in deck_vitorias:
            deck_vitorias[deck] = {"vitorias": 0, "total": 0}

        deck_vitorias[deck]['vitorias'] += 1
        deck_vitorias[deck]['total'] += 1

    # Filtra os decks que têm mais de X% de vitórias
    decks_com_vitorias = []
    for deck, stats in deck_vitorias.items():
        if stats['total'] > 0:
            porcentagem_vitorias = (stats['vitorias'] / stats['total']) * 100
            if porcentagem_vitorias >= porcentagem_minima:
                decks_com_vitorias.append({
                    "deck": list(deck),
                    "vitorias": stats['vitorias'],
                    "total_batalhas": stats['total'],
                    "porcentagem_vitorias": porcentagem_vitorias
                })

    return jsonify(decks_com_vitorias)

# API para calcular a quantidade de derrotas utilizando o combo de cartas (X1, X2, ...) em um intervalo de timestamps
@app.route('/derrotas_combo_cartas', methods=['GET'])
def derrotas_combo_cartas():
    cartas = request.args.getlist('cartas')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    # Converte as datas
    data_inicio = converter_data_api(inicio)
    data_fim = converter_data_api(fim)

    # Filtra as batalhas no intervalo de tempo
    batalhas = batalhas_collection.find({
        "data": {"$gte": data_inicio, "$lte": data_fim},
        "$or": [
            {"deck_jogador1": {"$all": cartas}},
            {"deck_jogador2": {"$all": cartas}}
        ]
    })

    derrotas = 0

    for batalha in batalhas:
        if all(carta in batalha['deck_jogador1'] for carta in cartas) and batalha['vencedor'] != batalha['deck_jogador1']:
            derrotas += 1
        elif all(carta in batalha['deck_jogador2'] for carta in cartas) and batalha['vencedor'] != batalha['deck_jogador2']:
            derrotas += 1

    return jsonify({
        "combo_cartas": cartas,
        "derrotas": derrotas
    })

# Roda a aplicação Flask
if __name__ == '__main__':
    app.run(debug=True)