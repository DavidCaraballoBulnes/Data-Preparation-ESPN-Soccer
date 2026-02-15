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

# Consulta SQL principal para extraer estadísticas generales ligadas a equipos y ligas
query = "SELECT name, played, wins, draws, points, goals_against, goals_for, name_league  FROM stats s INNER JOIN teams t ON team_id=id INNER JOIN league l ON league_id=id_league"

# Leer la base de datos con Polars empleando la query generada
df = pl.read_database_uri(query=query, uri=uri)

# Crear directorio de almacenamiento de CSV si no existe
DIRECTORIO_CSV = "data_output"
os.makedirs(DIRECTORIO_CSV, exist_ok=True)

# Crear directorio de almacenamiento de gráficos si no existe
DIRECTORIO_GRAFICOS = "graficos"
os.makedirs(DIRECTORIO_GRAFICOS, exist_ok=True)

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

    df_ve_liga.write_csv(DIRECTORIO_CSV+"/Victorias_Empates_Por_Liga.csv") # Una vez calculado todo, lo escribimos en un csv

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
    
    fig.write_html(DIRECTORIO_GRAFICOS+"/Victorias_Empates_Por_Liga.html")
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

    df_efficient_equipos.write_csv(DIRECTORIO_CSV+"/Equipos_Eficientes_GD_Puntos_Por_Partido.csv") 

    # Luego lo pintamos en un scatter

    fig = px.scatter(
        df_efficient_equipos.to_pandas(),
        x="goal_diff",
        y="points_per_game",
        color="name_league",
        hover_name="name",
        title="Goles de diferencia vs puntos por partido",
        trendline="ols" # Pintamos también la linea de tendencia de cada liga
    )

    # Podemos ver que la diferencia de goles y los puntos por partido tiene una correlación positiva, cuanto más diferencia de goles tengas, mayor puntos por partido obtienes
    fig.write_html(DIRECTORIO_GRAFICOS+"/Equipos_Eficientes_GD_Puntos_Por_Partido.html")
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

    df_goals_against_goals_for_team.write_csv(DIRECTORIO_CSV+"/Ataques_vs_Defensas_Por_Equipo.csv") # Lo guardamos en un csv

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
    fig.write_html(DIRECTORIO_GRAFICOS+"/Ataques_vs_Defensas_Por_Equipo.html")
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
            (pl.col("goals_against")/pl.col("played")).alias("avg_goals_against") # Calculamos la media de goles en contra por partido de cada liga
        ])
    )

    df_goals_against_liga.write_csv(DIRECTORIO_CSV+"/Ligas_Mas_Defensivas.csv") # Lo guardamos en un csv

    # Pintamos gráficos de barra para mostrar los resultados
    fig = px.bar(
        df_goals_against_liga.to_pandas(),
        x="name_league",
        y="avg_goals_against",
        color="avg_goals_against",
        color_continuous_scale="Reds",
        title="Promedio de goles encajados por partido por liga"
    )
    
    # Calculamos la media global para añadirla como línea de referencia en el gráfico
    global_avg = (
        df_goals_against_liga["goals_against"].sum() /
        df_goals_against_liga["played"].sum()
    )
    fig.add_hline(y=global_avg, line_dash="dash", line_color="black")
    
    fig.write_html(DIRECTORIO_GRAFICOS+"/Ligas_Mas_Defensivas.html")
    fig.show()
    return df_goals_against_liga

def get_df_avg_league_match_goals(df):
    """
    Docstring para get_df_avg_league_match_goals

    Método para mostrar gráficamente la media de los goles por partido por cada liga.
    
    :param df: DataFrame con los datos a tratar y graficar
    """
    # Descartamos variables irrelevantes para enfocarnos únicamente en los cálculos de goles
    df_goals_league = df.drop(["name", "wins", "goals_for", "points", "draws"])
    
    # Agrupamos por la liga para extraer la media aritmética de las columnas numéricas
    avg_league_matches_goals = df_goals_league.group_by("name_league").mean()
    
    # Calculamos la media de goles general dividiendo goles en contra entre los partidos jugados
    avg_league_goals = avg_league_matches_goals.with_columns((pl.col("goals_against") / pl.col("played")).alias("avg_league_goals"))

    # Exportamos el DataFrame transformado a formato CSV
    avg_league_goals.write_csv(DIRECTORIO_CSV+"/Media_Goles_Partido_Ligas.csv")

    # Representamos la proporción de goles mediante un gráfico de tipo Pie (Tarta)
    fig = px.pie(avg_league_goals, values='avg_league_goals', names='name_league', title='Media de goles por partido de cada liga')
    fig.write_html(DIRECTORIO_GRAFICOS+"/Media_Goles_Partido_Ligas.html")
    fig.show()
    return avg_league_goals

