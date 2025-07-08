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
sql='select distrito, estado_local from cantidad_votos_local'
df_local= pd.read_sql(sql, conn)
cantidad_locales=df_local.shape[0]


sql_veh = """SELECT distrito, count(id) as cantidad, 
sum(case when tipo_veh='CONTRATADO' then 1 else 0 end) as contratados,
 sum(case when tipo_veh='PROPIO' then 1 else 0 end) as propios

 FROM vehiculos23 group by distrito
"""
df_veh= pd.read_sql(sql_veh, conn)
vehiculos=df_veh.sum(axis=0)['cantidad']
sql_votos="""select distrito, avg(votos) as votos ,
sum(case when votos>0 then 1 else 0 end) as locales_votos,
sum(case when estado_local='FINALIZADO' then 1 else 0 end) as finalizados, 
sum(case when estado_local='HABILITADO' then 1 else 0 end) as habilitados,
sum(case when estado_local='NO INICIADO' then 1 else 0 end) as no_iniciados,
sum(case when estado_local='DESHABILITADO' then 1 else 0 end) as deshabilitados,
sum(case when estado_local='INICIADO' then 1 else 0 end) as iniciados,
sum(case when estado_local='NO FINALIZADO' then 1 else 0 end) as no_finalizados


from cantidad_votos_local where validado=1 group by distrito """
df_votos=pd.read_sql(sql_votos, conn)
locales_votos=df_votos.sum(axis=0)['locales_votos']
votos=df_votos['votos'].mean()
sql_personas='select distrito,total_general,total_ea,total_ara,total_faa,total_gna,total_pfa,total_pna,total_psa,total_fuerzas_provinciales  from sabanas_de_personal'
df_personas=pd.read_sql(sql_personas, conn)
sql_novedades='SELECT distrito, tipo FROM public.novedades_local'
df_novedades=pd.read_sql(sql_novedades, conn)
total_personas=int(df_personas.sum(axis=0)['total_general'])
sql_mesas='SELECT distrito, estado FROM mesas_estados'
df_mesas=pd.read_sql(sql_mesas, conn)
def grafico_novedades(df_novedades):
    
    df_counts = df_novedades['tipo'].value_counts().reset_index()
    df_counts.columns = ['tipo', 'conteo']

    # Crear gráfico circular con Plotly Express
    fig = px.pie(df_counts, 
                 hole=.4,
                 values='conteo', 
                 names='tipo', 
                 title='',
                 color_discrete_sequence=px.colors.qualitative.Plotly)

    # Personalizar el diseño
      # Separar un poco la primera categoría
    fig.update_layout(showlegend=True, 
                      title_font_size=20,
                      margin=dict(t=50, b=20, l=20, r=20))
    fig.update_layout( plot_bgcolor='rgb(40, 40, 40)', title_x=0.5,autosize=True, height=350,
                               paper_bgcolor='rgb(40, 40, 40)', title_font_size=25, font_color='rgb(255, 255, 255)',showlegend=True,font_size=9
                               ,legend=dict(   orientation="h", entrywidth=70, yanchor="bottom", y=1.02,  xanchor="right", x=1))
    # Mostrar el gráfico
    return fig

# Crear DataFrame
def graf_estados(df_mesas):
    # Contar la cantidad de mesas por estado
    estado_counts = df_mesas['estado'].value_counts()

    # Crear un DataFrame para el gráfico de torta
    df_pie = pd.DataFrame({
        'Estado': estado_counts.index,
        'Cantidad': estado_counts.values
    })

    # Crear el gráfico de torta con Plotly Express
    fig = px.pie(df_pie, values='Cantidad', names='Estado', title='Distribución de Mesas por Estado',hole=.4,)

    # Personalizar el gráfico
    #fig.update_traces(textposition='inside', textinfo='percent+label')

    fig.update_layout( plot_bgcolor='rgb(40, 40, 40)', title_x=0.5,autosize=True, height=350,
                               paper_bgcolor='rgb(40, 40, 40)', title_font_size=25, font_color='rgb(255, 255, 255)',showlegend=True,font_size=10
                               ,legend=dict(orientation="h", ))
    # Mostrar el gráfico
    return fig
# Contar la cantidad de mesas por estado

def crear_estado_local(df):
   
    estado_counts = df['estado_local'].value_counts()

