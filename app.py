import dash
import dash_core_components as dcc
import dash_html_components as html


from _plotly_future_ import v4_subplots
from plotly import offline as py

import plotly.graph_objects as go
from plotly.subplots import make_subplots


import pandas as pd
import numpy as np
from datetime import date


df = pd.read_csv('covid19.csv', sep=",")
df['Date'] = df['Date'].apply(lambda x: pd.to_datetime(x))
df['Hauts-de-France'] = df['Hauts-de-France'].astype(np.int64)
df = df.set_index('Date')

regions = pd.read_csv('regions_data.csv', sep=",", encoding='latin1')


def generate_evol_plot(df):
    data = []
    for col in df.columns:
        data.append({'x': df.index, 'y': df[col], 'name': col, 'showlegend': False})
    return data


diff = df.iloc[-1] - df.iloc[-2]
total_cases = pd.DataFrame(df.sum())
total_cases = total_cases.reset_index()
total_cases.columns = ["Région", "nb"]

total_cases = pd.merge(total_cases, regions, on="Région")

total_cases['inf_per_pop'] = (total_cases['nb'] / total_cases['Population(2020)']) * 100
total_cases['inf_per_km'] = (total_cases['nb'] / total_cases['Superficie']) * 100

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(className='container', children=[
    html.H1(children='Dashboard Covid-19', id="Title"),
    html.Div(children=[html.H3(children='Quel est l\'évolution du Covid19 depuis hier ?'),
                       html.H4(children=str(diff.sum()) + ' cas recensés', id='green' if diff.sum() < 0 else 'red')]),

    dcc.Graph(
        id='bar_total_cases',
        figure={
            'data': [
                {'x': df.sum().index, 'y': df.sum().values, 'type': 'bar'},
            ],
            'layout': {
                'title': 'Nombre de cas total daté du ' + str(date.today())
            }
        }
    ),
    dcc.Graph(
            id='evolution_regions',
            figure={
                'data': generate_evol_plot(df),
                'layout': {
                    'title': 'Evolution du Covid-19 par régions'
                }
            }
        ),
    html.Div(className='row', children=[

        dcc.Graph(
                id='cas_per_pop',
                className='col m6',

                figure={
                    'data': [{'x': total_cases['Région'], 'y': total_cases['inf_per_pop'], 'type': 'bar'}],
                    'layout': {
                        'title': 'Nombre d\'infectés par nombre d\'habitants'
                    }
                }
            ),
            dcc.Graph(
                    id='cas_per_km',
                    className='col m6',
                    figure={
                        'data': [{'x': total_cases['Région'], 'y': total_cases['inf_per_km'], 'type': 'bar'}],
                        'layout': {
                            'title': 'Nombre d\'infectés par km carré'
                        }
                    }
                ),

    ])



    ])

if __name__ == '__main__':
    app.run_server(debug=True)
