import pandas as pd
import psycopg2
from plotly.offline import plot
from plotly.subplots import make_subplots
import plotly.graph_objs as go

def custom_sql(connection, sql):
    """
    This function runs SQL command using connection specified
    Input: Mysql connection and SQL command
    Output: Returned results
    """
    #Execute SQL command using input connection as cursor
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchall()
    return row