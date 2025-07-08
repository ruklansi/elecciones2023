from django.conf import settings
import geopandas
import plotly.express as px 
from django_plotly_dash import DjangoDash
from sqlalchemy import create_engine
from dash import dcc,dash_table,html,Dash
from django.conf import settings
import pandas as pd

from dash.dependencies import Input,Output,State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

HOST = 'localhost'
NAME= 'elecciones23'
PASS='4rcg1s2024'
conn = create_engine("postgresql+psycopg2://elecciones23:"+PASS+"@"+HOST+":5432/"+NAME)

sql='select * from locales_validados'
df=geopandas.read_postgis(sql,conn,geom_col='ubicacion').to_crs(4326)
df['lon'] = df['ubicacion'].x
df['lat'] = df['ubicacion'].y


def crear_mapa(datos_mapa, zoom, lat_cen=None, lon_cen=None):
    if lat_cen and lon_cen:
        center = dict(lat=lat_cen, lon=lon_cen)
    else:
        center = dict()
    mapa = px.scatter_mapbox(data_frame=datos_mapa, lat="lat", lon="lon",
                             hover_name="nombre",
                             color='recepciono_mat_elec',
                             color_continuous_scale=[[0, 'red'], [0.5, 'orange'], [1.0, 'green']],
                             range_color=[0, 1],
                           
                             hover_data=dict(distrito=True,
                                             subdistrito=True,
                                             nombre=True,
                                             seccion=True,
                                             circuito=True,
                                             direccion=True,
                                             grado_jefe_local=True,
                                             nombre_jefe_local=True,
                                             apellido_jefe_local=True,
                                             telefono_jefe_local=True,
                                             castidad_auxiliares=True,
                                             cant_efectivos=True,
                                             lat=False,
                                             lon=False,
                                             ),
                              zoom=zoom, height=700, center=center,
                              
                             )
    mapa.update_traces(

        marker={'size': 13},
        hovertemplate="<br>".join(["<b>Nombre:</b> %{customdata[2]}",
                                                  "<b>Distrito:</b> %{customdata[0]}",
                                                  "<b>Subdistrito:</b> %{customdata[1]}",
                                                  "<b>Sección:</b> %{customdata[3]}",
                                                  "<b>Circuito:</b> %{customdata[4]}",
                                                  "<b>Dirección:</b> %{customdata[5]}",
                                                  "<b>J loc:</b> %{customdata[6]} %{customdata[8]} %{customdata[7]}",
                                                  "<b>Tel J Loc:</b> %{customdata[9]}",
                                                  "<b>Auxiliares:</b> %{customdata[10]}",
                                                  "<b>Seg Ext:</b> %{customdata[11]}",

                                                  ]), )
    mapa.update_layout(hoverlabel_bgcolor='#ffffff',coloraxis_showscale=False,

                       mapbox_style="open-street-map", margin={"r": 0, "t": 0, "l": 0, "b": 0}
                       )
    mapa.update_geos(fitbounds='locations')
    return mapa