def get_df_avg_league_match_pts(df):
    """
    Docstring para get_df_avg_league_match_pts

    Método para mostrar gráficamente la media de puntos que se consiguen por partido en cada liga.

    :param df: DataFrame con los datos a tratar y graficar
    """
    # Eliminamos columnas que no intervienen en el cálculo de eficiencia por puntos
    df_pts_league = df.drop(["name", "wins", "goals_for", "draws", "goals_against"])
    
    # Obtenemos las medias base agrupando los datos según la liga
    avg_league_pts = df_pts_league.group_by("name_league").mean()
    
    # Generamos la métrica final de puntos por partido (puntos obtenidos / partidos disputados)
    avg_league_matches_pts = avg_league_pts.with_columns((pl.col("points") / pl.col("played")).alias("mean_league_pts_match"))

    # Guardamos los resultados para alimentar visualizaciones externas si es necesario
    avg_league_matches_pts.write_csv(DIRECTORIO_CSV+"/Media_Puntos_Partidos_Ligas.csv")

    # Representamos los datos en un gráfico de tarta para comparar el peso relativo de cada liga
    fig = px.pie(avg_league_matches_pts, values='mean_league_pts_match', names='name_league', title='Media de puntos por partido de cada liga')
    fig.write_html(DIRECTORIO_GRAFICOS+"/Media_Puntos_Partidos_Ligas.html")
    fig.show()
    return avg_league_matches_pts

# =========================================================================
# EJECUCIÓN: ANÁLISIS A NIVEL DE EQUIPOS Y LIGAS
# =========================================================================

df_avg_league_goals = get_df_avg_league_match_goals(df)

df_avg_league_match_pts = get_df_avg_league_match_pts(df)

df_ve_ligue = get_df_victory_draw_for_league(df)

df_efficient_teams = get_df_efficients_teams(df)

df_goals_against_goals_for_teams = get_df_goals_against_goals_for_teams(df)

df_goals_against_leagues = get_df_goals_against_leagues(df)


# Gráficos de jugadores

wings_players = ["Vinícius Júnior", "Nico Williams", "Antony", "Lamine Yamal", "Raphinha", "Marcus Rashford", "Mohamed Salah", "Rafael Leão", "Jérémy Doku", "Alejandro Garnacho", "Arnaut Danjuma", "Thiago Almada", "Chidera Ejuke"]
# Convertimos la lista en string SQL
players_sql_wingers = ", ".join([f"'{player}'" for player in wings_players])

# Consulta SQL estructurada para extraer las estadísticas exhaustivas de jugadores de campo (field_players)
query = f"""
SELECT 
    -- Columnas de la tabla field_players (Jugadores)
    fp.id AS player_id,
    fp.name AS player_name,
    fp.dorsal,
    fp.position,
    fp.age,
    fp.nationality,
    fp.height,
    fp.weight,
    fp.games_played,
    fp.starts,
    fp.subs,
    fp.goals,
    fp.assists,
    fp.shots_on_target,
    fp.fouls_committed,
    fp.fouls_received,
    fp.yellow_cards,
    fp.red_cards,
    fp.team_id AS player_team_id,
    fp.league_id AS player_league_id,

    -- Columnas de la tabla teams (Equipos)
    t.id AS team_id,
    t.name AS team_name,
    t.logo AS team_logo,
    t.league_id AS team_league_id,

    -- Columnas de la tabla league (Ligas)
    l.id_league,
    l.name_league,
    CAST(l.year AS TEXT) AS league_year
    
FROM field_players fp
INNER JOIN teams t ON fp.team_id = t.id
INNER JOIN league l ON fp.league_id = l.id_league
"""

