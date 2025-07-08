from django.conf import settings

from django_plotly_dash import DjangoDash

from sqlalchemy import create_engine
HOST = settings.DATABASES['default']['HOST']
NAME= settings.DATABASES['default']['NAME']
PASS=settings.DATABASES['default']['PASSWORD']
conn = create_engine("postgresql+psycopg2://elecciones23:"+PASS+"@"+HOST+":5432/"+NAME)

import pandas as pd
import plotly.graph_objs as go
import dash
from dash import Dash, dcc, html
#import chart_studio.plotly as py
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html


sql = """SELECT distrito, count(id) as cantidad, 
sum(case when tipo_veh='CONTRATADO' then 1 else 0 end) as contratados,
 sum(case when tipo_veh='PROPIO' then 1 else 0 end) as propios,
 sum(case when tipo_vehiculo_provisto='COLECTIVO' then 1 else 0 end) as colectivos,
 sum(case when tipo_vehiculo_provisto='CAMIÓN' or tipo_vehiculo_provisto='UNIMOG' or tipo_vehiculo_provisto='TRAILER' or tipo_vehiculo_provisto='REO' then 1 else 0 end) as camion,
 sum(case when tipo_vehiculo_provisto='CAMIONETA' then 1 else 0 end) as CAMIONETA,
  sum(case when tipo_vehiculo_provisto='AUTOMÓVIL' or tipo_vehiculo_provisto='JEEP' then 1 else 0 end) as AUTO,
  sum(case when tipo_vehiculo_provisto='MULA' or tipo_vehiculo_provisto='CABALLO' then 1 else 0 end) as mula,
  sum(case when tipo_vehiculo_provisto='HELOCÓPTERO' then 1 else 0 end) as helicoptero,
  sum(case when tipo_vehiculo_provisto='MOTOCICLETA' then 1 else 0 end) as moto,
 sum(case when tipo_vehiculo_provisto='EMBARCACIÓN' then 1 else 0 end) as barco,
 sum(case when tipo_vehiculo_provisto='AMBULANCIA' then 1 else 0 end) as ambulancia
 FROM vehiculos23 group by distrito
"""
app = DjangoDash(name='Vehiculos',external_stylesheets=[dbc.themes.DARKLY])
try:
    df = pd.read_sql(sql, conn)
    df = df.sort_values('cantidad', ascending=True)
    df['total'] = df['colectivos'] + df['camion'] + df['camioneta'] + df['auto'] + df['mula'] + df['moto'] + df['barco'] + \
                  df['ambulancia'] + df['helicoptero']

    app = DjangoDash(name='Vehiculos',external_stylesheets=[dbc.themes.DARKLY])
    todos = [{"label": 'TODOS', "value": 'TODOS'}]
    app.layout = html.Div(
        [
            dbc.Row([html.H1('DISTRIBUCÍON DE VEHÍCULOS', style={'textAlign': 'center', 'background-color': '#267300'})]),
            dbc.Row([dbc.Select(id="selec_distrito",
                                options=todos + [{"label": x, "value": x} for x in df['distrito'].sort_values()], placeholder='  DISTRITO')]),
            dbc.Row([dbc.Col([dbc.Row([dcc.Graph(id='total')]),
                              dbc.Row([dcc.Graph(id='contratados')]),
                              dbc.Row(dcc.Graph(id='propios')),
                              ], style={"height": "100%", }
                             , md=3),
                     dbc.Col([dbc.Row([dcc.Graph(id='veh_por_dis')])], style={"height": "100%", }, md=6),

                     dbc.Col([dbc.Row([dcc.Graph(id='pie_categoria', )]),
                              dbc.Row([dcc.Graph(id='pie_tipo', )])],style={"height": "100%", },md=3),
                     ], className="g-0", ),

        ]
    )
except:
    pass


