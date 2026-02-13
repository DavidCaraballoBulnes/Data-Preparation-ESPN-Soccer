import polars as pl
import sys
import os
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

# Crear directorio de almacenamiento de CSV si no existe
DIRECTORIO_CSV = "data_output"
os.makedirs(DIRECTORIO_CSV, exist_ok=True)

def get_df_victory_draw_for_league(df):
    """
    Docstring para get_df_victory_draw_for_league

    Este método nos permite visualizar las victorias y empates por ligas
    
    :param df: DataFrame con los datos a tratar y graficar
    """
    # Nos quedamos solo con los datos que nos interesan
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

    df_ve_liga.write_csv("data_output/Victorias_Empates_Por_Liga.csv") # Una vez calculado todo, lo escribimos en un csv

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
    return df_ve_liga

def get_df_efficients_teams(df):
    """
    Docstring para get_df_efficients_teams
    
    Nos permite ver cuales son los equipos más eficientes, es decir,
    cuantos puntos por partido consigue cada equipo comparandolo con sus goles de diferencia

    :param df: DataFrame con los datos a tratar y graficar
    """
    df_efficient_equipos = df.drop(["wins", "draws"]) # Quitamos valores que no nos interesan como las victorias y los empates
    df_efficient_equipos = df_efficient_equipos.with_columns([
        (pl.col("goals_for") - pl.col("goals_against")).alias("goal_diff"), # Calculamos los goles de diferencia restadno los goles a fovr menos los goles en contra
        ((pl.col("points") / pl.col("played")).alias("points_per_game")) # Calculamos los puntos por partido dividiendo los puntos por los partidos jugados
    ])

    # Una vez hecho los cálculos, los esribimos en un csv

    df_efficient_equipos.write_csv("data_output/Equipos_Eficientes_GD_Puntos_Por_Partido.csv") 

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
    return df_efficient_equipos

def get_df_goals_against_goals_for_teams(df):
    """
    Docstring para get_df_goals_against_goals_for_teams
    
    Este método nos permite visualizar los goles a favor y en contra de cada equipo,
    clasificándolo por quien tiene buena/mala defensa buen/mal ataque comparándolo con la media

    :param df: DataFrame con los datos a tratar y graficar
    """
    # Por otro lado, vamos a hacer una comparación de los goles a favor y en contra de cada equipo, para ver si un equipo es mejor atacando o defendiendo
    df_goals_against_goals_for_team = df.drop(["wins", "draws"])

    df_goals_against_goals_for_team = df_goals_against_goals_for_team.with_columns([
        (pl.col("goals_for") / pl.col("played")).alias("avg_goals_for"), # Calculamos la media de goles a favor por partido
        (pl.col("goals_against")/pl.col("played")).alias("avg_goals_against") # Calculamos la media de goles en contra por partido
    ])

    df_goals_against_goals_for_team.write_csv("data_output/Ataques_vs_Defensas_Por_Equipo.csv") # Lo guardamos en un csv

    fig = px.scatter(
        df_goals_against_goals_for_team.to_pandas(),  # Plotly trabaja mejor con pandas
        x="avg_goals_for", # Ponemos en el eje X los goles a favor
        y="avg_goals_against", # Ponemos los goles en contra en el eje Y
        color="name_league", # El color de cada punto dependerá de la liga a la que se encuentre
        size="points", # El tamaño del punto dependerá de los puntos que tenga el equipo
        hover_name="name", # Cuando pasas el ratón por encima, sale el nombre del equipo
        title="Ataque vs Defensa por Equipo",
        labels={
            "avg_goals_for": "Goles a favor por partido",
            "avg_goals_against": "Goles en contra por partido"
        }
    )

    # Para ver que equipo tiene buena defensa o buen ataque, calculamos la media de los goles a favor y en contra, 
    # para poner una línea horizontal y vertical para establecer dichos límites

    mean_attack = df_goals_against_goals_for_team["avg_goals_for"].mean()
    mean_defense = df_goals_against_goals_for_team["avg_goals_against"].mean()
    fig.add_vline(x=mean_attack, line_dash="dash")
    fig.add_hline(y=mean_defense, line_dash="dash")

    # Añadimos las distintas anotaciones para dividir los distintos equipos por buena/mala defensa y buen/mal equipo

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
    return df_goals_against_goals_for_team

def get_df_goals_against_leagues(df):
    """
    Docstring para get_df_goals_against_leagues
    
    Esta función nos permite ver los goles en contra por cada liga para poder analizar que liga es más defensiva y cuales menos

    :param df: DataFrame con los datos a tratar y graficar
    """
    # Ahora vamos a ver que ligas tiene menos promedio de goles en contra por partido, por lo que cogemos los datos que nos interese
    df_goals_against_liga = df.drop(["name", "wins", "draws", "points"])

    df_goals_against_liga = (
        df_goals_against_liga.group_by("name_league").agg([ # Agrupamos por las diferentes ligas
            pl.sum("goals_against").alias("goals_against"), # Sumamos todos los goles en contra de cada liga
            pl.sum("played").alias("played") # Sumamos los partidos jugados de la liga
        ]).with_columns([
            (pl.col("goals_against")/pl.col("played")).alias("avg_goals_against") # Calculamoms la media de goles en contra por partido de cada liga
        ])
    )

    df_goals_against_liga.write_csv("data_output/Ligas_Mas_Defensivas.csv") # Lo guardamos en un csv

    # Pintamos gráficos de barra para mostrar los resultados
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
    return df_goals_against_liga

def show_avg_league_goals(df):
    """
    Docstring para show_avg_league_goals

    Método para mostrar gráficamente la media de los goles por partido por cada liga.
    
    :param df: DataFrame con los datos a tratar y graficar
    """
    df_goals_league = df.drop(["name", "wins", "goals_for", "points", "draws"])
    avg_league_matches_goals = df_goals_league.group_by("name_league").mean()
    avg_league_goals = avg_league_matches_goals.with_columns((pl.col("goals_against") / pl.col("played")).alias("avg_league_goals"))
    fig = px.pie(avg_league_goals, values='avg_league_goals', names='name_league', title='Media de goles por liga')
    fig.show()
    return avg_league_goals

def show_avg_league_match_pts(df):
    """
    Docstring para show_avg_league_match_pts

    Método para mostrar gráficamente la media de puntos que se consiguen por partido en cada liga.

    :param df: DataFrame con los datos a tratar y graficar
    """
    df_pts_league = df.drop(["name", "wins", "goals_for", "draws", "goals_against"])
    avg_league_pts = df_pts_league.group_by("name_league").mean()
    avg_league_matches_pts = avg_league_pts.with_columns((pl.col("points") / pl.col("played")).alias("mean_league_pts_match"))
    fig = px.pie(avg_league_matches_pts, values='mean_league_pts_match', names='name_league', title='Media de puntos por partido de cada liga')
    fig.show()
    return avg_league_matches_pts

show_avg_league_goals(df)
show_avg_league_match_pts(df)

df_ve_liga = get_df_victory_draw_for_league(df)

df_efficient_teams = get_df_efficients_teams(df)

df_goals_against_goals_for_teams = get_df_goals_against_goals_for_teams(df)

df_goals_against_leagues = get_df_goals_against_leagues(df)