# Generación del DataFrame para jugadores de campo
df_players = pl.read_database_uri(query=query, uri=uri)

# Consulta SQL estructurada para aislar las estadísticas específicas y únicas de los porteros (goalkeepers)
query_porteros = f"""
SELECT 
    -- Columnas de la tabla goalkeepers (Porteros)
    gk.id AS player_id,
    gk.name AS player_name,
    gk.dorsal,
    gk.position,
    gk.age,
    gk.nationality,
    gk.height,
    gk.weight,
    gk.games_played,
    gk.saves,              -- Atajadas (específico de porteros)
    gk.goals_conceded,     -- Goles encajados (específico de porteros)
    gk.fouls_committed,
    gk.fouls_received,
    gk.yellow_cards,
    gk.red_cards,
    gk.team_id AS player_team_id,
    gk.league_id AS player_league_id,

    -- Columnas de la tabla teams (Equipos)
    t.id AS team_id,
    t.name AS team_name,
    t.logo AS team_logo,
    t.league_id AS team_league_id,

    -- Columnas de la tabla league (Ligas)
    l.id_league,
    l.name_league,
    CAST(l.year AS TEXT) AS league_year
    
FROM goalkeepers gk
INNER JOIN teams t ON gk.team_id = t.id
INNER JOIN league l ON gk.league_id = l.id_league
"""

# Generación del DataFrame exclusivamente para porteros
df_goalkeepers = pl.read_database_uri(query=query_porteros, uri=uri)

def get_df_goals_assist_wingers(df, wingers):
    """
    Docstring para get_df_goals_assist_wingers

    Filtra los datos de los jugadores para centrarse en una lista específica de extremos (wingers).
    Calcula su contribución ofensiva total (Goles + Asistencias) y genera una visualización 
    compuesta: un gráfico de barras apiladas y un gráfico de dispersión (Scatter Plot).

    :param df: DataFrame general con las métricas de los jugadores.
    :param wingers: Lista de cadenas que contiene los nombres de los extremos seleccionados.
    :return: DataFrame filtrado y ordenado con el análisis individual de cada jugador.
    """
    # Aislamos a los jugadores utilizando la lista de parámetros introducida
    df_wingers = df.filter(pl.col("player_name").is_in(wingers))
    
    # Descartamos columnas prescindibles para el contexto de contribución de goles
    df_wingers = df_wingers.drop(["team_name", "games_played"])
    
    # Computamos la contribución total agregando goles y asistencias, y ordenamos los resultados de mayor a menor
    df_wingers = (
    df_wingers.with_columns(
        (pl.col("goals") + pl.col("assists")).alias("total_contribution")
    )
    .sort("total_contribution", descending=True)
    )
    
    # Volcamos a CSV para posibilitar análisis independientes
    df_wingers.write_csv(DIRECTORIO_CSV+"/Goles_Asistencias_Extremos.csv")
    
    # Convertimos a Pandas para integrarlo sin incidencias con la librería Plotly
    df_pd = df_wingers.to_pandas()

    # Preparamos un lienzo con 1 fila y 2 columnas para el reporte dual
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Goles + Asistencias", "Goles vs Asistencias"),
        horizontal_spacing=0.15
    )

    # Barras apiladas: Trazado de los goles aportados
    fig.add_trace(
        go.Bar(
            x=df_pd["player_name"],
            y=df_pd["goals"],
            name="Goles"
        ),
        row=1, col=1
    )

    # Barras apiladas: Trazado de las asistencias aportadas
    fig.add_trace(
        go.Bar(
            x=df_pd["player_name"],
            y=df_pd["assists"],
            name="Asistencias"
        ),
        row=1, col=1
    )

    # Scatter plot: Permite evaluar la relación proporcional entre asistir o anotar
    fig.add_trace(
        go.Scatter(
            x=df_pd["goals"],
            y=df_pd["assists"],
            mode="markers+text",
            text=df_pd["player_name"],
            textposition="top center",
            name="Jugador",
            marker=dict(
                size=df_pd["total_contribution"] * 2  # tamaño según contribución
            ),
            hovertemplate=(
                "<b>%{text}</b><br>" +
                "Goles: %{x}<br>" +
                "Asistencias: %{y}<br>"
            )
        ),
        row=1, col=2
    )

    # Aseguramos que el barmode se aplique en formato de pila (stack)
    fig.update_layout(
        barmode="stack",
        title="Comparación de Extremos - Goles y Asistencias",
    )

    # Personalizamos las etiquetas de los sub-gráficos
    fig.update_xaxes(title_text="Jugador", row=1, col=1)
    fig.update_yaxes(title_text="Cantidad", row=1, col=1)

    fig.update_xaxes(title_text="Goles", row=1, col=2)
    fig.update_yaxes(title_text="Asistencias", row=1, col=2)

    fig.write_html(DIRECTORIO_GRAFICOS+"/Goles_Asistencias_Extremos.html")
    fig.show()
    return df_wingers