@app.callback(
    Output('veh_por_dis', 'figure'), Output('total', 'figure'), Output('contratados', 'figure'),
    Output('propios', 'figure'), Output('pie_categoria', 'figure'), Output('pie_tipo', 'figure'),
    [Input('selec_distrito', 'value')]
)
def actualizar_div(valor_entrada):
    lista = ['colectivos', 'camion', 'camioneta', 'auto', 'mula', 'moto', 'barco', 'ambulancia', 'helicoptero']
    df_filtrado = df[df['distrito'] == valor_entrada]
    if not valor_entrada or valor_entrada == 'TODOS':
        distritos = df['distrito']
        propios = df['propios']
        contratados = df['contratados']
        total = df.sum(axis=0)['cantidad']
        cont_ind = df.sum(axis=0)['contratados']
        prop_ind = df.sum(axis=0)['propios']
        datos = {a: df.sum(axis=0)[a] for a in lista}
    else:
        distritos = df_filtrado['distrito']
        propios = df_filtrado['propios']
        contratados = df_filtrado['contratados']
        total = df_filtrado.sum(axis=0)['cantidad']
        cont_ind = df_filtrado.sum(axis=0)['contratados']
        prop_ind = df_filtrado.sum(axis=0)['propios']
        datos = {a: df_filtrado.sum(axis=0)[a] for a in lista}
    mi_plantilla = dict(
        layout=go.Layout(plot_bgcolor='rgb(40, 40, 40)', paper_bgcolor='rgb(40, 40, 40)', hovermode="x unified",
                         title_x=0.5, title_font_size=20, font_color='rgb(255, 255, 255)')
    )
    fig = go.Figure([go.Bar(name='PROPIOS', y=distritos, x=propios, marker_color='rgb(0, 179, 0)',
                            marker_line_color='rgb(51, 255, 51)',
                            marker_line_width=2, opacity=0.7, text=propios, orientation='h'),
                     go.Bar(name='CONTRATADOS', y=distritos,
                            x=contratados,
                            marker_color='rgb(255, 153, 51)',
                            marker_line_color='rgb(255, 166, 77)',
                            marker_line_width=1.5, opacity=0.7, text=contratados, orientation='h', )])
    fig.update_traces(hovertemplate="%{x}")
    fig.update_layout(barmode='stack', title_text='VEHICULOS POR DISTRITO', template=mi_plantilla,
                      margin=dict(l=120, r=20), hovermode='y',
                      autosize=True,height=750, legend=dict(
            yanchor="bottom",
            y=0.95,
            xanchor="left",
            x=0.95,
        )
                      )
    graf_total = go.Figure()
    graf_total.add_trace(go.Indicator(
        mode="number",
        value=total,
        domain={'row': 0, 'column': 1}))

    graf_total.update_layout(autosize=True,height=250,  title_text='TOTAL VEHÍCULOS',
                             plot_bgcolor='rgb(40, 40, 40)', paper_bgcolor='rgb(40, 40, 40)',
                             grid={'rows': 1, 'columns': 1, 'pattern': "independent"}, title_x=0.5, font=dict(
            size=18, color='rgb(255, 255, 255)'

        ))
    graf_cont = go.Figure()
    graf_cont.add_trace(go.Indicator(
        mode="number",
        value=cont_ind,
        domain={'row': 0, 'column': 1}))

    graf_cont.update_layout(autosize=True,height=250, title_text='VEHÍCULOS CONTRATADOS',
                            plot_bgcolor='rgb(40, 40, 40)', paper_bgcolor='rgb(40, 40, 40)',
                            grid={'rows': 1, 'columns': 1, 'pattern': "independent"}, title_x=0.5, font=dict(
            size=18, color='rgb(255, 255, 255)'

        ))

    graf_prop = go.Figure()
    graf_prop.add_trace(go.Indicator(
        mode="number",
        value=prop_ind,
        # domain = {'row': 0, 'column': 0}
    ))

    graf_prop.update_layout(autosize=True, height=250, title_text='VEHÍCULOS PROPIOS',
                            plot_bgcolor='rgb(40, 40, 40)', paper_bgcolor='rgb(40, 40, 40)',
                            grid={'rows': 1, 'columns': 1, 'pattern': "independent"}, title_x=0.5, font=dict(
            size=18, color='rgb(255, 255, 255)'

        ))

    # pie_cont=df.sum(axis=0)['contratados']
    # pie_prop=df.sum(axis=0)['propios']
    labels = ['Contratados', 'Propios']
    values = [cont_ind, prop_ind]
    colors = ['rgb(255, 153, 51)', 'rgb(0, 179, 0)']
    fig_categoria = go.Figure([go.Pie(labels=labels, values=values, hole=.4)])
    fig_categoria.update_layout(title_text='POR CATEGORIA', plot_bgcolor='rgb(40, 40, 40)', title_x=0.5,autosize=True, height=375,showlegend=False,
                                paper_bgcolor='rgb(40, 40, 40)', title_font_size=25, font_color='rgb(255, 255, 255)')
    fig_categoria.update_traces(hoverinfo='label+value', textinfo='percent', textfont_size=20,
                                marker=dict(colors=colors, line=dict(color='#000000', width=2)))

    labels = list(datos.keys())
    values = list(datos.values())
    # colors = ['rgb(255, 153, 51)', 'rgb(0, 179, 0)']
    fig_tipo = go.Figure([go.Pie(labels=labels, values=values, hole=.4)])
    fig_tipo.update_layout(title_text='POR TIPO', plot_bgcolor='rgb(40, 40, 40)', title_x=0.5,autosize=True, height=375,
                           paper_bgcolor='rgb(40, 40, 40)', title_font_size=25, font_color='rgb(255, 255, 255)',showlegend=False)
    fig_tipo.update_traces(hoverinfo='label+value', textinfo='percent', textfont_size=20,
                           marker=dict(line=dict(color='#000000', width=2)))

    return fig, graf_total, graf_cont, graf_prop, fig_categoria, fig_tipo


# Configure app layout

