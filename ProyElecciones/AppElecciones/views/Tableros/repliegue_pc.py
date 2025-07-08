import os
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


HOST ='localhost' #settings.DATABASES['default']['HOST']
NAME= 'elecciones23'#settings.DATABASES['default']['NAME']
PASS='4rcg1s2024'#settings.DATABASES['default']['PASSWORD']
conn = create_engine("postgresql+psycopg2://elecciones23:"+PASS+"@"+HOST+":5432/"+NAME)

sql="""
 SELECT * FROM public.movimientos_repliegue_shp
 """
sql_mov="""
SELECT distrito,tipo FROM public.movimientos_des_rep
where tipo<>'DESPLIEGUE GRUESO (PERSONAL Y MEDIOS)' and tipo<>'DESPLIEGUE PELOTÓN ADELANTADO (PERSONAL Y MEDIOS)' and tipo<>'DESPLIEGUE PUESTO COMANDO (PERSONAL Y MEDIOS)'

"""
df_mov = pd.read_sql(sql_mov, conn)
df_mapa = geopandas.GeoDataFrame.from_postgis(sql, conn)
df_mapa.to_crs(epsg=4326, inplace=True)
df_mapa['repliegue']=round(df_mapa['finalizados']*100/df_mapa['total'],2)
distritos=df_mapa.drop_duplicates('distrito')['distrito'].sort_values()
def crear_mapa(df, zoom):
    center=shapely.box(*df.total_bounds).centroid
    colorscale = ["rgb(255, 230, 230)", "rgb(210, 231, 154)", "rgb(94, 179, 39)", "rgb(67, 136, 33)", "rgb(33, 74, 12)"]
    mapa= px.choropleth_mapbox(df,
                            geojson=df.geom,
                            locations=df.index,
                            hover_data={'id':False, 'distrito':True, "finalizados":True,"total":True,'repliegue':True},
                            color='repliegue',
                            #labels={'repliegue':'Estado del Repliegue'},
                            color_continuous_scale=colorscale,
                            color_continuous_midpoint=0,
                            range_color=(0, 100),
                            mapbox_style="open-street-map",
                            center={'lat':center.y, 'lon':center.x},
                            zoom=zoom,
                            opacity=0.7,
                            height=820
                            )
    mapa.update_layout(hoverlabel_bgcolor='#ffffff',

                        margin={"r": 0, "t": 0, "l": 0, "b": 0}
                       )
    mapa.update_traces(hovertemplate='<b>%{customdata[1]}: %{customdata[4]}% </b><br>Replegados:%{customdata[2]}<br>Total:%{customdata[3]}')
    return mapa

df=df_mapa.fillna(0)
df_mov = pd.read_sql(sql_mov, conn)
df_mov=df_mov.value_counts(dropna=False).reset_index()

sql_mov_lista="""
SELECT distrito,tipo,inicio as ini,fin,efectivos as ef, vehiculos as veh FROM public.movimientos_des_rep
where tipo<>'DESPLIEGUE GRUESO (PERSONAL Y MEDIOS)' and tipo<>'DESPLIEGUE PELOTÓN ADELANTADO (PERSONAL Y MEDIOS)' and tipo<>'DESPLIEGUE PUESTO COMANDO (PERSONAL Y MEDIOS)'
"""
df_mov_lista = pd.read_sql(sql_mov_lista, conn)
df_mov_lista['ini']=df_mov_lista['ini'].dt.strftime('%d/%m %H:%M')
df_mov_lista['fin']=df_mov_lista['fin'].dt.strftime('%d/%m %H:%M')

def crear_tabla(df_mov_lista):
    data_table = dash_table.DataTable(df_mov_lista.to_dict('records'),
                                    [{"name": i, "id": i.lower()} for i in ['Distrito','Tipo','Ef','Veh', 'Ini', 'Fin']],
                                    id='datatable',
                                    editable=False,
                                    
                                    sort_action="native",
                                    sort_mode="multi",
                                    selected_columns=[],
                                    selected_rows=[],
                                
                                    page_action="native",
                                    page_current=0,
                                    page_size=13,
                                    style_cell={'textAlign': 'center','fontSize':11, 'font-family':'sans-serif'},
                                    style_data={
                                        'color': 'black',
                                        'backgroundColor': 'white'

                                    },
                                    style_header={
                                        'backgroundColor': 'rgb(210, 210, 210)',
                                        'color': 'black',
                                        'fontWeight': 'bold'
                                    }

                                    )
    return data_table

