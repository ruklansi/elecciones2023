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
from shapely.geometry import Point

HOST ='localhost' #settings.DATABASES['default']['HOST']
NAME= 'elecciones23'#settings.DATABASES['default']['NAME']
PASS='4rcg1s2024'#settings.DATABASES['default']['PASSWORD']
conn = create_engine("postgresql+psycopg2://elecciones23:"+PASS+"@"+HOST+":5432/"+NAME)


sql="""
 SELECT * FROM public.despliegue_repliegue
 """
sql_telegramas="""
 SELECT * FROM public.trasmision_telegramas
"""
df_telegrama = geopandas.GeoDataFrame.from_postgis(sql_telegramas, conn)
df_telegrama.to_crs(epsg=4326, inplace=True)
df_telegrama['tranmistido']=round(df_telegrama['cant_tranmitida']*100/df_telegrama['total'],2)
df = geopandas.GeoDataFrame.from_postgis(sql, conn)
df.to_crs(epsg=4326, inplace=True)
df['repliegue']=round(df['replegado']*100/df['total'],2)

distritos=df.drop_duplicates('distrito')['distrito'].sort_values()

sql_malvinas="""
 SELECT nam,geom, -51.74153477642776 as lat,59.38576589695881 as lon FROM public.malvinas
"""
gdf_poligono = geopandas.read_postgis(sql_malvinas, conn, geom_col='geom')
gdf_poligono.to_crs(epsg=4326, inplace=True)
#gdf_poligono.simplify(tolerance=1000, preserve_topology=True)
poligono_geojson = gdf_poligono.__geo_interface__

def estado_urnas(distrito):
    if distrito and distrito != 'TODOS':
        sql_mesas="""
        SELECT * FROM public.mesas_estados where distrito='"""+distrito+"""'"""
    else:
        sql_mesas="""
        SELECT * FROM public.mesas_estados """   
    df_mesas= pd.read_sql(sql_mesas, conn)
    df_mesas=df_mesas.drop(columns=['punto', ])
    urnas=len(df_mesas)-df_mesas['entrego_correo'].sum()
    urnas_en_correo=df_mesas['entrego_correo'].sum()-df_mesas['entrego_urna_en_led'].sum()

    urnas_en_led=df_mesas['entrego_urna_en_led'].sum()
    return [str(urnas),str(urnas_en_correo),str(urnas_en_led)]