df1 = df.drop(columns=['ubicacion', ])
data_table = dash_table.DataTable(df1.to_dict('records'),
                                  [{"name": i, "id": i.lower()} for i in ['Nombre',]],
                                  id='datatable',
                                  editable=False,
                                  filter_action="native",
                                  sort_action="native",
                                  sort_mode="multi",
                                  selected_columns=[],
                                  selected_rows=[],

                                  page_action="native",
                                  page_current=0,
                                  page_size=10,
                                  style_cell={'textAlign': 'center'},
                                  style_data={
                                      'color': 'black',
                                      'backgroundColor': 'white'

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
df1 = df.drop(columns=['ubicacion', ])
datos_tabla = df1.to_dict('records')
datos_mapa = df
option_sub = [{}]
zoom = 3

todos = [{"label": 'TODOS', "value": 'TODOS'}]

def crear_votos(data):
    locales=data.shape[0]
    recibio=data[data['recepciono_mat_elec']==1].shape[0]
    fig = go.Figure(
        go.Indicator(
             mode='gauge+number',
            value= (recibio *100)/ locales,
            number={"font": {"size": 30,"color":'white'},'suffix': "%",'valueformat': '.2f'},
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

    fig.update_layout(height=300,title_text='PORCENTAJE DE VOTOS',autosize=True, 
        font={'color': "white", 'family': "Arial",'size':20},grid={'rows': 1, 'columns': 1, 'pattern': "independent"}, title_x=0.5,
        
        plot_bgcolor='rgb(40, 40, 40)',
    
        paper_bgcolor='rgb(40, 40, 0)',
    )
    return fig

def crear_indicadores(df_data,tipo):
    data = df_data.drop(columns=['ubicacion', ])
    
    
    if tipo=='locales':
        valor=data.shape[0]
        titulo='LOCALES'   
        color='rgb(255, 194, 102)'
    
    if tipo=='recibio':
        valor=data[data['recepciono_mat_elec']==1].shape[0]
        titulo='REC MAT ELEC' 
        color='rgb(0, 230, 0)' 
   
    if tipo=='no_recibio':
        valor=data[data['recepciono_mat_elec']==0].shape[0]
        titulo='NO REC MAT ELEC' 
        color='rgb(255, 71, 26)'   
    
           
    graf_total = go.Figure()
    graf_total.add_trace(go.Indicator(
        mode="number",
        number={"font": {"size":60}, 'valueformat': ',.0f', },
        value=valor,
        domain={'x': [0, 1], 'y': [0, 1]}))

    graf_total.update_layout(autosize=True, height=250, title_text=titulo, plot_bgcolor='rgb(40, 40, 40)',
                             paper_bgcolor='rgb(40, 40, 40)',
                             grid={'rows': 1, 'columns': 1, 'pattern': "independent"}, title_x=0.5, font=dict(
            size=18, color=color

        ))
  
    return graf_total
#app = Dash( external_stylesheets=[dbc.themes.DARKLY])
app = DjangoDash(name='recepcionMatElec',  external_stylesheets=[dbc.themes.DARKLY])
app.layout = html.Div(
    [
        dbc.Row([html.H1('RECEPCIÓN DE MATERIAL ELECTORAL', style={'textAlign': 'center', 'background-color': '#267300'})],
                className="g-0"),

        dbc.Row([dbc.Col([dbc.Select(id="selec_distrito", options=todos + [{"label": x, "value": x} for x in df[
            'distrito'].drop_duplicates().sort_values()], placeholder='DISTRITO')]),
                 dbc.Col([dbc.Select(id="selec_subdistrito", placeholder='SUBDISTRITO')]),
                 dbc.Col([dbc.Select(id="selec_seccion", placeholder='SECCION')]),
                 dbc.Col([dbc.Select(id="selec_circuito", placeholder='CIRCUITO')])

                 ], style={'marginBottom' : '5px',}),

        dbc.Row([dbc.Col([dbc.Select(id="estado", options=todos + [{"label": 'RECIBIO MATERIAL ELECTORAL', "value": '1'} ,{"label": 'NO RECIBIO MATATERIAL ELECTORAL', "value": '0'}], placeholder='ESTADO')]),

                 ], style={'marginBottom' : '5px',}),
dbc.Row([dbc.Col([
    dbc.Row([dcc.Loading(id="ls-loading-10", children=[data_table], type="default")]),
    dbc.Row([dcc.Loading(id="ls-loading-11", children=[dcc.Graph(id='graf_votos', figure=crear_votos(df))], type="default")])
    
    ],md=4),
        
        
        dbc.Col([

            dbc.Row(dcc.Loading(id="ls-loading-0", children=[dcc.Graph(id='mapa', figure=crear_mapa(datos_mapa, zoom))], type="default")),
            
        ],md=6),

        dbc.Col([dbc.Row([dcc.Loading(id="ls-loading-1", children=[dcc.Graph(id='graf_locales', figure=crear_indicadores(df,'locales'))],type="default")]),
                dbc.Row([dcc.Loading(id="ls-loading-3", children=[dcc.Graph(id='graf_recibio', figure=crear_indicadores(df,'recibio'))],type="default")]),
                dbc.Row([dcc.Loading(id="ls-loading-4", children=[dcc.Graph(id='no_recibio', figure=crear_indicadores(df,'no_recibio'))],type="default")]),
                
        ],md=2),
]) ,
dcc.Interval(
                id='interval-component',
                interval=60 * 2000,  # in milliseconds
                n_intervals=0
            ),
           
 dcc.Interval(
                id='interval-component1',
                interval=60 * 2000,  # in milliseconds
                n_intervals=0
            )

    ]
)

@app.callback(
    Output('mapa', 'figure', ), Output('selec_subdistrito', 'options'),
    [Input('selec_distrito', 'value'), Input('selec_subdistrito', 'value'),
     Input('selec_seccion', 'value'),
     Input('selec_circuito', 'value'), Input('datatable', 'active_cell'), Input('datatable', "derived_virtual_data"),Input('interval-component', 'n_intervals'),Input('estado', 'value')], [State('datatable', 'data')],
    prevent_initial_call=True
)
def actualizar_mapa(distrito, subdistrito, seccion, circuito, data, nueva_tabla,intervalo,estado,tabla,**kwargs):
    lat_cen=0
    lon_cen=0 
    df=geopandas.read_postgis(sql,conn,geom_col='ubicacion').to_crs(4326)
    df['lon'] = df['ubicacion'].x
    df['lat'] = df['ubicacion'].y
    datos_mapa = df
    option_sub = [{"label": 'TODOS', "value": 'TODOS'}]
    zoom = 3
    if distrito and distrito != 'TODOS':
        datos_mapa = df[df['distrito'] == distrito]
        option_sub = todos + [{"label": x, "value": x} for x in
                              datos_mapa['subdistrito'].drop_duplicates().sort_values()]
        zoom = 5
    if subdistrito and subdistrito != '' and subdistrito != 'TODOS':
        datos_mapa = datos_mapa[datos_mapa['subdistrito'] == subdistrito]
        zoom = 7
    if seccion and seccion != 'TODOS':
        datos_mapa = datos_mapa[datos_mapa['seccion'] == seccion]
        zoom = 9
    if circuito and circuito != 'TODOS':
        datos_mapa = datos_mapa[datos_mapa['circuito'] == circuito]
        zoom = 12
    if estado and estado!='TODOS' :
        datos_mapa = datos_mapa[datos_mapa['recepciono_mat_elec'] == int(estado)]
        
    if nueva_tabla:
        a=[x['id'] for x in nueva_tabla]    
        datos_mapa=datos_mapa[datos_mapa['id'].isin(a)]
    if data:
       
        if nueva_tabla:
            tabla=nueva_tabla
        lat_cen = tabla[data['row']]['lat']
        lon_cen = tabla[data['row']]['lon']
        zoom = 18
        return crear_mapa(datos_mapa, zoom, lat_cen, lon_cen), option_sub
    if len(datos_mapa.index) == 0:
       lat_cen=-38.416097
       lon_cen=-63.616672 
      
    return crear_mapa(datos_mapa, zoom,lat_cen, lon_cen), option_sub


@app.callback(
    Output('selec_seccion', 'options'),
    [Input('selec_subdistrito', 'value'), Input('selec_distrito', 'value')],State('selec_seccion', 'value'), prevent_initial_call=True
)
def actualizar_sec(subdistrito, distrito,seccion,**kwargs):
    option_sec=[{"label": 'TODOS', "value": 'TODOS'},]
    if distrito and distrito != 'TODOS':
        datos_mapa = df[df['distrito'] == distrito]
        option_sec = todos + [{"label": x, "value": x} for x in datos_mapa['seccion'].drop_duplicates().sort_values()]
    if subdistrito and subdistrito != '' and subdistrito != 'TODOS':
        datos_mapa = datos_mapa[datos_mapa['subdistrito'] == subdistrito]
        option_sec = todos + [{"label": x, "value": x} for x in datos_mapa['seccion'].drop_duplicates().sort_values()]
    return option_sec


@app.callback(
    Output('selec_circuito', 'options'),
    [Input('selec_subdistrito', 'value'), Input('selec_distrito', 'value'), Input('selec_seccion', 'value')],State('selec_circuito', 'value'),
    prevent_initial_call=True
)
def actualizar_cir(subdistrito, distrito, seccion,circuito,**kwargs):
    option_cir=[{"label": 'TODOS', "value": 'TODOS'},]
    if distrito and distrito != 'TODOS':
        datos_mapa = df[df['distrito'] == distrito]
        option_cir = todos + [{"label": x, "value": x} for x in datos_mapa['seccion'].drop_duplicates().sort_values()]
    if subdistrito and subdistrito != '' and subdistrito != 'TODOS':
        datos_mapa = datos_mapa[datos_mapa['subdistrito'] == subdistrito]
        option_cir = todos + [{"label": x, "value": x} for x in datos_mapa['seccion'].drop_duplicates().sort_values()]
    if seccion and seccion != 'TODOS':
        datos_mapa = datos_mapa[datos_mapa['seccion'] == seccion]
        option_cir = todos + [{"label": x, "value": x} for x in datos_mapa['circuito'].drop_duplicates().sort_values()]

    return option_cir


@app.callback(
    Output('datatable', 'data'), Output('datatable', "active_cell"), Output('datatable', 'selected_cells'),
    Output('graf_locales', 'figure'),
    Output('graf_recibio', 'figure'),
    Output('no_recibio', 'figure'),
    Output('graf_votos','figure'),
    [Input('selec_distrito', 'value'), Input('selec_subdistrito', 'value'), Input('selec_seccion', 'value'),
     Input('selec_circuito', 'value'),Input('interval-component1', 'n_intervals'),Input('estado', 'value')
     ], prevent_initial_call=True
)
def actualizar_tabla(distrito, subdistrito, seccion, circuito,intervalo,estado,**kwargs):
    df=geopandas.read_postgis(sql,conn,geom_col='ubicacion').to_crs(4326)
    
    datos=df 
    datos_tabla=df.drop(columns=['ubicacion', ]).to_dict('records')
    if distrito and distrito != 'TODOS':
        datos = df[df['distrito'] == distrito]
        df1 = datos.drop(columns=['ubicacion', ])
        datos_tabla = df1.to_dict('records')
       
    if subdistrito and subdistrito != 'TODOS':
        datos = datos[datos['subdistrito'] == subdistrito] 
        df1 = datos.drop(columns=['ubicacion', ])
        datos_tabla = df1.to_dict('records')
    if seccion and seccion != 'TODOS':
        datos = datos[datos['seccion'] == seccion]
        df1 = datos.drop(columns=['ubicacion', ])
        datos_tabla = df1.to_dict('records')
    if circuito and circuito != 'TODOS':
        datos = datos[datos['circuito'] == circuito]
        df1 = datos.drop(columns=['ubicacion', ])
        datos_tabla = df1.to_dict('records')
    if estado and estado!='TODOS' :
        datos = datos[datos['recepciono_mat_elec'] == int(estado)]
        df1 = datos.drop(columns=['ubicacion', ])  
        datos_tabla = df1.to_dict('records')
    return datos_tabla, None, [], crear_indicadores(datos,'locales'),crear_indicadores(datos,'recibio'),crear_indicadores(datos,'no_recibio'),crear_votos(datos)
