import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import requests

# Inicializar a aplicação Dash
app = dash.Dash(__name__)


# Layout da aplicação
app.layout = html.Div([
    html.H1("Clash Royale Dashboard"),
    dcc.Dropdown(
        id='rarity-type-dropdown',  # Atualize o ID para 'rarity-type-dropdown'
        options=[
            {'label': 'Common', 'value': 'Common'},
            {'label': 'Rare', 'value': 'Rare'},
            {'label': 'Epic', 'value': 'Epic'},
            {'label': 'Por Tipo', 'value': 'Type'}  # Nova opção para "Tipo"
        ],
        value='Common'  # Valor inicial
    ),
    dcc.Graph(id='rarity-graph')
])

# # Layout da aplicação
# app.layout = html.Div([
#     html.H1("Clash Royale Dashboard"),
#     dcc.Dropdown(
#         id='rarity-dropdown',
#         options=[
#             {'label': 'Common', 'value': 'Common'},
#             {'label': 'Rare', 'value': 'Rare'},
#             {'label': 'Epic', 'value': 'Epic'}
#         ],
#         value='Common'
#     ),
#     dcc.Graph(id='rarity-graph')
# ])


@app.callback(
    Output('rarity-graph', 'figure'),
    [Input('rarity-type-dropdown', 'value')]
)
def update_graph(selected_value):
    """Atualiza o gráfico de acordo com a raridade ou tipo selecionado"""
    
    # Se a seleção for uma das raridades (Common, Rare, Epic)
    if selected_value in ['Common', 'Rare', 'Epic']:
        # Fazer a requisição para a API Flask com base na raridade
        response = requests.get(f'http://localhost:5000/cards/{selected_value}')
        cards = response.json()
        df = pd.DataFrame(cards)

        # Criar gráfico de barras para raridade
        fig = px.bar(df, x='name', y='elixir', title=f'Elixir por Card ({selected_value})')
    
    # Se a seleção for por "Tipo"
    elif selected_value == 'Type':
        # Fazer a requisição para buscar todos os cards
        response = requests.get('http://localhost:5000/cards')
        cards = response.json()
        df = pd.DataFrame(cards)

        # Converter a coluna 'elixir' para numérico, forçando erros a NaN
        df['elixir'] = pd.to_numeric(df['elixir'], errors='coerce')

        # Agrupar por 'type' e calcular a média de 'elixir', ignorando NaN
        df_grouped = df.groupby('type')['elixir'].mean().reset_index()

        # Criar gráfico de barras para a média de elixir por tipo
        fig = px.bar(df_grouped, x='type', y='elixir', title='Média de Elixir por Tipo')

    return fig

# # Callback para atualizar o gráfico com base na raridade selecionada
# @app.callback(
#     Output('rarity-graph', 'figure'),
#     [Input('rarity-dropdown', 'value')]
# )
# def update_graph(rarity):
#     """Atualiza o gráfico de acordo com a raridade selecionada"""
#     # Fazer a requisição para a API Flask
#     response = requests.get(f'http://localhost:5000/cards/{rarity}')
#     cards = response.json()
#     df = pd.DataFrame(cards)

#     # Criar o gráfico de barras usando Plotly
#     fig = px.bar(df, x='name', y='elixir', title=f'Elixir por Card ({rarity})')
#     return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)