import pandas as pd
import random
from datetime import datetime, timedelta

# Parâmetros
num_jogadores = 1000
num_batalhas = 5000

# Lista de cartas reais do Clash Royale
cartas_clash_royale = [
    # Tropas
    "Arqueiras", "Cavaleiro", "Gigante", "Mini P.E.K.K.A", "Mosqueteira", 
    "Príncipe", "Dragão Bebê", "Bruxa", "Executor", "Mago", 
    "Mago de Gelo", "P.E.K.K.A", "Mega Servo", "Golem", "Corredor", "Bárbaros",
    # Feitiços
    "Bola de Fogo", "Fúria", "Zap", "Relâmpago", "Tornado", "Veneno", "Descarga",
    # Construções
    "Canhão", "Torre Inferno", "Cabana de Bárbaros", "Torre de Bombas", 
    "Cabana de Goblins", "Fornalha", "Lápide", "Coletor de Elixir"
]

# Função para gerar um deck aleatório de 8 cartas reais
def gerar_deck_real():
    return random.sample(cartas_clash_royale, 8)

# Função para gerar uma data aleatória para as batalhas
def gerar_data():
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 1, 1)
    return start_date + (end_date - start_date) * random.random()

# Tabela de Jogadores
jogadores = []
for i in range(1, num_jogadores + 1):
    jogador = {
        "nickname": f"Player{i:04d}",
        "tempo_de_jogo": random.randint(50, 500),  # Entre 50 e 500 horas de jogo
        "trofeus": random.randint(2000, 6000),  # Entre 2000 e 6000 troféus
        "nivel": random.randint(9, 14),  # Nível entre 9 e 14
        "deck": ', '.join(gerar_deck_real()),  # Deck aleatório com cartas reais
    }
    jogadores.append(jogador)

df_jogadores = pd.DataFrame(jogadores)

# Tabela de Batalhas
batalhas = []
for i in range(1, num_batalhas + 1):
    jogador1 = random.choice(jogadores)
    jogador2 = random.choice(jogadores)
    
    # Garante que os jogadores não sejam a mesma pessoa
    while jogador2["nickname"] == jogador1["nickname"]:
        jogador2 = random.choice(jogadores)
    
    batalha = {
        "id_batalha": i,
        "data": gerar_data(),  # Data e hora da batalha
        "tempo_de_batalha": round(random.uniform(1.5, 5.0), 2),  # Tempo da batalha entre 1.5 e 5 minutos
        "torres_derrubadas_jogador1": random.randint(0, 3),  # Torres derrubadas por jogador 1
        "torres_derrubadas_jogador2": random.randint(0, 3),  # Torres derrubadas por jogador 2
        "vencedor": random.choice([jogador1["nickname"], jogador2["nickname"]]),  # Escolhe o vencedor aleatoriamente
        "deck_jogador1": jogador1["deck"],
        "deck_jogador2": jogador2["deck"],
        "trofeus_jogador1": jogador1["trofeus"],
        "trofeus_jogador2": jogador2["trofeus"],
    }
    
    # Ajusta o número de torres com base no vencedor (quem ganhou normalmente derruba mais torres)
    if batalha["vencedor"] == jogador1["nickname"]:
        batalha["torres_derrubadas_jogador1"] = max(batalha["torres_derrubadas_jogador1"], 1)
        batalha["torres_derrubadas_jogador2"] = min(batalha["torres_derrubadas_jogador2"], 2)
    else:
        batalha["torres_derrubadas_jogador2"] = max(batalha["torres_derrubadas_jogador2"], 1)
        batalha["torres_derrubadas_jogador1"] = min(batalha["torres_derrubadas_jogador1"], 2)
    
    batalhas.append(batalha)

df_batalhas = pd.DataFrame(batalhas)

# Exporta os datasets para CSV
df_jogadores.to_csv('jogadores.csv', index=False, encoding='utf-8')
df_batalhas.to_csv('batalhas.csv', index=False, encoding='utf-8')

print("Datasets gerados e exportados como 'jogadores.csv' e 'batalhas.csv'")