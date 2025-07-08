from django.conf import settings
import geopandas
import pandas as pd
#from django_plotly_dash import DjangoDash
from sqlalchemy import create_engine
from dash import dcc,dash_table,html,Dash
from dash.dependencies import Input,Output,State
import dash_bootstrap_components as dbc
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import shapely
from django_plotly_dash import DjangoDash

 
HOST = 'localhost'
NAME= 'elecciones23'
PASS='4rcg1s2024'
conn = create_engine("postgresql+psycopg2://elecciones23:"+PASS+"@"+HOST+":5432/"+NAME)

sql_total_personal="""SELECT distrito_name as distrito,seg_extena, personal_led, personal_sacas,personal_con_cargo, total from totales_personal"""

df = pd.read_sql(sql_total_personal, conn)
df=df.fillna(0)

sql_lugar_personal="""SELECT  case when distrito <> '-' then distrito else 'CGE' END as distrito ,lugar, count(*) as cantidad from exportarpersonal group by distrito, lugar """
df_cant = pd.read_sql(sql_lugar_personal, conn)
df_cant=df_cant.sort_values(by='cantidad', ascending=False)

colores = {
    'DISTRITO': '#1f77b4',  # Azul
    'SECCION': '#ff7f0e',  # Naranja
    'LOCAL': '#2ca02c',   # Verde
    'CGE': '#cc66ff',  # violeta
    'SUBDISTRITO': '#ffff00' # amarillo
}

def crear_graf_pers(df):
    df_grouped = df.groupby('lugar')['cantidad'].sum().reset_index()

    
      # Crear una lista de colores en el orden de los lugares
    colores_ordenados = [colores[lugar] for lugar in df_grouped['lugar']]

    # Crear el gráfico circular
    fig = go.Figure(data=[
        go.Pie(
            labels=df_grouped['lugar'],
            values=df_grouped['cantidad'],
            marker=dict(colors=colores_ordenados),  # Asignar colores personalizados
            textinfo='label+percent',  # Mostrar etiqueta y porcentaje
            hoverinfo='label+value+percent'  # Información al pasar el cursor
        )
    ])

    # Configurar el layout
    fig.update_layout( plot_bgcolor='rgb(40, 40, 40)', title_x=0.5,autosize=True, height=700,
                           paper_bgcolor='rgb(40, 40, 40)', title_font_size=25, font_color='rgb(255, 255, 255)',showlegend=True,font_size=12
                           ,legend=dict(orientation="h", ))
    return fig

mi_plantilla = dict(
        layout=go.Layout(plot_bgcolor='rgb(40, 40, 40)', paper_bgcolor='rgb(40, 40, 40)', 
                         title_x=0.5, title_font_size=20, font_color='rgb(255, 255, 255)'))
def crear_barras(df):
    df_pivot = df.pivot(index='distrito', columns='lugar', values='cantidad').fillna(0)
# Calcular los totales por distrito
    totales = df_pivot.sum(axis=1)
    df_pivot = df_pivot.loc[totales.sort_values(ascending=True).index]
    # Crear el gráfico de barras apiladas horizontal
    fig = go.Figure()
    # Añadir una barra por cada lugar
    for lugar in df_pivot.columns:
        fig.add_trace(
            go.Bar(
                name=lugar,
                y=df_pivot.index,
                x=df_pivot[lugar],
                orientation='h',  # Orientación horizontal
                marker=dict(color=colores.get(lugar, '#000000')) 
            )
        )
    fig.update_traces(hovertemplate="%{x}")
    # Configurar el layout para barras apiladas
    fig.update_layout(
        barmode='stack',
        title='',
        font_size=12,
        # yaxis_title='Lugar',
        # xaxis_title='Cantidad',
        showlegend=True,
    margin=dict(l=120, r=20), 
    autosize=True,height=700, 
        template=mi_plantilla,
        legend=dict(orientation="h", )
    )

    # Añadir los valores totales al lado de las barras
    for i, total in enumerate(totales):
        fig.add_annotation(
            y=totales.index[i],
            x=total,
            text=str(int(total)),
            showarrow=False,
            xshift=20,  # Ajustar la posición horizontal del texto
            font=dict(size=12)
        )

    # Mostrar el gráfico
    return fig