# Crear un DataFrame para el gráfico de torta
    df_pie = pd.DataFrame({
        'Estado': estado_counts.index,
        'Cantidad': estado_counts.values
    })

    # Crear el gráfico de torta con Plotly Express
    fig = px.pie(df_pie, values='Cantidad', names='Estado', title='',hole=.4,)

    # Personalizar el gráfico

    fig.update_layout( plot_bgcolor='rgb(40, 40, 40)', title_x=0.5,autosize=True, height=350,
                           paper_bgcolor='rgb(40, 40, 40)', title_font_size=25, font_color='rgb(255, 255, 255)',showlegend=True,legend=dict(orientation="h", ))
    
    return fig

def crear_graf_personal(df):
   
    df = df.rename(columns={
    'total_ea': 'EA',
    'total_ara': 'ARA',
    'total_faa': 'FAA',
    'total_gna': 'GNA',
    'total_pfa': 'PFA',
    'total_pna': 'PNA',
    'total_psa': 'PSA',
    'total_fuerzas_provinciales': 'FPP'
})

# Sumar los valores de cada tipo de personal (excluyendo 'distrito' y 'total_general' si existe)
    totals = df[['EA', 'ARA', 'FAA', 'GNA', 'PFA', 'PNA', 'PSA', 'FPP']].sum()
            

# Crear un DataFrame para el gráfico circular
    df_pie = pd.DataFrame({
    'Tipo': totals.index,
    'Cantidad': totals.values
})

# Crear el gráfico circular con Plotly Express
    fig = px.pie(df_pie, values='Cantidad', names='Tipo', title='', hole=.4,)

# Personalizar el gráfico (opcional)
    fig.update_layout(showlegend=True, 
                      title_font_size=20,
                      margin=dict(t=50, b=50, l=50, r=50))
    fig.update_layout( plot_bgcolor='rgb(40, 40, 40)', title_x=0.5,autosize=True, height=350,
                               paper_bgcolor='rgb(40, 40, 40)', title_font_size=25, font_color='rgb(255, 255, 255)',showlegend=True,font_size=10
                               ,legend=dict(orientation="h", ))
    return fig

def crear_graf_vehiculos(df):
   
    campos = ['propios','contratados']
    labels=[x for x in campos if df.sum(axis=0)[x] >0 ]
    values = [df.sum(axis=0)[a] for a in labels]
    # colors = ['rgb(255, 153, 51)', 'rgb(0, 179, 0)']
    fig_estado = go.Figure([go.Pie(labels=labels, values=values, hole=.5,)])
    fig_estado.update_layout( plot_bgcolor='rgb(40, 40, 40)', title_x=0.5,autosize=True, height=350,
                           paper_bgcolor='rgb(40, 40, 40)', title_font_size=25, font_color='rgb(255, 255, 255)',showlegend=True,legend=dict(orientation="h", ))
   
    return fig_estado



