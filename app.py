# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from typing import List

import dash_auth
import dash_bootstrap_components as dbc
import geopandas as gpd
import pandas as pd
import numpy as np

from dash import Dash, Input, Output, dash_table, dcc, html
import plotly.express as px
from plotly import graph_objects as go
from plotly.subplots import make_subplots


# ---------------------------------------------------------
# Constantes y carga de los datasets
# ---------------------------------------------------------

# Cargar Parquets
TOP_REGIONES = pd.read_parquet(
    "./datasets/top_regiones.parquet"
)
TOP_POBLACIONES = pd.read_parquet(
    "./datasets/top_poblaciones.parquet"
)
TOP = pd.read_parquet(
    "./datasets/top_diags.parquet"
)
DIST_EDAD = pd.read_parquet(
    "./datasets/df_dist_edades.parquet"
)
LUGAR_TIEMPO = pd.read_parquet(
    "./datasets/df_anios.parquet"
)
EXTRANNAS = pd.read_parquet(
    "./datasets/df_meanstd_out.parquet"
)
# Cargar Excels
MISC = pd.read_excel(
    "./datasets/misc.xlsx",
    index_col=0
)


# User-password
VALID_USERNAME_PASSWORD_PAIRS = {"visualiza": "muertes"}

# Leer mapas
GDF = gpd.read_file("./maps/comunas.geojson")


# ---------------------------------------------------------
# Configuración del servidor.
# ---------------------------------------------------------

# aplicación y carga de tema
# Otros temas se pueden encontrar en: https://bootswatch.com/
#BS = "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"

app = Dash(
    external_stylesheets=[dbc.themes.CYBORG],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    title="Defunciones en Chile",
)

# autenticación
auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

# server para heroku (no eliminar)
server = app.server


# ---------------------------------------------------------
# Callbacks.
# ---------------------------------------------------------

@app.callback(
    Output("e1-opciones", "options"),
    Output("e1-opciones", "disabled"),
    Input("e1-eleccion", "value"),
)
def actualizar_opciones_1(eleccion: str):

    if eleccion not in OPCIONES or eleccion is None:
        return [], True

    opciones = OPCIONES[eleccion]
    return [{"label": v, "value": v} for v in opciones], False


@app.callback(
    Output("e2-opciones", "options"),
    Output("e2-opciones", "disabled"),
    Input("e2-eleccion", "value"),
)
def actualizar_opciones_2(eleccion: str):
    if eleccion not in OPCIONES or eleccion is None:
        return [], True

    opciones = OPCIONES[eleccion]
    return [{"label": v, "value": v} for v in opciones], False

# Gráficos sin funciones

# Top regiones
top_regiones = TOP_REGIONES
fig_top_regiones = go.Figure()
fig_top_regiones.add_trace(                               
        go.Bar(
        x=top_regiones['Región'],
        y=top_regiones['Conteo'],
        name="Cantidad de Muertes",             
        ),
        )                                    

fig_top_regiones.add_trace(                             
    go.Scatter(                          
    x=top_regiones['Región'],
    y=top_regiones['Normalizado'],
    name="Porcentaje respecto al ultimo Censo",
    mode='markers',  
    yaxis="y2"),                          
    )

fig_top_regiones.update_layout(
    title = 'Total de Muertes en el Registro por Regiones',
    template='plotly_white',
    yaxis=dict(                         
        title="Cantidad de Muertes",              
              ),
    yaxis2=dict(
        title="% Ult. Censo",           
        overlaying="y",
        side="right",
              )
    )

# Gráfico: Evolución de las muertes en el tiempo
fig_lugar_tiempo = px.line(LUGAR_TIEMPO, x='fecha', y='Conteo', color='lugar', title='Muertes en Chile a lo Largo de los Años')

fig_lugar_tiempo.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(step="all")
        ])
    )
)

fig_lugar_tiempo = fig_lugar_tiempo.update_layout(
        template='plotly_white',
        )

# Gráfico de 15 enfermedades mas extrañas dentro del país
df_muertes_outliers = EXTRANNAS.drop_duplicates(subset=['diag1_categoria_glosa'])
fig_extrannas_muertes_1 = px.bar(df_muertes_outliers.head(15), 
       x='diag1_categoria_glosa', y='mean_anual', color='comuna_glosa',
       color_discrete_sequence=px.colors.qualitative.Dark24)