def get_df_fouls_received_per_game(df, wingers):
    """
    Docstring para get_df_fouls_received_per_game

    Calcula el ratio o promedio de faltas recibidas por partido para una selección de extremos.
    Genera un gráfico de barras comparativo destacando qué jugadores sufren más el impacto defensivo.

    :param df: DataFrame con las métricas acumuladas de jugadores.
    :param wingers: Lista de extremos objeto de nuestro análisis.
    :return: DataFrame actualizado incluyendo el cálculo de faltas promedio.
    """
    # Filtramos la tabla general para focalizarnos exclusivamente en los extremos
    df_wingers = df.filter(pl.col("player_name").is_in(wingers))
    
    # Descartamos columnas irrelevantes para aligerar la carga de procesamiento
    df_wingers = df_wingers.drop(["team_name", "name_league", "goals", "assists"])
    
    # Ejecutamos la métrica dividiendo las faltas recibidas entre los partidos disputados
    df_fouls_per_game = df_wingers.with_columns(
    (pl.col("fouls_received") / pl.col("games_played")).alias("fouls_per_game")
    )

    # Guardado físico de la extracción de datos
    df_fouls_per_game.write_csv(DIRECTORIO_CSV+"/Faltas_Recibidas_Extremos.csv")

    # Pintamos gráficos de barra para mostrar los resultados de las faltas
    fig = px.bar(
        df_fouls_per_game.to_pandas(),
        x="player_name",
        y="fouls_per_game",
        color="player_name",
        color_continuous_scale="Reds",
        title="Faltas cometidas a los extremos por partido"
    )

    fig.write_html(DIRECTORIO_GRAFICOS+"/Faltas_Recibidas_Extremos.html")
    fig.show()
    return df_fouls_per_game