mi_plantilla = dict(
        layout=go.Layout(plot_bgcolor='rgb(40, 40, 40)', paper_bgcolor='rgb(40, 40, 40)', hovermode="x unified",
                         title_x=0.5, title_font_size=20, font_color='rgb(255, 255, 255)'))

def crear_barras(df):
    fig=px.bar(df, y="distrito", x="count", color="tipo", text_auto=True,orientation='h')
    fig.update_traces(hovertemplate="%{x}")
    fig.update_layout(barmode='stack', title_text='MOVIMIENTOS POR DISTRITO', showlegend=False,template=mi_plantilla,
                      margin=dict(l=120, r=20), hovermode='x',
                      autosize=True,height=820, 
                      )
    return fig

def crear_graf_movimientos(df):
    fig = px.pie(df, values='count', names='tipo',hole=.4,title='Cantidad de Movimientos')
   
    fig.update_layout( plot_bgcolor='rgb(40, 40, 40)', title_x=0.5,autosize=True, height=375,
                           paper_bgcolor='rgb(40, 40, 40)', title_font_size=25, font_color='rgb(255, 255, 255)',showlegend=False)
    fig.update_traces(hoverinfo='label', textinfo='percent', textfont_size=20,
                           marker=dict(line=dict(color='#000000', width=2)))
    return fig

app = DjangoDash(name='Repliegue_pc',  external_stylesheets=[dbc.themes.DARKLY])
todos = [{"label": 'TODOS', "value": 'TODOS'}]
app.layout = html.Div(
        [   
            dbc.Row([html.H1('REPLIEGUE PERSONAL Y MEDIOS DESDE PUESTO COMANDO ', style={'textAlign': 'center', 'background-color': '#267300'})]),
            dbc.Row([dbc.Select(id="selec_distrito",
                                options=todos + [{"label": x, "value": x} for x in distritos],placeholder='DISTRITO' )]),
                               
            dbc.Row([dbc.Col([dbc.Row([dcc.Loading(id="ls-loading-2", children=[crear_tabla(df_mov_lista)], type="default")]),
                              
                              dbc.Row([dcc.Loading(id="ls-loading-6", children=[dcc.Graph(id='grafico1',figure=crear_graf_movimientos(df_mov) )], type="default")])
                              ], style={"height": "100%", }
                             , md=5),
                     dbc.Col([dbc.Row([dcc.Loading(id="ls-loading-3", children=[dcc.Graph(id='mapa', figure=crear_mapa(df,3))], type="default")])], style={"height": "100%", }, md=4),

                     dbc.Col([dbc.Row([dcc.Loading(id="ls-loading-4", children=[dcc.Graph(id='barras',figure=crear_barras(df_mov) )], type="default")]),
                              ],style={"height": "100%", },md=3),
                     ], className="g-0", ),
             dcc.Interval(
                id='interval-component',
                interval=60 * 1000,  # in milliseconds
                n_intervals=0
            )
        ]
    )
@app.callback(
    Output('mapa', 'figure', ), Output('barras','figure'),Output('ls-loading-2','children'),Output('grafico1','figure'),
    Input('selec_distrito', 'value'),  [State('datatable', 'data')],
    prevent_initial_call=True
)
def actualizar(distrito,datatable, **kwargs):
    
    zoom = 3
    df_mapa = geopandas.GeoDataFrame.from_postgis(sql, conn)
    df_mapa.to_crs(epsg=4326, inplace=True)
    df_mapa['repliegue']=round(df_mapa['finalizados']*100/df['total'],2) 
    datos_barra = pd.read_sql(sql_mov, conn)
    datos_barra=datos_barra.value_counts(dropna=False).reset_index()
    df_mov_lista = pd.read_sql(sql_mov_lista, conn)
    df_mov_lista['ini']=df_mov_lista['ini'].dt.strftime('%d/%m %H:%M')
    df_mov_lista['fin']=df_mov_lista['fin'].dt.strftime('%d/%m %H:%M')

    if distrito and distrito != 'TODOS':
        datos_mapa = df_mapa[df_mapa['distrito'] == distrito]
        datos_barra=datos_barra[datos_barra['distrito']==distrito]
        df_mov_lista=df_mov_lista[df_mov_lista['distrito']==distrito]
        zoom = 5        
    barras=crear_barras(datos_barra)
    mapa=crear_mapa(datos_mapa,zoom)
    grafico=crear_graf_movimientos(datos_barra)
    return mapa,barras,crear_tabla(df_mov_lista),grafico