def crear_mapa(df, zoom):
    center=shapely.box(*df.total_bounds).centroid
    colorscale = ["rgb(255, 230, 230)", "rgb(210, 231, 154)", "rgb(94, 179, 39)", "rgb(67, 136, 33)", "rgb(33, 74, 12)"]
    px.set_mapbox_access_token('pk.eyJ1IjoiemFsaXRvYXIiLCJhIjoiYVJFNTlfbyJ9.mPX8qTsRUGOOETl0CtA-Pg')
    punto = Point(-59.5236, -51.7963)  # Longitud, Latitud (centro del círculo)
    gdf_circulo = geopandas.GeoDataFrame(geometry=[punto], crs="EPSG:4326")
    # Proyectar a UTM para un buffer preciso en metros
    gdf_circulo = gdf_circulo.to_crs("EPSG:32721")  # UTM zona 21S (ajusta según la ubicación)
    gdf_circulo['geometry'] = gdf_circulo.geometry.buffer(280000)  # Buffer de 10 km
    gdf_circulo = gdf_circulo.to_crs("EPSG:4326")  # Volver a WGS84 para Mapbox

    # Crear el mapa coroplético base
    mapa = px.choropleth_mapbox(
        df,
        geojson=df.geom,
        locations=df.index,
        hover_data={'id': False, "departamen": True, "sde": True, "total": True, 'cant_tranmitida': True},
        color='tranmistido',
        color_continuous_scale=colorscale,
        color_continuous_midpoint=0,
        range_color=(0, 100),
        mapbox_style="open-street-map",
        center={'lat': center.y, 'lon': center.x},
        zoom=zoom,
        opacity=0.7,
        height=750
    )

    # Actualizar el diseño del mapa
    mapa.update_layout(
        hoverlabel_bgcolor='#ffffff',
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    # Personalizar la plantilla de hover
    mapa.update_traces(
        hovertemplate='<b>%{customdata[1]}  </b><br>Transmitidos:%{customdata[4]}<br>Total:%{customdata[3]}'
    )

    # Agregar la capa del círculo (debajo de todo)
    mapa.add_choroplethmapbox(
        geojson=gdf_circulo.__geo_interface__,
        locations=gdf_circulo.index,
        z=[1] * len(gdf_circulo),
        colorscale=[[0, 'rgba(170, 211, 223, 1)'], [1, 'rgba(170, 211, 223, 1)']],
        showscale=False,
          hoverinfo='text',  # Activar etiqueta al pasar el cursor
         text=['Islas Malvinas'] * len(gdf_poligono),  # Etiqueta para el polígono
        marker_line_color='rgba(170, 211, 223, 0.6)',  # Borde igual al fondo
        marker_line_width=1,
        
    )

# Agregar la capa del polígono (encima del círculo, debajo del mapa coroplético principal)
    mapa.add_choroplethmapbox(
        geojson=poligono_geojson,
        locations=gdf_poligono.index,
        z=[1] * len(gdf_poligono),
        colorscale=[[0, 'rgb(242, 239, 233, 0.6)'], [1, 'rgb(242, 239, 233, 0.6)']],
        showscale=False,
        hoverinfo='text',  # Activar etiqueta al pasar el cursor
         text=['Islas Malvinas'] * len(gdf_poligono),  # Etiqueta para el polígono
    )
    

    return mapa


def crear_porcentaje(df, graf_rep):
    if graf_rep=='rep':
        data=round(df['repliegue'].mean(skipna = True),2)
        titulo='ESTADO DEL REPLIEGUE'
    else:
        data=round(df['tranmistido'].mean(skipna = True),2)    
        titulo='TRANSMISIÓN DE TELEGRAMAS'
    fig = go.Figure(
        go.Indicator(
            mode='gauge+number',
            value=data,
            number={"font": {"size": 50,"color":'white'},'suffix': "%"},
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 2,'tickcolor':'white',},
                'bar': {'color': "red"},
                'borderwidth': 2,
                'steps': [
                    {'range': [0, 50], 'color': 'pink'},
                    {'range': [50, 75], 'color': 'yellow'},
                    {'range': [75 ,100], 'color': 'green'}],
            }
        )
    )

    fig.update_layout(height=370,title_text=titulo,autosize=True, 
        font={'color': "white", 'family': "Arial",'size':20},grid={'rows': 1, 'columns': 1, 'pattern': "independent"}, title_x=0.5,
        
        plot_bgcolor='rgb(40, 40, 40)',
    
        paper_bgcolor='rgb(40, 40, 40)',
    )


    return fig
def crear_indicadores(df_data,accion):
    data = df_data.drop(columns=['geom', ])
    color='#ffffff'
    if accion=='total':
        valor=data['total'].sum()
        titulo='TOTAL TELEGRAMAS'
      
    if accion=='ini':
        valor=data['cant_tranmitida'].sum()
        titulo='TRANSMITIDOS' 
        color="#085f0c"
         

    graf_total = go.Figure()
    graf_total.add_trace(go.Indicator(
        mode="number",
        number={"font": {"size": 80}, 'valueformat': 'f'},
        value=valor,
        domain={'x': [0, 1], 'y': [0, 1]}),
        
        )
    

    graf_total.update_layout(autosize=True, height=400, title_text=titulo,legend_title_font_size=80, plot_bgcolor='rgb(40, 40, 40)',
                             paper_bgcolor='rgb(40, 40, 40)' ,
                             grid={'rows': 1, 'columns': 1, 'pattern': "independent"}, title_x=0.5, font=dict(
            size=18, color=color

        ))
    return graf_total


