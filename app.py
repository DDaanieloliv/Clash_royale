import logging
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

app = Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id='bar-chart-dropdown',
        options=[
            {'label': 'Cartas', 'value': '_id'},
        ],
        value='_id'
    ),
    dcc.Graph(id='bar-chart')
])

@app.callback(
    Output('bar-chart', 'figure'),
    Input('bar-chart-dropdown', 'value')
)
def update_bar_chart(selected_column):
    logging.debug(f'Atualizando gráfico para coluna: {selected_column}')
    # Código do gráfico aqui...
    pass

if __name__ == '__main__':
    logging.debug('Iniciando servidor Dash...')
    app.run(debug=True)