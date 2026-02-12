import polars as pl
import sys
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


sys.stdout.reconfigure(encoding='utf-8')
# Definir la ruta de la base de datos
db_path = "soccer.db"
# Crear la URI de conexión para SQLite
uri = f"sqlite://{db_path}"

# Consulta SQL
query = "SELECT name, played, wins, draws, points, goals_against, goals_for, name_league  FROM stats s INNER JOIN teams t ON team_id=id INNER JOIN league l ON league_id=id_league"

# Leer la base de datos con Polars
df = pl.read_database_uri(query=query, uri=uri)

# Vamos a hacer en primer lugar las victorias y empates por ligas, para ello nos quedamos solo con los datos que nos interesan
# que son los partidos jugados para hacer el porcentaje, las victorias, empates, y el nombre de la liga
df_ve_liga = df.drop(["name", "goals_against", "goals_for", "points"])
df_ve_liga = (
    df_ve_liga.group_by("name_league").agg([ # Agrupamos por ligas
        pl.sum("wins").alias("wins"), # Sumamos el numero de victorias totales por liga
        pl.sum("draws").alias("draws"), # El número de empates por ligas
        pl.sum("played").alias("played") # El número de partidos para hacer el porcentaje
    ])
)

# Cuando un equipo empata, empata dos equipos, por lo que se divide entre dos para quedarnos con el empate único

df_ve_liga = df_ve_liga.with_columns([
    (pl.col("draws") / 2).alias("draws")
])

df_ve_liga = df_ve_liga.with_columns([
    (pl.col("wins") / pl.col("played")).alias("win_rate"), # Calculamos el win-rate de la liga correspondiente
        (pl.col("draws") / pl.col("played")).alias("draw_rate") # Calculamos el draw-rate de la liga correspondiente
])

df_ve_liga.write_csv("Victorias_Empates_Por_Liga.csv") # Una vez calculado todo, lo escribimos en un csv

labels = df_ve_liga["name_league"].to_list() # Obtenemos los labels de las diferentes ligas para ponerlo en los gráficos
win_values = df_ve_liga["win_rate"].to_list() # Obtenemos los valores de las victorias
draw_values = df_ve_liga["draw_rate"].to_list() # Obtenemos los valores de los empates
# Creamos gráficos facetados, donde crearemos dos gráficos tipo 'donuts'
fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
fig.add_trace(go.Pie(labels=labels, values=win_values, name="Wins"), # Creamos el primer gráfico donde se muestra el porcentaje de victorias por liga
            1, 1)
fig.add_trace(go.Pie(labels=labels, values=draw_values, name="Draws"), # El segundo se muestra el porcentaje de empates por liga
            1, 2)

# Con el parámetro `hole` se crea un gráfico circular con forma de donut
fig.update_traces(hole=.4, hoverinfo="label+percent+name")

fig.update_layout(
    title_text="Comparacion Win Rate vs Draw Rate por Liga",
    # Añadimos anotaciones en el centro del donut
    annotations=[dict(text='Wins', x=sum(fig.get_subplot(1, 1).x) / 2, y=0.5,
                    font_size=20, showarrow=False, xanchor="center"),
                dict(text='Draws', x=sum(fig.get_subplot(1, 2).x) / 2, y=0.5,
                    font_size=20, showarrow=False, xanchor="center")])
fig.show()

# Ahora vamos a ver cuales son los equipos más eficientes, es decir,
# cuantos puntos por partido consigue cada equipo comparandolo con sus goles de diferencia
# habrá equipos que con poco gol de diferencia ganen más puntos que otros

df_efficient_equipos = df.drop(["wins", "draws"]) # Quitamos valores que no nos interesan como las victorias y los empates
df_efficient_equipos = df_efficient_equipos.with_columns([
    (pl.col("goals_for") - pl.col("goals_against")).alias("goal_diff"), # Calculamos los goles de diferencia restadno los goles a fovr menos los goles en contra
    ((pl.col("points") / pl.col("played")).alias("points_per_game")) # Calculamos los puntos por partido dividiendo los puntos por los partidos jugados
])

