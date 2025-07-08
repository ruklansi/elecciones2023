import pandas as pd
from django_plotly_dash import DjangoDash
from sqlalchemy import create_engine
from dash import dcc,dash_table,html,Dash
from dash.dependencies import Input,Output,State
import dash_bootstrap_components as dbc

from django.conf import settings
HOST = settings.DATABASES['default']['HOST']
NAME= settings.DATABASES['default']['NAME']
conn = create_engine("postgresql+psycopg2://elecciones23:1%40Elec2023-*@"+HOST+":5432/"+NAME)
sql="""SET SESSION TIME ZONE 'America/Argentina/Buenos_Aires';
select
grado, concat(nombre,' ',apellido) as Persona,
novedad, to_char(fecha,'dd/mm/YYYY HH:MI') as fecha,
case when cargo <> '-' then cargo when seg_interna_local<>'-' then seg_interna_local else '-' end as cargo,
case when cge <>'-' then 'CGE' 
when distrito <>'-' then distrito
end as Dis_CGE ,
case when reserva <> '-' then reserva 
when nombre_local <> '-' then concat(subdistrito,'-',seccion,'-',circuito,'-',nombre_local) else '-'end as lugar,
nro_tel as telefono,
latitud,
longitud
from novedad_sms as n join exportarpersonal as p on p.id=n.persona_id order by fecha desc"""
#df=geopandas.read_postgis(sql,conn,geom_col='ubicacion').to_crs(4326)
app2 = DjangoDash(name='Novedades', external_stylesheets=[dbc.themes.DARKLY])
try:
    df=pd.read_sql(sql,conn)
    cont = 0


    data_table = dash_table.DataTable(df.to_dict('records'),
                                      [{"name": i, "id": i.lower()} for i in
                                       ['Grado', 'Persona', 'Novedad', 'Fecha', 'Cargo', 'Telefono']],
                                      id='datatable1',
                                      editable=False,
                                      filter_action="native",
                                      sort_action="native",
                                      sort_mode="multi",
                                      selected_columns=[],
                                      selected_rows=[],

                                      page_action="native",
                                      page_current=0,
                                      page_size=18,
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
    app2.layout = html.Div(
        [dbc.Alert(
            "Hay Novedades Nuevas!!",
            id="alerta",
            is_open=True,
            color="danger",
            duration=4000,
        ),
            html.Audio(id='audio', autoPlay=True, src='/elecciones/static/notificacion.mp3'),
            dbc.Row([html.H1('NOVEDADES', style={'textAlign': 'center', 'background-color': '#267300'})],
                    className="g-0"),

            dbc.Row([dbc.Col(data_table), ]),

            dcc.Interval(
                id='interval-component',
                interval=10 * 1000,  # in milliseconds
                n_intervals=0
            )

        ]
    )
except:
    pass

@app2.callback(
    Output('datatable1', 'data'), Output('alerta', 'is_open'),
    [Input('interval-component', 'n_intervals')],
)
def actualizar_tabla(intervalo, ):
    conn = create_engine("postgresql+psycopg2://elecciones23:1%40Elec2023-*@172.16.0.9:5432/elecciones2023")
    sql = """SET SESSION TIME ZONE 'America/Argentina/Buenos_Aires';
select 
grado,concat(nombre,' ',apellido) as Persona,
novedad, to_char(fecha,'dd/mm/YYYY HH:MI') as fecha,
case when cargo <> '-' then cargo when seg_interna_local<>'-' then seg_interna_local else '-' end as cargo,
case when cge <>'-' then 'CGE' 
when distrito <>'-' then distrito
end as Dis_CGE ,
case when reserva <> '-' then reserva 
when nombre_local <> '-' then concat(subdistrito,'-',seccion,'-',circuito,'-',nombre_local) else '-'end as lugar,
nro_tel  as telefono,
latitud,
longitud
from novedad_sms as n join exportarpersonal as p on p.id=n.persona_id order by fecha desc"""
    # df=geopandas.read_postgis(sql,conn,geom_col='ubicacion').to_crs(4326)
    df = pd.read_sql(sql, conn)
    global cont
    if cont != len(df):
        abrir = True
    else:
        abrir = False
    cont = len(df)
    return df.to_dict('records'), abrir