import pandas as pd
from django_plotly_dash import DjangoDash
from sqlalchemy import create_engine
from dash import dcc,dash_table,html,Dash
from dash.dependencies import Input,Output,State
import dash_bootstrap_components as dbc
import plotly.express as px
import geopandas
import shapely
import textwrap
HOST = 'localhost'
NAME= 'elecciones23'
PASS='4rcg1s2024'
conn = create_engine("postgresql+psycopg2://elecciones23:"+PASS+"@"+HOST+":5432/"+NAME)
sql="""
select 
tipo, nivel,nivel1,fecha, detalle, subsanada, medidas_adoptadas, distrito,
ubicacion as geom
from novedades_local order by fecha asc
"""
sql_generales="""
select 
tipo, 
nivel AS nivel1,
        CASE
            WHEN nivel::text = '1'::text THEN 'Media'::text
            WHEN nivel::text = '2'::text THEN 'Alta'::text
            WHEN nivel::text = '3'::text THEN 'Critica'::text
            ELSE NULL::text
        END AS nivel,
to_char(fecha, 'dd/mm/YYYY HH:MI'::text) AS fecha, detalle, subsanada, medidas_adoptadas, distrito,
ubicacion as geom
from novedades_generales order by fecha asc
"""
df=geopandas.read_postgis(sql,conn,).to_crs(4326)
df['origen'] = 'LOCAL'
df_generales=geopandas.read_postgis(sql_generales,conn,).to_crs(4326)
df_generales['origen'] = 'GENERAL'
sql2="""
select nam as distrito from distritos
"""
df_mapa=pd.concat([df, df_generales], ignore_index=True)
cont=len(df)
distritos_df=pd.read_sql(sql2, conn)
df['lon'] = df['geom'].x
df['lat'] = df['geom'].y

def generar_tabla(df1,id):
   
    df1 = df1.drop(columns=['geom', ])

    data_table = dash_table.DataTable(df1.to_dict('records'),
                                        [{"name": i, "id": i.lower()} for i in
                                        ['Fecha', 'Tipo', 'Detalle', ]],
                                        id=id,
                                        editable=False,
                                        filter_action="native",
                                        sort_action="native",
                                        sort_mode="multi",
                                        selected_columns=[],
                                        selected_rows=[],
                                        style_table={'overflowX': 'scroll',  },
                                        style_cell={'fontSize':11, 'font-family':'sans-serif', 'textAlign': 'center', 'whiteSpace': 'normal','overflow': 'hidden',
                                        'textOverflow': 'ellipsis',},
                                        page_action="native",
                                        page_current=0,
                                        
                                        page_size=8,
                                        
                                        style_data={
                                            'color': 'black',
                                            'backgroundColor': 'white',
                                            

                                        },
                                        style_data_conditional=[
                                            {
                                                "if": {"state": "active"},  # 'active' | 'selected'
                                                "backgroundColor": "rgb(102, 102, 102)",
                                                "border": "3px solid white",
                                                "color": "white",
                                            },
                                            {
                                                'if': {
                                                    'state': 'selected'  # 'active' | 'selected'
                                                },
                                                'backgroundColor': 'rgba(0, 116, 217, 0.3)'
                                            },
                                        ],
                                        style_header={
                                            'backgroundColor': 'rgb(210, 210, 210)',
                                            'color': 'black',
                                            'fontWeight': 'bold'
                                        }

                                        )
    return data_table