app = DjangoDash(name='Telegramas', external_stylesheets=[dbc.themes.DARKLY])
todos = [{"label": 'TODOS', "value": 'TODOS'}]
app.layout = html.Div(
        [   
            dbc.Row([html.H1('ESTADO DE TRANMISIÓN DE TELEGRAMAS', style={'textAlign': 'center', 'background-color': '#267300'})]),
            dbc.Row([dbc.Select(id="selec_distrito",
                                options=todos + [{"label": x, "value": x} for x in distritos],placeholder='DISTRITO' )]),
            dbc.Row([dbc.Col([html.H3('URNAS EN LOCAL', style={'textAlign': 'center', 'background-color': '#ff0000'})]),
                     dbc.Col([html.H3(id='urnas', children=[estado_urnas('TODOS')[0]])]),
                     dbc.Col([html.H3('EN CORREO', style={'textAlign': 'center', 'background-color': '#e6e600'})]),
                     dbc.Col([html.H3(id='urnas_correo', children=[estado_urnas('TODOS')[1]])]),
                     dbc.Col([html.H3('URNAS EN LED', style={'textAlign': 'center', 'background-color': '#267300'})]),
                     dbc.Col([html.H3(id='urnas_led', children=[estado_urnas('TODOS')[2]])])
                                                
        ]),                    
            dbc.Row([dbc.Col([dbc.Row([dcc.Loading(id="ls-loading-2", children=[dcc.Graph(id='grafico2', figure=crear_porcentaje(df_telegrama,'tele'))], type="default")]),
                              
                              dbc.Row([dcc.Loading(id="ls-loading-6", children=[dcc.Graph(id='grafico1', figure=crear_porcentaje(df,'rep'))], type="default")])
                              ], style={"height": "100%", }
                             , md=3),
                     dbc.Col([dbc.Row([dcc.Loading(id="ls-loading-3", children=[dcc.Graph(id='mapa', figure=crear_mapa(df_telegrama,3))], type="default")])], style={"height": "100%", }, md=6),

                     dbc.Col([dbc.Row([dcc.Loading(id="ls-loading-4", children=[dcc.Graph(id='total',figure=crear_indicadores(df_telegrama,'total') )], type="default")]),
                              dbc.Row([dcc.Loading(id="ls-loading-5", children=[dcc.Graph(id='ini', figure=crear_indicadores(df_telegrama,'ini'))], type="default")])
                              ],style={"height": "100%", },md=3),
                     ], className="g-0", ),
             dcc.Interval(
                id='interval-component',
                interval=120 * 1000,  # in milliseconds
                n_intervals=0
            )
        ]
    )

@app.callback([Output('mapa', 'figure'),
               Output('total', 'figure'),
               Output('ini', 'figure'),
               Output('grafico1', 'figure'),
               Output('grafico2', 'figure'),
               Output('urnas','children'),
               Output('urnas_correo','children'),
               Output('urnas_led','children')
               ],Input('selec_distrito', 'value'),Input('interval-component', 'n_intervals'),prevent_initial_call=True)
def actualizar_mapa(distrito,intervalo,**kwargs):
       
    zoom = 3
    if distrito and distrito != 'TODOS':
        sql="""SELECT * FROM public.despliegue_repliegue where distrito='"""+distrito+"""'"""
        sql_telegramas=""" SELECT * FROM public.trasmision_telegramas where distrito='"""+distrito+"""'"""
        datos = geopandas.GeoDataFrame.from_postgis(sql, conn)
        datos_mapa= geopandas.GeoDataFrame.from_postgis(sql_telegramas, conn)
        datos_mapa.to_crs(epsg=4326, inplace=True)

        esta_urnas=estado_urnas(distrito)
        if distrito=='CABA':
            zoom=11 
        elif distrito=='TUCUMÁN' or distrito=='JUJUY':
            zoom=7
        else:
            zoom=6    
    else:
        sql="""SELECT * FROM public.despliegue_repliegue"""
        sql_telegramas=""" SELECT * FROM public.trasmision_telegramas """
        datos = geopandas.GeoDataFrame.from_postgis(sql, conn)
        datos_mapa= geopandas.GeoDataFrame.from_postgis(sql_telegramas, conn)
        datos_mapa.to_crs(epsg=4326, inplace=True)      
        esta_urnas=estado_urnas('TODOS') 
    datos_mapa['tranmistido']=round(df_telegrama['cant_tranmitida']*100/df_telegrama['total'],2)    
    datos['repliegue']=round(df['replegado']*100/df['total'],2)
    return crear_mapa(datos_mapa,zoom),crear_indicadores(datos_mapa,'total'),crear_indicadores(datos_mapa,'ini'),crear_porcentaje(datos,'rep'),crear_porcentaje(datos_mapa,'tele'),esta_urnas[0],esta_urnas[1],esta_urnas[2]