def crear_indicadores(df_data,tipo):
    height=175
    size=50    
    color='rgb(255, 194, 102)'
    if tipo=='total':
        valor=df_data['total'].sum() 
        titulo=''
        color='rgb(255, 194, 102)'
        height=80
        size=65
    if tipo=='organizacion':
        valor=df_data['personal_con_cargo'].sum() 
        titulo='ORGANIZACION,<br>CGE,SEG LOC'   
        
        
        size=50
    if tipo=='seg_ext':
        valor=df_data['seg_extena'].sum()
        titulo='SEG EXTERNA'
        
    if tipo=='seg_led':
        valor=df_data['personal_led'].sum()
        titulo='SEG LED' 
         
    if tipo=='sacas':
        valor=df_data['personal_sacas'].sum()
        titulo='SEG SACAS'
        
         
    graf_total = go.Figure()
    
    graf_total.add_trace(go.Indicator(
        mode="number",
        number={"font": {"size": size}, 'valueformat':"5.d"},
        value=valor,
        domain={'x': [0, 1], 'y': [0, 1]}))
    graf_total.update_layout(autosize=True, height=height, title_text=titulo, plot_bgcolor='rgb(40, 40, 40)',
                             paper_bgcolor='rgb(40, 40, 40)',
                             grid={'rows': 3, 'columns': 1, 'pattern': "independent"}, title_x=0.5, title_y=0.9, font=dict(
            size=20, color=color

        ))
  
    return graf_total

distritos=df_cant.drop_duplicates('distrito')['distrito'].sort_values()
app = DjangoDash(name='distribucionPersonal',  external_stylesheets=[dbc.themes.DARKLY])
todos = [{"label": 'TODOS', "value": 'TODOS'}]
app.layout = html.Div(
        [   
            dbc.Row([html.H1('TOTAL DE PERSONAL Y SU DISTRIBUCIÓN', style={'textAlign': 'center', 'background-color': '#267300'})]),
            dbc.Row([dbc.Select(id="selec_distrito",
                                options=todos + [{"label": x, "value": x} for x in distritos],placeholder='DISTRITO' )]),
            dbc.Row([dbc.Col([dcc.Loading(id="ls-loading-1", children=[dcc.Graph(id='total', figure=crear_indicadores(df,'total'))], type="default")],
                              style={"height": "100%", }, md=12),]),                   
                               
            dbc.Row([dbc.Col([dbc.Row([dcc.Loading(id="ls-loading-2", children=[dcc.Graph(id='grafico1', figure=crear_indicadores(df,'organizacion'))],type="default")]),                              
                              dbc.Row([dcc.Loading(id="ls-loading-3", children=[dcc.Graph(id='grafico9', figure=crear_indicadores(df,'seg_ext'))], type="default")]),
                              dbc.Row([dcc.Loading(id="ls-loading-4", children=[dcc.Graph(id='grafico2', figure=crear_indicadores(df,'seg_led'))], type="default")]),
                               dbc.Row([dcc.Loading(id="ls-loading-5", children=[dcc.Graph(id='grafico3',figure=crear_indicadores(df,'sacas') )], type="default")])


                              ], style={"height": "100%", }
                             , md=3),


                     dbc.Col([dbc.Row([dcc.Loading(id="ls-loading-6", children=[dcc.Graph(id='circular1',figure=crear_graf_pers(df_cant) )], type="default")])], style={"height": "100%", }, md=4),

                     dbc.Col([dbc.Row([dcc.Loading(id="ls-loading-7", children=[dcc.Graph(id='barras', figure=crear_barras(df_cant))], type="default")]),
                              ],style={"height": "100%", },md=5),
                     ], className="g-0", ),
             dcc.Interval(
                id='interval-component',
                interval=60 * 1000,  # in milliseconds
                n_intervals=0
            )
        ]
    )

@app.callback(
    Output('total', 'figure', ), Output('grafico1','figure'),Output('grafico9','figure'),
    Output('grafico2','figure'),Output('grafico3','figure'),Output('circular1','figure'),Output('barras','figure'),
    Input('selec_distrito', 'value'),
    prevent_initial_call=True
)
def actualizar(distrito, **kwargs):
    df = pd.read_sql(sql_total_personal, conn)
    datos_indi=df=df.fillna(0)
    df_cant = pd.read_sql(sql_lugar_personal, conn)
    datos_graf=df_cant.sort_values(by='cantidad', ascending=False) 
    if distrito and distrito != 'TODOS':
        datos_indi = df[df['distrito'] == distrito]
        datos_graf=df_cant[df_cant['distrito']==distrito]
             
    total=crear_indicadores(datos_indi,'total')
    organizacion=crear_indicadores(datos_indi,'organizacion')
    seg_ext=crear_indicadores(datos_indi,'seg_ext')
    seg_led=crear_indicadores(datos_indi,'seg_led')
    sacas=crear_indicadores(datos_indi,'sacas')
    graf_pers=crear_graf_pers(datos_graf)
    barras=crear_barras(datos_graf)
    return total, organizacion, seg_ext, seg_led, sacas, graf_pers, barras     