fig_extrannas_muertes_1.add_trace(                             
    go.Scatter(                          
    x=df_muertes_outliers['diag1_categoria_glosa'].head(15),
    y=df_muertes_outliers['mean_all'].head(15),
    name="Media de muertes en Chile",
    mode='markers', 
    marker=dict(
        color=px.colors.qualitative.Dark24[23]
        )
    ),)

fig_extrannas_muertes_1 = fig_extrannas_muertes_1.update_layout(
    legend=dict(title='Comunas'),
    template='plotly_white',
    title = 'Enfermedades Extrañas en Chile',
    xaxis=dict(                         
        title="Diagnostico",              
              ),
    yaxis=dict(
        title="Cantidad de Muertes",
              )
    )
    

# Cantidad de muertes por top de enfermedades
df_muertes = TOP
fig_muertes_bar = px.bar(df_muertes, x='anio', y='conteo', 
                color='diag1_categoria_glosa', title="Cantidad de Muertes del Top 10 de las Defunciones",
                color_discrete_sequence=px.colors.qualitative.Dark24)

fig_muertes_bar = fig_muertes_bar.update_layout(
    template='plotly_white',
    legend=dict(title='Diagnosticos'),
    showlegend=True,
    xaxis=dict(                         
        title="Año de Registro",              
              ),
    yaxis=dict(
        title="Cantidad de Muertes",           
              )
    )

# Ranking plot
fig_rank_plot = px.line(df_muertes, x="anio", y="ranking", color="diag1_categoria_glosa", 
                color_discrete_sequence=px.colors.qualitative.Dark24)
for trazo in fig_rank_plot['data']:
    trazo['showlegend'] = False

plot_marks = px.scatter(df_muertes, x="anio", y="ranking", color="diag1_categoria_glosa",
                        color_discrete_sequence=px.colors.qualitative.Dark24)['data']

for i in range(len(plot_marks)):
    fig_rank_plot = fig_rank_plot.add_trace(plot_marks[i])
fig_rank_plot['layout']['yaxis']['autorange'] = "reversed"
fig_rank_plot = fig_rank_plot.update_layout(
    yaxis =dict(tickmode='linear'),
    xaxis =dict(tickmode='linear'),
    legend=dict(title='Diagnosticos'),
    template='plotly_white'
    )
fig_rank_plot = fig_rank_plot.update_traces(marker=dict(size=12,
                                line=dict(width=2,
                                color='DarkSlateGrey')),
                    selector=dict(mode='markers'))
fig_rank_plot = fig_rank_plot.update_xaxes(title="Año de Registro")
fig_rank_plot = fig_rank_plot.update_yaxes(title="TOP")
fig_rank_plot = fig_rank_plot.update_layout(
    title = "Evolución del Top de Muertes en los Años de Registro"
    )

fig_top_comunas = px.bar(TOP_POBLACIONES, x='comuna_glosa', y='count', 
                  color_discrete_sequence=px.colors.qualitative.Dark24)
fig_top_comunas.update_layout(
    title = 'Top 10 de Comunas con más Defunciones',
    template='plotly_white',
    yaxis=dict(                         
        title="Cantidad de Muertes",              
              ),
    xaxis=dict(
        title="Comunas",           
              )
    )


# Callbacks para plot

# Distribución de edades
@app.callback(
    Output("sex-age-dist-plot", "figure"),
    Input("e1-eleccion", "value"),)
def dist_age_sex_plot(sex: str):

    fig = px.bar(DIST_EDAD[DIST_EDAD['sexo'] == sex], x='edad_cantidad', y='anio',
                 color_discrete_sequence=px.colors.qualitative.Dark24)
    
    median_age = DIST_EDAD.groupby('sexo').agg({
    'edad_cantidad':'median'
    }).reset_index()
    median_age = median_age[median_age['sexo'] == sex]['edad_cantidad']

    fig.add_vline(x=int(median_age), line_width=3, line_dash="dash", line_color="red")

    fig = fig.update_layout(
        template='plotly_white',
        showlegend=False,
        title=f'Distribución de las Edades de Defunción: {sex}'
        )

    return fig

# Evolución porcentual
@app.callback(
    Output("perc-plot", "figure"),
    Input("e2-eleccion", "value"),)