def get_df_avg_team_ages(df_players, df_goalkeepers):
    """
    Calcula y grafica la edad media de cada equipo utilizando un gráfico 
    de puntos (Cleveland Dot Plot). 
    Incluye un componente interactivo (Slider) para ajustar la altura del gráfico.
    
    :param df_players: pl.DataFrame con los datos de los jugadores de campo.
    :param df_goalkeepers: pl.DataFrame con los datos de los porteros.
    :return: pl.DataFrame con la edad media calculada por equipo.
    """
    # 1. CONSOLIDACIÓN DE DATOS
    # Unimos a los jugadores de campo y a los porteros para obtener la plantilla completa.
    # Seleccionamos únicamente las columnas necesarias para optimizar la memoria.
    df_team_ages = pl.concat([
        df_players['player_name', 'age', 'team_name', 'name_league'], 
        df_goalkeepers['player_name', 'age', 'team_name', 'name_league']
    ])

    # 2. LIMPIEZA DE DATOS (DATA IMPUTATION)
    # Corrección manual de un valor atípico (nulo). 
    # Tras una investigación externa, se determinó que el jugador sin edad registrada tiene 16 años.
    df_team_ages = df_team_ages.with_columns(
        pl.col("age").fill_null(16)
    )

    # 3. AGREGACIÓN Y CÁLCULO
    # Agrupamos por equipo y calculamos la media aritmética de la columna 'age'.
    df_avg_team_ages = df_team_ages.group_by("team_name").agg(
        pl.col("age").mean().alias("avg_age")
    )

    # 4. ORDENACIÓN
    # Ordenar los datos de menor a mayor es crucial en un Dot Plot para crear 
    # un efecto de "escalera" visual y facilitar el ranking de equipos.
    df_avg_team_ages = df_avg_team_ages.sort("avg_age", descending=False)

    df_avg_team_ages.write_csv(DIRECTORIO_CSV+"/Media_Edades_Equipos.csv")

    # 5. CREACIÓN DEL GRÁFICO (SCATTER / DOT PLOT)
    fig = px.scatter(
        df_avg_team_ages.to_pandas(), 
        x="avg_age", 
        y="team_name",
        title="Edad Media de las Plantillas por Equipo",
        labels={
            "avg_age": "Edad Media (Años)",
            "team_name": "" # Se omite el título del eje Y por ser redundante
        },
        color="avg_age", 
        color_continuous_scale="RdYlBu_r" # Escala divergente: Azul (Jóvenes) -> Rojo (Veteranos)
    )

    # Ajustes estéticos de los marcadores (puntos más grandes y con borde para destacar)
    fig.update_traces(
        marker=dict(size=14, line=dict(width=1, color="DarkSlateGrey"))
    )

    # =========================================================================
    # 6. CONFIGURACIÓN DE INTERACTIVIDAD: SLIDER DE ALTURA
    # =========================================================================
    steps = []
    # Definimos el rango de alturas permitidas para el slider (600px a 1500px, en saltos de 100px)
    alturas_disponibles = list(range(600, 1600, 100))
    altura_por_defecto = 900
    indice_por_defecto = alturas_disponibles.index(altura_por_defecto)
    
    # Construcción de las opciones (steps) del slider
    for h in alturas_disponibles:
        step = dict(
            method="relayout",          # 'relayout' modifica únicamente propiedades de diseño de la figura
            args=[{"height": h}],       # Se pasa el nuevo valor de altura
            label=f"{h} px"             # Etiqueta visible bajo la marca del slider
        )
        steps.append(step)

    # Ensamblaje del componente Slider con su formato
    sliders = [dict(
        active=indice_por_defecto,
        currentvalue={"prefix": "Altura actual: "},
        pad={"t": 60},                  # Separación superior (padding-top) para no pisar el eje X
        steps=steps
    )]

    # 7. APLICACIÓN DEL LAYOUT FINAL
    fig.update_layout(
        plot_bgcolor="white",
        # Cuadrículas de fondo para guiar la vista desde el nombre del equipo hasta el punto
        yaxis=dict(showgrid=True, gridcolor="whitesmoke", gridwidth=1),
        xaxis=dict(showgrid=True, gridcolor="lightgray", gridwidth=1, zeroline=False),
        height=altura_por_defecto,      # Altura inicial sincronizada con el slider
        coloraxis_colorbar=dict(title="Edad"),
        sliders=sliders                 # Inserción del control interactivo en la figura
    )

    # Renderizar el gráfico
    fig.write_html(DIRECTORIO_GRAFICOS+"/Media_Edades_Equipos.html")
    fig.show()
    
    # Retornamos el DataFrame procesado por si se requiere en otras funciones
    return df_avg_team_ages

