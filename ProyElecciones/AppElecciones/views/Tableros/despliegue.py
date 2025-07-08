from django.conf import settings
import geopandas
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

sql="""SELECT * FROM public.despliegue_repliegue"""

df = geopandas.GeoDataFrame.from_postgis(sql, conn)
df.to_crs(epsg=4326, inplace=True)
df['despliegue']=df['desplegado']*100/df['total']
df['inicio_despliegue']=df['ini_des']*100/df['total']
distritos=df.drop_duplicates('distrito')['distrito'].sort_values()

sql_malvinas="""
 SELECT nam,geom, -51.74153477642776 as lat,59.38576589695881 as lon FROM public.malvinas
"""
gdf_poligono = geopandas.read_postgis(sql_malvinas, conn, geom_col='geom')
gdf_poligono.to_crs(epsg=4326, inplace=True)
#gdf_poligono.simplify(tolerance=1000, preserve_topology=True)
poligono_geojson = gdf_poligono.__geo_interface__
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
                            hover_data={'id':False, "departamen":True, "desplegado":True,"total":True,'despliegue':True},
                            hover_name='departamen',
                            color='despliegue',
                            #labels={'despliegue':'Estado del Despliegue %','departamen':'Departamento','distrito':'Distrito','desplegado':'Cir Desplegados','total':'Total Cir'},
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
    mapa.update_traces(hovertemplate='<b>%{customdata[1]} %{customdata[4]}</b><br>Desplegados:%{customdata[2]}<br>Total:%{customdata[3]}')

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
        data=round(df['despliegue'].mean(skipna = True),2)
        titulo='ESTADO DEL DESPLIEGUE'
    else:
        data=round(df['inicio_despliegue'].mean(skipna = True),2)    
        titulo='INICIARON EL DESPLIEGUE'
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

    fig.update_layout(height=400,title_text=titulo,autosize=True, 
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
        titulo='TOTAL CIRCUITOS'
    if accion=='desplegados':
        valor=data['act_no_ini'].sum()
        titulo='ACT. NO INICIADAS'   
    if accion=='ini':
        valor=data['ini_des'].sum()
        titulo='INICIARON DESPLIEGUE' 
        color='#e74c3c'
    if accion=='reple':
        valor=data['desplegado'].sum()
        titulo='DESPLEGADOS'  
        color= '#18c044'      

    graf_total = go.Figure()
    graf_total.add_trace(go.Indicator(
        mode="number",
        number={"font": {"size": 100}, 'valueformat': 'f'},
        value=valor,
        domain={'x': [0, 1], 'y': [0, 1]}),
        
        )
    

    graf_total.update_layout(autosize=True, height=270, title_text=titulo,legend_title_font_size=80, plot_bgcolor='rgb(40, 40, 40)',
                             paper_bgcolor='rgb(40, 40, 40)' ,
                             grid={'rows': 1, 'columns': 1, 'pattern': "independent"}, title_x=0.5, font=dict(
            size=18, color=color

        ))
    return graf_total


app = DjangoDash(name='Despliegue', external_stylesheets=[dbc.themes.DARKLY])
todos = [{"label": 'TODOS', "value": 'TODOS'}]
app.layout = html.Div(
        [   
            dbc.Row([html.H1('DESPLIEGUE DEL PERSONAL A LOS LOCALES', style={'textAlign': 'center', 'background-color': '#267300'})]),
            dbc.Row([dbc.Select(id="selec_distrito",
                                options=todos + [{"label": x, "value": x} for x in distritos],placeholder='DISTRITO' )]),
            dbc.Row([dbc.Col([
                              dbc.Row([dcc.Loading(id="ls-loading-3", children=[dcc.Graph(id='grafico2', figure=crear_porcentaje(df,'ini'))], type="default")]),
                              dbc.Row([dcc.Loading(id="ls-loading-7", children=[dcc.Graph(id='grafico1', figure=crear_porcentaje(df,'rep'))], type="default")])
                              ], style={"height": "100%", }
                             , md=3),
                     dbc.Col([dbc.Row([dcc.Loading(id="ls-loading-4", children=[dcc.Graph(id='mapa', figure=crear_mapa(df,3))], type="default")])], style={"height": "100%", }, md=6),

                     dbc.Col([dbc.Row([dcc.Loading(id="ls-loading-5", children=[dcc.Graph(id='total',figure=crear_indicadores(df,'total'))], type="default")]),
                              dbc.Row([dcc.Loading(id="ls-loading-6", children=[dcc.Graph(id='ini',figure=crear_indicadores(df,'ini') )], type="default")]),
                              dbc.Row([dcc.Loading(id="ls-loading-1", children=[dcc.Graph(id='reple', figure=crear_indicadores(df,'reple'))], type="default")])],style={"height": "100%", },md=3),
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
               Output('reple', 'figure'),
               Output('ini', 'figure'),
               Output('grafico1', 'figure'),
               Output('grafico2', 'figure')],Input('selec_distrito', 'value'),Input('interval-component', 'n_intervals'),prevent_initial_call=True)
def actualizar_mapa(distrito,intervalo,**kwargs):
    
    
    zoom = 3
 
    if distrito and distrito != 'TODOS':
        sql="""SELECT * FROM public.despliegue_repliegue where distrito='"""+distrito+"""'"""
        datos_mapa = geopandas.GeoDataFrame.from_postgis(sql, conn)
        datos_mapa.to_crs(epsg=4326, inplace=True)
        datos_mapa['despliegue']=round(datos_mapa['desplegado']*100/datos_mapa['total'],2)
        datos_mapa['inicio_despliegue']=round(datos_mapa['ini_des']*100/datos_mapa['total'],2)
        
        if distrito=='CABA':
            zoom=11 
        elif distrito=='TUCUMÁN' or distrito=='JUJUY':
            zoom=8
        else:
            zoom=6    
    else:
        sql="""SELECT * FROM public.despliegue_repliegue"""
        datos_mapa = geopandas.GeoDataFrame.from_postgis(sql, conn)
        datos_mapa.to_crs(epsg=4326, inplace=True)
        datos_mapa['despliegue']=round(datos_mapa['desplegado']*100/df['total'],2)
        datos_mapa['inicio_despliegue']=round(datos_mapa['ini_des']*100/datos_mapa['total'],2)      
         
    return crear_mapa(datos_mapa,zoom),crear_indicadores(datos_mapa,'total'),crear_indicadores(datos_mapa,'reple'),crear_indicadores(datos_mapa,'ini'),crear_porcentaje(datos_mapa,'rep'),crear_porcentaje(datos_mapa,'ini')