def percentage_plot(place: str):
    x = LUGAR_TIEMPO[LUGAR_TIEMPO['lugar'] == place]['fecha']
    y = LUGAR_TIEMPO[LUGAR_TIEMPO['lugar'] == place]['percentage']

    y_m = LUGAR_TIEMPO[LUGAR_TIEMPO['lugar'] == place]['percentage'].mean()
    y_m = np.repeat(y_m, x.shape[0])

    mask = y >= LUGAR_TIEMPO[LUGAR_TIEMPO['lugar'] == place]['percentage'].mean()
    fig = go.Figure(go.Scatter(x=x, y=y, mode='lines'))
    fig.add_trace(go.Scatter(x=x[~mask], y=y_m[~mask], mode='lines',fill='tonexty', fillcolor='red'))

    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )

    fig = fig.update_layout(
        template='plotly_white',
        showlegend=False,
        title=f'Variación Porcentual Respecto a la Media Mensual: {place}'
        )

    return fig

# ---------------------------------------------------------
# Layout.
# ---------------------------------------------------------

app.layout = dbc.Container(
    [   
        html.H1("Defunciones en Chile", className="mt-3"),
        html.H4("Visualización de Información: CC5208", className="mt-4"),
        dcc.Markdown(
            """
            ### Cantidad de Muertes por Zona

            Se visualiza la cantidad de defunciones por regiones y comunas. El objetivo es observar donde se concentran la mayor cantidad de muertes en Chile y ver como se contrasta con la población total que presentan.

            De la figura regional es posible observar que el ordenamiento de las muertes es por densidad, a medida que mayor población poseen mayor es el número de muertes. Sin embargo, llama la atención que la cantidad de muertes respecto a la población del ultimo censo no es proporcional. Esto último llama la atención, observando a Santiago con bajo

            En segundo lugar, a través de la de las comunas podemos observar las 10 comunas que presentan mas defunciones, de ellas se puede notar que nuevamente se reordenan por densidades.
            """
        ),
        dcc.Graph(id="top-muertes-regiones", figure=fig_top_regiones),
        dcc.Graph(id="fig-top-comunas", figure=fig_top_comunas),
        dcc.Markdown(
            """
            ### Distribucion de Edades

            Para los gráficos referentes a las distribuciones de las edades de muerte en chile se observan skewness negativas para ambos sexos, por lo que la media no representa la edad a la que tienden a morir más personas.

            De las distribuciones se visualiza que la edad de defunción en los hombres se concentra en alrededor de los 78 años, mientras que para el caso de las mujeres es 88 años. Esta gran diferencia llama la atención, debido a que podría deberse a diferencias en la calidad de vida de ambos sexos y lleva a cuestionar aspectos como la edad de jubilación.
            """
        ),
        html.H2("Elección 1: Seleccione el Sexo que Desea Graficar", className="mt-1"),
        dcc.Dropdown(
                                    id="e1-eleccion",
                                    options=[
                                        {"label": str(v), "value": v}
                                        for v in list(DIST_EDAD['sexo'].unique())
                                    ],
                                    className="mb-1",
                                    placeholder="Elección 1",
                                    value="Plebiscitox",
                                ),
        dcc.Graph(id="sex-age-dist-plot"),
        dcc.Markdown(
            """
            ### Evolución Temporal de Defunciones

            Del gráfico es posible visualizar una gran diferencia entre la cantidad de muertes registradas para el lugar “otro”, respecto a los hospitales y hogares.

            Desde el inicio del registro hasta mediados del 2021 se observa un comportamiento cíclico en los diferentes lugares de defunción. El factor cíclico se pierde a partir de abril del 2020, presentando un comportamiento estocástico en comparación a los años previos, visualizándose alzas en muertes para algunos lugares.

            Llama la atención que previo a abril del 2020 las muertes se daban principalmente en hogares, cosa que posteriormente se observan alzas de muertes en los hospitales que superan a las de los hogares.
            """
        ),
        dcc.Graph(id="time-series-lugar-deaths", figure=fig_lugar_tiempo),
        dcc.Markdown(
            """
            ### Evolución Porcentual a través del Tiempo

            Son graficados los aumentos exponenciales respecto a la media de los diferentes lugares de muerte. De los gráficos es posible observar un comportamiento cíclico mas claro desde los datos.

            Tanto para “Casa habitación” como para “Hospital o Clínica” se observa un comportamiento similar, donde se tienen alzas de defunciones entre las fechas mayo y agosto, lo que podrían ser debido a el aumento de enfermedades respiratorias en estos periodos. Por otro lado, llama la atención que durante el periodo de febrero se obtenga una baja considerable de las muertes en el país, lo que podría deberse a mayores precauciones durante el periodo de vacaciones de verano. Por otro lado, a partir de abril del 2020 se observa la perdida del comportamiento cíclico y se observan alzas considerables en las muertes respecto a periodos anteriores. Esto se explica principalmente por la expansión de la pandemia Covid-19 en Chile, teniendo un peak de muertes en junio del 2020.
            
            Para el caso del lugar "Otro" se observa una tendencia similar a la ya comentada en los gráficos anteriores. Sin embargo, ocurre un fenómeno diferente a partir de noviembre del 2019 en las defunciones, observándose un aumento en el número de muertes hasta julio del 2020. Sin embargo, esto cambia abruptamente a partir de Julio del 2020 donde se comienzan a visualizar bajas considerables en las muertes respecto a otros periodos, lo que podría deberse a las mayores restricciones de salida durante la cuarentena en el país. Notar que la baja tiende a desvanecerse rápidamente en noviembre del 2021, donde las restricciones de cuarentena comienzan a ser menores.
            """
        ),
        html.H2("Elección 2: Escoger Lugar para Graficar", className="mt-2"),
        dcc.Dropdown(
                                    id="e2-eleccion",
                                    options=[
                                        {"label": str(v), "value": v}
                                        for v in list(LUGAR_TIEMPO['lugar'].unique())
                                    ],
                                    className="mb-2",
                                    placeholder="Elección 2",
                                    value="Plebiscito",
                                ),
        dcc.Graph(id="perc-plot"),
        dcc.Markdown(
            """
            ### Principales Diagnósticos de Defunción en Chile

            De la figura es posible visualizar los principales diagnósticos de muertes respecto a los años. De ella es posible notar que previo al 2020 las muertes tienen un comportamiento estático y no de mucha variación entre años, mientras que en años posteriores el covid tiene un numero considerable de muertes.
            """
        ),
        dcc.Graph(id="muertes-bar-plot", figure=fig_muertes_bar),
        dcc.Markdown(
            """
            ### Evolución de los Principales Diagnósticos de Defunción en Chile

            Como segundo ejercicio respecto a la evolución de las defunciones, se visualiza el cambio de posición de las 10 causas principales de muertes a través de los años. Del gráfico es posible visualizar varios patrones interesantes:
            - Uno de los mas destacables es que la hipertensión desde 2016 ha presentado un alza consistente, comenzando en posición 9 y llegando a la tercera posición el 2021.
            - Enfermedades pulmonares, que no son Covid-19, presentan periodos de baja en el 2020 al 2021.
            - Los tumores malignos de estomago tienen una baja consistente durante el largo del registro.
            - Los infartos agudos al miocardio y los tumores malignos pulmonares son unas de las principales causas de muertes en el país, manteniéndose en los primeros lugares durante gran parte de los periodos.
            """
        ),
        dcc.Graph(id="muertes-rank-plot", figure=fig_rank_plot),
        dcc.Markdown(
            """
            ### Diagnosticos Outliers como Causa de Muerte

            Como ultimo ejercicio se obtienen enfermedades outliers del registro de datos, para esto se considera un conteo de enfermedades anómalos si el conteo esta sobre la media más seis desviaciones estándar. Parte del resultado es expuesto en el gráfico, donde se exponen algunas de las enfermedades mas extrañas del dataset con su respectiva comuna.

            Las enfermedades expuestas presentan un numero anómalo que exponen ciertos problemas sociales presentes en las comunas. Un ejemplo de esto es Puente Alto, quien presenta los números mas altos de muertes por covid, los que pueden deberse a malas campañas de prevención de covid en la comuna; junto a esto, la comuna de Puente Alto presenta elevados números de asfixia, los que al ser comprobados corresponden a suicidios realizados durante la pandemia, esto señala el gran impacto de la pandemia en la comuna.
            """
        ),
        dcc.Graph(id="caso-outliers", figure=fig_extrannas_muertes_1),
    ],
    className="p-5",
    style={"max-width": "100%"},
)


if __name__ == "__main__":
    app.run_server(debug=True)

