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
        id='rarity-dropdown',
        options=[
            {'label': 'Common', 'value': 'Common'},
            {'label': 'Rare', 'value': 'Rare'},
            {'label': 'Epic', 'value': 'Epic'}
        ],
        value='Common'
    ),
    dcc.Graph(id='rarity-graph')
])

# Callback para atualizar o gráfico com base na raridade selecionada
@app.callback(
    Output('rarity-graph', 'figure'),
    [Input('rarity-dropdown', 'value')]
)
def update_graph(rarity):
    """Atualiza o gráfico de acordo com a raridade selecionada"""
    # Fazer a requisição para a API Flask
    response = requests.get(f'http://localhost:5000/cards/{rarity}')
    cards = response.json()
    df = pd.DataFrame(cards)

    # Criar o gráfico de barras usando Plotly
    fig = px.bar(df, x='name', y='elixir', title=f'Elixir por Card ({rarity})')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)