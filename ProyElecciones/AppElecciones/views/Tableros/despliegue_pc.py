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
 SELECT * FROM public.movimientos_despliegue_shp
 """
sql_mov="""
SELECT distrito,tipo FROM public.movimientos_des_rep
where tipo<>'REPLIEGUE PELOTÓN ADELANTADO (PERSONAL Y MEDIOS)' and tipo<>'REPLIEGUE PUESTO COMANDO (PERSONAL Y MEDIOS)' and tipo<>'REPLIEGUE GRUESO (PERSONAL Y MEDIOS)'

"""
sql_malvinas="""
 SELECT nam,geom, -51.74153477642776 as lat,59.38576589695881 as lon FROM public.malvinas
"""
gdf_poligono = geopandas.read_postgis(sql_malvinas, conn, geom_col='geom')
gdf_poligono.to_crs(epsg=4326, inplace=True)
#gdf_poligono.simplify(tolerance=1000, preserve_topology=True)
poligono_geojson = gdf_poligono.__geo_interface__
df_mov = pd.read_sql(sql_mov, conn)
df_mapa = geopandas.GeoDataFrame.from_postgis(sql, conn)
df_mapa.to_crs(epsg=4326, inplace=True)
df_mapa['despliegue']=round(df_mapa['finalizados']*100/df_mapa['total'],2)
distritos=df_mapa.drop_duplicates('distrito')['distrito'].sort_values()
def crear_mapa(df, zoom):
    px.set_mapbox_access_token('pk.eyJ1IjoiemFsaXRvYXIiLCJhIjoiYVJFNTlfbyJ9.mPX8qTsRUGOOETl0CtA-Pg')
    punto = shapely.Point(-59.5236, -51.7963)  # Longitud, Latitud (centro del círculo)
    gdf_circulo = geopandas.GeoDataFrame(geometry=[punto], crs="EPSG:4326")
    # Proyectar a UTM para un buffer preciso en metros
    gdf_circulo = gdf_circulo.to_crs("EPSG:32721")  # UTM zona 21S (ajusta según la ubicación)
    gdf_circulo['geometry'] = gdf_circulo.geometry.buffer(280000)  # Buffer de 10 km
    gdf_circulo = gdf_circulo.to_crs("EPSG:4326")  # Volver a WGS84 para Mapbox
    center=shapely.box(*df.total_bounds).centroid
    colorscale = ["rgb(255, 230, 230)", "rgb(210, 231, 154)", "rgb(94, 179, 39)", "rgb(67, 136, 33)", "rgb(33, 74, 12)"]
    mapa= px.choropleth_mapbox(df,
                            geojson=df.geom,
                            locations=df.index,
                            hover_data={'id':False, 'distrito':True, "finalizados":True,"total":True,'despliegue':True},
                            color='despliegue',
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
    mapa.update_traces(hovertemplate='<b>%{customdata[1]}: %{customdata[4]}% </b><br>Desplegados:%{customdata[2]}<br>Total:%{customdata[3]}')

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
 
df=df_mapa.fillna(0)
df_mov = pd.read_sql(sql_mov, conn)
df_mov=df_mov.value_counts(dropna=False).reset_index()

sql_mov_lista="""
SELECT distrito,tipo,inicio as ini,fin,efectivos as ef, vehiculos as veh FROM public.movimientos_des_rep
where tipo<>'REPLIEGUE PELOTÓN ADELANTADO (PERSONAL Y MEDIOS)' and tipo<>'REPLIEGUE PUESTO COMANDO (PERSONAL Y MEDIOS)' and tipo<>'REPLIEGUE GRUESO (PERSONAL Y MEDIOS)'
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

app = DjangoDash(name='Despliegue_pc',  external_stylesheets=[dbc.themes.DARKLY])
todos = [{"label": 'TODOS', "value": 'TODOS'}]
app.layout = html.Div(
        [   
            dbc.Row([html.H1('DESPLIEGUE PERSONAL Y MEDIOS HACIA PTO(S) CDO DEL DISTRITO', style={'textAlign': 'center', 'background-color': '#267300'})]),
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
    df_mapa['despliegue']=round(df_mapa['finalizados']*100/df['total'],2) 
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