def crear_votos(data):
    fig = go.Figure(
        go.Indicator(
            mode='gauge+number',
            value=data,
            number={"font": {"size": 30,"color":'white'},'suffix': "%"},
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

    fig.update_layout(height=350,title_text='PORCENTAJE DE VOTOS',autosize=True, 
        font={'color': "white", 'family': "Arial",'size':20},grid={'rows': 1, 'columns': 1, 'pattern': "independent"}, title_x=0.5,
        
        plot_bgcolor='rgb(40, 40, 40)',
    
        paper_bgcolor='rgb(40, 40, 40)',
    )
    return fig
todos = [{"label": 'TODOS', "value": 'TODOS'}]
app = DjangoDash(name='ResumenGeneral', external_stylesheets=[dbc.themes.DARKLY])
app.layout = html.Div(
    [
        dbc.Row([html.H1('RESUMEN GENERAL', style={'textAlign': 'center', 'background-color': '#267300'})],
                className="g-0"),

        dbc.Row([dbc.Col([dbc.Select(id="selec_distrito", options=todos + [{"label": x, "value": x} for x in df_local[
            'distrito'].drop_duplicates().sort_values()], placeholder='DISTRITO')])], style={'marginBottom' : '5px',}),
        dbc.Row([
           dbc.Col([ html.H2(id='locales_cant',children= 'LOCALES: '  + str(cantidad_locales), style={'textAlign': 'center', 'background-color': '#0066cc'})],md=4),
            
        dbc.Col([html.H2(id='cant_pers', children='PERSONAL:  '  + str(total_personas), style={'textAlign': 'center', 'background-color': '#0066cc'}) ],md=4),

        dbc.Col([ html.H2(id='cant_veh', children='VEHÍCULOS: '  + str(vehiculos), style={'textAlign': 'center', 'background-color': '#0066cc'}) ],md=4),


        ],className="g-0"), 
        dbc.Row([dbc.Col([  dcc.Loading(id="ls-loading-12", children=[dcc.Graph(id='graf_local', figure=crear_estado_local(df_local))], type="default")  ],md=4),
            
        dbc.Col([ dcc.Loading(id="ls-loading-14", children=[dcc.Graph(id='pie_personas', figure=crear_graf_personal(df_personas))], type="default")    ],md=4),

        dbc.Col([  dcc.Loading(id="ls-loading-15", children=[dcc.Graph(id='pie_vehiculos', figure=crear_graf_vehiculos(df_veh))], type="default")    ],md=4),
]) ,

 dbc.Row([
           dbc.Col([ html.H2(id='cant_votos',children='INFORMARON VOTOS: '  + str(locales_votos), style={'textAlign': 'center', 'background-color': '#0066cc'})],md=4),
            
        dbc.Col([html.H2(id='cant_nov',children='NOVEDADES EN LOCAL: '  + str( df_novedades.shape[0]), style={'textAlign': 'center', 'background-color': '#0066cc'}) ],md=4),

        dbc.Col([ html.H2(id='cant_mesas',children='MESAS: '  + str(df_mesas.shape[0]), style={'textAlign': 'center', 'background-color': '#0066cc'}) ],md=4),


        ],className="g-0"), 

         dbc.Row([dbc.Col([  dcc.Loading(id="ls-loading-11", children=[dcc.Graph(id='graf_votos', figure=crear_votos(votos))], type="default")  ],md=4),
                  
            
        dbc.Col([   dcc.Loading(id="ls-loading-13", children=[dcc.Graph(id='pie_3', figure=grafico_novedades(df_novedades))], type="default")    ],md=4),

        dbc.Col([  dcc.Loading(id="ls-loading-17", children=[dcc.Graph(id='pie_7', figure=graf_estados(df_mesas))], type="default")      ],md=4),
]) ,
dcc.Interval(
                id='interval-component',
                interval=60 * 2000,  # in milliseconds
                n_intervals=0
            ),


    ]
)

@app.callback(
    [Output('locales_cant', 'children'), Output('cant_pers', 'children'),
    Output('cant_veh', 'children'), Output('cant_votos', 'children'), Output('cant_nov', 'children'),
    Output('cant_mesas', 'children'), Output('graf_local', 'figure'), Output('pie_personas', 'figure'),
    Output('pie_vehiculos', 'figure'), Output('graf_votos', 'figure'), Output('pie_3', 'figure'),
    Output('pie_7', 'figure'), ],
   
    [Input('selec_distrito', 'value')],
    prevent_initial_call=True
)
def actualizar(distrito, **kwargs):
    df_veh= pd.read_sql(sql_veh, conn)
    df_votos=pd.read_sql(sql_votos, conn)
    df_personas=pd.read_sql(sql_personas, conn)
    df_mesas=pd.read_sql(sql_mesas, conn)
    df_novedades=pd.read_sql(sql_novedades, conn)
    df_local= pd.read_sql(sql, conn)
     
    if distrito and distrito != 'TODOS':
        df_local = df_local[df_local['distrito'] == distrito]     
        df_veh = df_veh[df_veh['distrito'] == distrito]
        df_votos = df_votos[df_votos['distrito'] == distrito]
        df_personas = df_personas[df_personas['distrito'] == distrito]
        df_mesas = df_mesas[df_mesas['distrito'] == distrito]
        df_novedades = df_novedades[df_novedades['distrito'] == distrito]
    cantidad_locales=df_local.shape[0]
    total_personas=int(df_personas.sum(axis=0)['total_general'])
    votos=df_votos['votos'].mean()
    locales_votos=df_votos.sum(axis=0)['locales_votos']
    total_mesas=int(df_mesas.shape[0])
    total_novedades=int(df_novedades.shape[0])
    fig_estado = crear_estado_local(df_local)
    personal=crear_graf_personal(df_personas)
    vehiculos=crear_graf_vehiculos(df_veh)
    vehiculos_cant=df_veh.sum(axis=0)['cantidad']
    fig_votos= crear_votos(votos)
    fig_novedades=grafico_novedades(df_novedades)
    fig_mesas=graf_estados(df_mesas)
    
    return 'LOCALES: '+ str(cantidad_locales), 'PERSONAL:  ' + str(total_personas), 'VEHÍCULOS: ' + str(vehiculos_cant), 'INFORMARON VOTOS: ' + str(
        locales_votos), 'NOVEDADES EN LOCAL: ' + str(total_novedades), 'MESAS: ' + str(total_mesas), fig_estado, personal, vehiculos,fig_votos, fig_novedades, fig_mesas