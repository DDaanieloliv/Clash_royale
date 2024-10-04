from dash import Dash, dcc, html, Input, Output
import requests
import plotly.express as px
import pandas as pd

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Análise de Batalhas Clash Royale"),
    
    html.Div([
        html.Label("Selecione a carta:"),
        dcc.Input(id='input-carta', type='text', value=''),
        html.Label("Data de início (YYYY-MM-DD HH:MM:SS):"),
        dcc.Input(id='input-inicio', type='text', value='2024-01-01 00:00:00'),
        html.Label("Data de fim (YYYY-MM-DD HH:MM:SS):"),
        dcc.Input(id='input-fim', type='text', value='2024-12-31 23:59:59'),
        html.Button("Calcular Vitória/Derrota", id='submit-vitorias'),
    ]),

    dcc.Graph(id='graph-vitorias'),

    html.Div([
        html.Label("Percentual de vitórias:"),
        dcc.Input(id='input-percentual', type='number', value=50),
        html.Button("Listar Decks com Vitorias", id='submit-decks'),
    ]),

    dcc.Graph(id='graph-decks'),

    html.Div([
        html.Label("Combo de cartas (separadas por vírgula):"),
        dcc.Input(id='input-combo', type='text', value=''),
        html.Button("Calcular Derrotas", id='submit-derrotas'),
    ]),

    html.Div(id='output-derrotas'),
])

@app.callback(
    Output('graph-vitorias', 'figure'),
    Input('submit-vitorias', 'n_clicks'),
    Input('input-carta', 'value'),
    Input('input-inicio', 'value'),
    Input('input-fim', 'value')
)
def update_graph_vitorias(n_clicks, carta, inicio, fim):
    if n_clicks is None:
        return {}
    
    response = requests.get(f'http://127.0.0.1:5000/vitorias_derrotas_carta?carta={carta}&inicio={inicio}&fim={fim}')
    data = response.json()

    df = pd.DataFrame({
        'Resultado': ['Vitórias', 'Derrotas'],
        'Quantidade': [data['vitorias'], data['derrotas']]
    })

    fig = px.pie(df, values='Quantidade', names='Resultado', title=f"Vitórias e Derrotas da Carta: {carta}")
    return fig

@app.callback(
    Output('graph-decks', 'figure'),
    Input('submit-decks', 'n_clicks'),
    Input('input-percentual', 'value'),
    Input('input-inicio', 'value'),
    Input('input-fim', 'value')
)
def update_graph_decks(n_clicks, percentual, inicio, fim):
    if n_clicks is None:
        return {}
    
    response = requests.get(f'http://127.0.0.1:5000/decks_vitorias?percentual={percentual}&inicio={inicio}&fim={fim}')
    data = response.json()

    # Transformar a resposta em um DataFrame
    decks = []
    for deck, stats in data.items():
        decks.append({'Deck': ', '.join(deck), 'Vitórias': stats['vitorias'], 'Total': stats['total']})
    
    df = pd.DataFrame(decks)

    fig = px.bar(df, x='Deck', y='Vitórias', title='Decks com Percentual de Vitórias', color='Vitórias', 
                 labels={'Vitórias': 'Número de Vitórias'})
    return fig

@app.callback(
    Output('output-derrotas', 'children'),
    Input('submit-derrotas', 'n_clicks'),
    Input('input-combo', 'value'),
    Input('input-inicio', 'value'),
    Input('input-fim', 'value')
)
def calculate_derrotas(n_clicks, combo, inicio, fim):
    if n_clicks is None:
        return ""
    
    cartas = combo.split(',')
    response = requests.get(f'http://127.0.0.1:5000/derrotas_combo?cartas={cartas}&inicio={inicio}&fim={fim}')
    data = response.json()

    return f"Total de Derrotas com o Combo {combo}: {data['derrotas']}"

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)