def get_df_total_goals_by_nationality_map(df_players):
    """
    Calcula la SUMA TOTAL de goles por nacionalidad y lo representa 
    en un mapa geográfico interactivo (Choropleth).
    """
    
    # 1. Seleccionamos columnas y rellenamos nulos con 0
    df_team_country_goals = (
        df_players
        .select(["player_name", "nationality", "goals", "team_name", "name_league"])
        .with_columns(pl.col("goals").fill_null(0))
    )
    
    # 2. Agrupación y Suma de goles (en lugar de media)
    df_total_country_goals = df_team_country_goals.group_by("nationality").agg(
        pl.col("goals").sum().alias("total_goals"),                 # Suma de goles
        pl.col("player_name").count().alias("player_count")         # Conteo de jugadores
    )
    
    # 3. Filtramos países que tengan al menos 1 gol para limpiar el mapa
    df_total_country_goals = (
        df_total_country_goals
        .filter(pl.col("total_goals") > 0)
        .sort("total_goals", descending=True)
    )

    df_total_country_goals.write_csv(DIRECTORIO_CSV+"/Total_Goles_Nacionalidad.csv")

    # =========================================================================
    # MAPEO DE PAÍSES PARA PLOTLY (De Español a Código ISO Alpha-3)
    # =========================================================================
    PAISES_ISO = {
        "España": "ESP", "Argentina": "ARG", "Brasil": "BRA", "Francia": "FRA",
        "Uruguay": "URY", "Alemania": "DEU", "Inglaterra": "GBR", "Portugal": "PRT",
        "Italia": "ITA", "Países Bajos": "NLD", "Holanda": "NLD", "Bélgica": "BEL",
        "Croacia": "HRV", "Marruecos": "MAR", "Colombia": "COL", "Senegal": "SEN",
        "Suiza": "CHE", "Polonia": "POL", "Serbia": "SRB", "Gales": "WAL",
        "Estados Unidos": "USA", "México": "MEX", "Ecuador": "ECU", "Ghana": "GHA",
        "Camerún": "CMR", "Corea del Sur": "KOR", "Japón": "JPN", "Canadá": "CAN",
        "Costa Rica": "CRI", "Dinamarca": "DNK", "Túnez": "TUN", "Arabia Saudita": "SAU",
        "Australia": "AUS", "Malasia": "MYS", "Finlandia": "FIN", "Grecia": "GRC",
        "Rumania": "ROU", "Chile": "CHL", "Paraguay": "PRY", "Perú": "PER",
        "Venezuela": "VEN", "Noruega": "NOR", "Suecia": "SWE", "Turquía": "TUR",
        "Argelia": "DZA", "Costa de Marfil": "CIV", "Egipto": "EGY", "Nigeria": "NGA",
        "Mali": "MLI", "Guinea": "GIN", "República Democrática del Congo": "COD",
        "Ucrania": "UKR", "República Checa": "CZE", "Austria": "AUT", "Escocia": "SCO",
        "Irlanda": "IRL", "Islandia": "ISL", "Albania": "ALB", "Bosnia y Herzegovina": "BIH"
    }

    # Convertimos a Pandas para graficar y aplicamos el mapeo
    df_pandas = df_total_country_goals.to_pandas()
    
    # Creamos una nueva columna con el código ISO. Si el país no está en el dicc, lo deja tal cual.
    df_pandas['iso_alpha'] = df_pandas['nationality'].map(PAISES_ISO).fillna(df_pandas['nationality'])

    # 4. Creación del Mapa (Choropleth) con Plotly
    fig = px.choropleth(
        df_pandas,
        locations="iso_alpha",          # Usamos los códigos ISO (ej: "ESP", "ARG")
        color="total_goals",            # La intensidad del color depende de los goles
        hover_name="nationality",       # Al pasar el ratón, queremos leer "España", no "ESP"
        hover_data={
            "iso_alpha": False,         # Ocultamos el código ISO en el recuadro flotante
            "player_count": True, 
            "total_goals": True
        },
        title="Suma Total de Goles por Nacionalidad",
        labels={
            "total_goals": "Goles Totales",
            "player_count": "Nº Jugadores",
            "nationality": "País"
        },
        color_continuous_scale="Viridis", # Una paleta que contrasta muy bien en mapas
        projection="natural earth"        # Hace que el mapa se vea curvado/realista en vez de un rectángulo plano
    )
    
    # Estilo del mapa
    fig.update_layout(
        margin={"r":0, "t":50, "l":0, "b":0},
        geo=dict(
            showframe=False,        # Quita el marco negro exterior
            showcoastlines=True,    # Dibuja las costas
            coastlinecolor="Black",
            projection_type='natural earth'
        )
    )
    
    fig.write_html(DIRECTORIO_GRAFICOS+"/Total_Goles_Nacionalidad.html")
    fig.show()
    return df_total_country_goals

# =========================================================================
# EJECUCIÓN: ANÁLISIS ESPECÍFICO DE JUGADORES
# =========================================================================

df_wingers = get_df_goals_assist_wingers(df_players, wings_players)

df_fouls_wingers_per_game = get_df_fouls_received_per_game(df_players, wings_players)

df_avg_team_ages = get_df_avg_team_ages(df_players, df_goalkeepers)

df_total_goals_nationality = get_df_total_goals_by_nationality_map(df_players)