# Una vez hecho los cálculos, los esribimos en un csv

df_efficient_equipos.write_csv("Equipos_Eficientes_GD_Puntos_Por_Partido.csv") 

# Luego lo pintamos en un scatter

fig = px.scatter(
    df_efficient_equipos.to_pandas(),
    x="goal_diff",
    y="points_per_game",
    color="name_league",
    hover_name="name",
    title="Goal Difference vs Points per Game",
    trendline="ols" # Pintamos también la linea de tendencia de cada liga
)

# Podemos ver que la diferencia de goles y los puntos por partido tiene una correlación positiva, cuanto más diferencia de goles tengas, mayor puntos por partido obtienes

fig.show()

df_goals_against_goals_for_team = df.drop(["wins", "draws"])

df_goals_against_goals_for_team = df_goals_against_goals_for_team.with_columns([
    (pl.col("goals_for") / pl.col("played")).alias("avg_goals_for"),
    (pl.col("goals_against")/pl.col("played")).alias("avg_goals_against")
])

df_goals_against_goals_for_team.write_csv("Ataques_vs_Defensas_Por_Equipo.csv")

fig = px.scatter(
    df_goals_against_goals_for_team.to_pandas(),  # Plotly trabaja mejor con pandas
    x="avg_goals_for",
    y="avg_goals_against",
    color="name_league",
    size="points",
    hover_name="name",
    title="Ataque vs Defensa por Equipo",
    labels={
        "avg_goals_for": "Goles a favor por partido",
        "avg_goals_against": "Goles en contra por partido"
    }
)
mean_attack = df_goals_against_goals_for_team["avg_goals_for"].mean()
mean_defense = df_goals_against_goals_for_team["avg_goals_against"].mean()
fig.add_vline(x=mean_attack, line_dash="dash")
fig.add_hline(y=mean_defense, line_dash="dash")
fig.add_annotation(
    x=0.98, y=0.98,
    xref="paper", yref="paper",
    text="Mucho ataque<br>Poca defensa",
    showarrow=False,
    xanchor="right",
    yanchor="top",
    font=dict(size=12, color="gray")
)

fig.add_annotation(
    x=0.02, y=0.98,
    xref="paper", yref="paper",
    text="Poco ataque<br>Poca defensa",
    showarrow=False,
    xanchor="left",
    yanchor="top",
    font=dict(size=12, color="gray")
)

fig.add_annotation(
    x=0.02, y=0.02,
    xref="paper", yref="paper",
    text="Poco ataque<br>Buena defensa",
    showarrow=False,
    xanchor="left",
    yanchor="bottom",
    font=dict(size=12, color="gray")
)

fig.add_annotation(
    x=0.98, y=0.02,
    xref="paper", yref="paper",
    text="Mucho ataque<br>Buena defensa",
    showarrow=False,
    xanchor="right",
    yanchor="bottom",
    font=dict(size=12, color="gray")
)
fig.update_layout(template="plotly_white")
fig.show()

df_goals_against_liga = df.drop(["name", "wins", "draws", "points"])

df_goals_against_liga = (
    df_goals_against_liga.group_by("name_league").agg([
        pl.sum("goals_against").alias("goals_against"),
        pl.sum("played").alias("played")
    ]).with_columns([
        (pl.col("goals_against")/pl.col("played")).alias("avg_goals_against")
    ])
)

df_goals_against_liga.write_csv("Ligas_Mas_Defensivas.csv")

fig = px.bar(
    df_goals_against_liga.to_pandas(),
    x="name_league",
    y="avg_goals_against",
    color="avg_goals_against",
    color_continuous_scale="Reds",
    title="Promedio de goles encajados por partido por liga"
)
global_avg = (
    df_goals_against_liga["goals_against"].sum() /
    df_goals_against_liga["played"].sum()
)
fig.add_hline(y=global_avg, line_dash="dash", line_color="black")
fig.show()