sql_malvinas="""
 SELECT nam,geom, -51.74153477642776 as lat,59.38576589695881 as lon FROM public.malvinas
"""
gdf_poligono = geopandas.read_postgis(sql_malvinas, conn, geom_col='geom')
gdf_poligono.to_crs(epsg=4326, inplace=True)
#gdf_poligono.simplify(tolerance=1000, preserve_topology=True)
poligono_geojson = gdf_poligono.__geo_interface__
def crear_mapa(df, zoom, lat_cen=None, lon_cen=None):
    px.set_mapbox_access_token('pk.eyJ1IjoiemFsaXRvYXIiLCJhIjoiYVJFNTlfbyJ9.mPX8qTsRUGOOETl0CtA-Pg')
    punto = shapely.Point(-59.5236, -51.7963)  # Longitud, Latitud (centro del círculo)
    gdf_circulo = geopandas.GeoDataFrame(geometry=[punto], crs="EPSG:4326")
    # Proyectar a UTM para un buffer preciso en metros
    gdf_circulo = gdf_circulo.to_crs("EPSG:32721")  # UTM zona 21S (ajusta según la ubicación)
    gdf_circulo['geometry'] = gdf_circulo.geometry.buffer(280000)  # Buffer de 10 km
    gdf_circulo = gdf_circulo.to_crs("EPSG:4326")  # Volver a WGS84 para Mapbox
    if lat_cen and lon_cen:
        center = dict(lat=lat_cen, lon=lon_cen)
    else:
        center = dict()
    df['lon'] = df['geom'].x
    df['lat'] = df['geom'].y
    if lat_cen and lon_cen:
        center = dict(lat=lat_cen, lon=lon_cen)
    else:
        center = dict(lat=-34.603722,lon=-58.381592)  # Default center (Buenos Aires)
    df['detalle2'] = ['<br>'.join(textwrap.wrap(x, width=50)) for x in df['detalle']]   
    df['medidas2'] = ['<br>'.join(textwrap.wrap(x, width=50)) for x in df['medidas_adoptadas']]  
    mapa = px.scatter_mapbox(data_frame=df, lat="lat", lon="lon",
                             hover_name="nivel",
                             color='nivel',
                             category_orders={'gender': ['Media', 'Alta', 'Critica']},
                        color_discrete_sequence=["#656d1c", "#8b5f26","#830b0b" ],
                           
                             hover_data=dict(distrito=True,
                                             tipo=True,
                                             fecha=True,
                                             detalle2=True,
                                             subsanada=True,
                                             medidas2=True,
                                             origen=True,
                                             lat=False,
                                             lon=False,
                                             ),
                              zoom=zoom, height=800, center=center,
                              
                             )
    mapa.update_traces(

        marker={'size': 13},
        hovertemplate="<br>".join(["<b>Fecha:</b> %{customdata[2]}",
                                                  "<b>Distrito:</b> %{customdata[0]}",
                                                  "<b>Origen:</b> %{customdata[6]}",
                                                  "<b>Tipo:</b> %{customdata[1]}",
                                                  "<b>Fecha:</b> %{customdata[2]}",
                                                  "<b>Detalle:</b> %{customdata[3]}",
                                                  "<b>Subsanada:</b> %{customdata[4]}",
                                                  "<b>Medidas Adoptadas:</b> %{customdata[5]}",
                                                  

                                                  ]), )
    mapa.update_layout(hoverlabel_bgcolor="#FFFFFF",coloraxis_showscale=False,

                       mapbox_style="open-street-map", margin={"r": 0, "t": 0, "l": 0, "b": 0}
                       )
    mapa.update_geos(fitbounds='locations')
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

def graf_nov_loc(df):
    # Contar la cantidad de mesas por estado
    estado_counts = df['nivel'].value_counts()

    # Crear un DataFrame para el gráfico de torta
    df_pie = pd.DataFrame({
        'Nivel': estado_counts.index,
        'Cantidad': estado_counts.values
    })

    # Crear el gráfico de torta con Plotly Express
    fig = px.pie(df_pie, values='Cantidad', names='Nivel', title='Novedades en locales',hole=.4,
                 )

    # Personalizar el gráfico
    fig.update_traces(textposition='inside', textinfo='percent+label',marker=dict(
            colors=["#b5c717", "#FF1E00", "#FF9900"]))

    fig.update_layout( plot_bgcolor='rgb(40, 40, 40)', title_x=0.5,autosize=True, height=400,
                               paper_bgcolor='rgb(40, 40, 40)', title_font_size=25, font_color='rgb(255, 255, 255)',showlegend=True,font_size=10
                               ,legend=dict(orientation="h", ))
    # Mostrar el gráfico
    
    return fig


def get_points_center_and_zoom(df,):
    #
    # Calcular centroide (promedio de lat y lon)
    lat_cen = df['lat'].mean()
    lon_cen = df['lon'].mean()

    # Calcular extensión para determinar zoom
    if len(df) > 1:
        max_diff = max(df['lat'].max() - df['lat'].min(), df['lon'].max() - df['lon'].min())
        if max_diff > 5:
            zoom = 3  # Áreas grandes
        elif max_diff > 2:
            zoom = 8  # Áreas medianas
        elif max_diff > 0.5:
            zoom = 10  # Áreas pequeñas
        else:
            zoom = 11  # Áreas muy pequeñas o puntos cercanos
    else:
        zoom = 12  # Zoom fijo para un solo punto

    return zoom,lat_cen, lon_cen, 

app2 = DjangoDash(name='novedades',  external_stylesheets=[dbc.themes.DARKLY])
todos = [{"label": 'TODOS', "value": 'TODOS'}]
app2.layout = html.Div(
        [dbc.Alert(
            "Hay Novedades Nuevas!!",
            id="alerta",
            is_open=False,
            color="danger",
            duration=4000,
        ),
            html.Audio(id='audio', autoPlay=True, src='/elecciones/static/notificacion.mp3'),
            
            dbc.Row([html.H2('NOVEDADES', style={'textAlign': 'center', 'background-color': '#267300'})],
                    className="g-0"),
            dbc.Row([dbc.Col([dbc.Select(id="selec_distrito", options=todos + [{"label": x, "value": x} for x in distritos_df[
            'distrito'].drop_duplicates().sort_values()], placeholder='DISTRITO')]),
            dbc.Col([dbc.Select(id="Subsanada", options=[{"label": 'No', "value": 'No'} ,{"label": 'Si', "value": 'Si'}], placeholder='SUBSANADO')])
            
            ],className="m-2 g-0"),        

            dbc.Row([dbc.Col([dbc.Row(html.H3('NOVEDADES DE  LOCAL', style={'textAlign': 'center', 'background-color': '#267300'})),
                dbc.Row(dcc.Loading(id="ls-loading-3", children=[generar_tabla(df,'datatable1')])), 
                dbc.Row(html.H3('NOVEDADES GENERALES', style={'textAlign': 'center', 'background-color': '#267300'})),
                dbc.Row(dcc.Loading(id="ls-loading-1", children=[generar_tabla(df_generales,'datatable2')])),
                              
                              ],md=5),
                 dbc.Col([dbc.Row(dcc.Loading(id="ls-loading-4", children=[dcc.Graph(id='mapa', figure=crear_mapa(df_mapa, 3))]))],md=4),
                  dbc.Col([dbc.Row(dcc.Loading(id="ls-loading-5", children=[dcc.Graph(id='pie_3', figure=graf_nov_loc(df))])),
                           dbc.Row(dcc.Loading(id="ls-loading-", children=[dcc.Graph(id='pie4', figure=graf_nov_loc(df_generales))]))],md=3)            
                              ],className="g-0"),

            dcc.Interval(
                id='interval-component',
                interval=60 * 1000,  # in milliseconds
                n_intervals=0
            )

        ]
    )

@app2.callback(
    Output('datatable1', 'data'),
    Output('datatable2', 'data'),
    Output('mapa', 'figure'),
    Output('pie_3', 'figure'),
    Output('pie4', 'figure'),
    [
        Input('interval-component', 'n_intervals'),
        Input('selec_distrito', 'value'),
        Input('datatable1', 'active_cell'),
        Input('datatable2', 'active_cell'),
        Input('datatable1', 'derived_virtual_data'),
        Input('datatable2', 'derived_virtual_data'),
    ],
    [
        State('datatable1', 'data'),
        State('datatable2', 'data'),
    ],
    prevent_initial_call=True
)
def actualizar_tabla(intervalo, distrito, active_cell1, active_cell2, derived_data1, derived_data2, data1, data2, **kwargs):
    from dash import ctx
    df=geopandas.read_postgis(sql,conn,).to_crs(4326)
    df['origen'] = 'LOCAL'
    df_generales=geopandas.read_postgis(sql_generales,conn,).to_crs(4326)
    df_generales['origen'] = 'GENERAL'
    df['lon'] = df['geom'].x
    df['lat'] = df['geom'].y
    df_generales['lon'] = df_generales['geom'].x
    df_generales['lat'] = df_generales['geom'].y
    if distrito and distrito != 'TODOS':
        df = df[df['distrito'] == distrito]
        df_generales = df_generales[df_generales['distrito'] == distrito]
    df1 = df.drop(columns=['geom', ])
    df1_generales = df_generales.drop(columns=['geom', ])
    df_mapa=pd.concat([df, df_generales], ignore_index=True)
    lat_cen = None
    lon_cen = None
    zoom = 3
    zoom, lat_cen, lon_cen = get_points_center_and_zoom(df_mapa)
    if active_cell1 and derived_data1:
        row = active_cell1['row']
        lat_cen = derived_data1[row].get('lat')
        lon_cen = derived_data1[row].get('lon')
        zoom = 18
    
    # Manejar clic en datatable2
    elif active_cell2 and derived_data2:
        row = active_cell2['row']
        lat_cen = derived_data2[row].get('lat')
        lon_cen = derived_data2[row].get('lon')
        zoom = 18

    return (
        df1.to_dict('records'),
        df1_generales.to_dict('records'),
        crear_mapa(df_mapa, zoom, lat_cen, lon_cen),  # Usar la función crear_mapa ya modificada
        graf_nov_loc(df),
        graf_nov_loc(df_generales)
    )