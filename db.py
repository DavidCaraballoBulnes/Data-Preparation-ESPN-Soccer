import sqlite3
import unicodedata

def create_tables():
    conn = sqlite3.connect("soccer.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS league (id_league INTEGER PRIMARY KEY, name_league TEXT, year INTEGER)"
    )
    conn.commit()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS teams (id INTEGER PRIMARY KEY, name TEXT, logo TEXT, league_id INTEGER, FOREIGN KEY(league_id) REFERENCES league(id_league))"
    )
    conn.commit()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS stats (id_stats INTEGER PRIMARY KEY, team_id INTEGER, points INTEGER, played INTEGER, goals_against INTEGER, goals_for INTEGER, wins INTEGER, draws INTEGER, losses INTEGER, position TEXT, FOREIGN KEY(team_id) REFERENCES teams(id))"
    )
    conn.commit()
    conn.close()


def insert_leagues(leagues):
    conn = sqlite3.connect("soccer.db")
    cursor = conn.cursor()
    prev_leagues = [
        row[0] for row in cursor.execute("SELECT name_league FROM league").fetchall()
    ]
    if (leagues[0]) not in prev_leagues:
        cursor.execute(
            "INSERT INTO league (name_league, year) VALUES (?, ?)",
            (leagues[0], leagues[1]),
        )
    else:
        update_league = cursor.execute(
            "SELECT name_league, year FROM league WHERE name_league = ?", (leagues[0],)
        ).fetchone()
        if update_league[1] != leagues[1]:
            cursor.execute(
                "UPDATE league SET year = ? WHERE name_league = ?",
                (leagues[1], leagues[0]),
            )
            cursor.execute("DELETE FROM stats")
            cursor.execute("DELETE FROM teams")
    conn.commit()
    conn.close()


def insert_teams(teams):
    conn = sqlite3.connect("soccer.db")
    cursor = conn.cursor()
    prev_teams = cursor.execute("SELECT name FROM teams").fetchall()
    for team_name, team_data in teams.items():
        team_data["league"] = cursor.execute(
            "SELECT id_league FROM league WHERE name_league = ?", (team_data["league"],)
        ).fetchone()[0]
        if (team_data["nombre"],) not in prev_teams:
            cursor.execute(
                "INSERT INTO teams (name, league_id, logo) VALUES (?, ?, ?)",
                (team_data["nombre"], team_data["league"], team_data["logo"]),
            )
        else:
            cursor.execute(
                "UPDATE teams SET name = ?, league_id = ?, logo = ? WHERE name = ?",
                (team_data["nombre"], team_data["league"], team_data["logo"], team_data["nombre"]),
            )
        conn.commit()
        insert_stats(team_data["estadisticas"], team_data["nombre"])
    conn.commit()
    conn.close()


def insert_stats(stat, nombreEquipo):
    conn = sqlite3.connect("soccer.db")
    cursor = conn.cursor()
    team_id = cursor.execute("SELECT id FROM teams WHERE name = ?", (nombreEquipo,)).fetchone()
    team_id = team_id[0]
    prev_stats = cursor.execute("SELECT team_id FROM stats").fetchall()
    if (team_id,) in prev_stats:
        cursor.execute(
            "UPDATE stats SET position = ?, points = ?, played = ?, goals_against = ?, goals_for = ?, wins = ?, draws = ?, losses = ? WHERE team_id = ?",
            (
                stat["rank"],
                stat["points"],
                stat["gamesPlayed"],
                stat["pointsAgainst"],
                stat["pointsFor"],
                stat["wins"],
                stat["ties"],
                stat["losses"],
                team_id,
            ),
        )
    else:
        cursor.execute(
            "INSERT INTO stats (position, team_id, points, played, goals_against, goals_for, wins, draws, losses) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                stat["rank"],
                team_id,
                stat["points"],
                stat["gamesPlayed"],
                stat["pointsAgainst"],
                stat["pointsFor"],
                stat["wins"],
                stat["ties"],
                stat["losses"],
            ),
        )
    conn.commit()
    conn.close()

def create_player_tables():
    """
    Crea las tablas para jugadores de campo y porteros con claves foráneas
    hacia las tablas de equipos y ligas.
    """
    conn = sqlite3.connect("soccer.db")
    cursor = conn.cursor()

    # 1. Tabla de Jugadores de Campo (field_players)
    # Relaciona team_id con teams(id) y league_id con league(id_league)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS field_players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            dorsal INTEGER,
            position TEXT,
            age INTEGER,
            nationality TEXT,
            height REAL,
            weight INTEGER,
            games_played INTEGER,
            starts INTEGER,
            subs INTEGER,
            goals INTEGER,
            assists INTEGER,
            shots_on_target INTEGER,
            fouls_committed INTEGER,
            fouls_received INTEGER,
            yellow_cards INTEGER,
            red_cards INTEGER,
            team_id INTEGER,
            league_id INTEGER,
            FOREIGN KEY(team_id) REFERENCES teams(id),
            FOREIGN KEY(league_id) REFERENCES league(id_league)
        )
    """)
    conn.commit()

    # 2. Tabla de Porteros (goalkeepers)
    # Tiene columnas específicas como 'saves' (atajadas) y 'goals_conceded'
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goalkeepers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            dorsal INTEGER,
            position TEXT,
            age INTEGER,
            nationality TEXT,
            height REAL,
            weight INTEGER,
            games_played INTEGER,
            saves INTEGER,
            goals_conceded INTEGER,
            fouls_committed INTEGER,
            fouls_received INTEGER,
            yellow_cards INTEGER,
            red_cards INTEGER,
            team_id INTEGER,
            league_id INTEGER,
            FOREIGN KEY(team_id) REFERENCES teams(id),
            FOREIGN KEY(league_id) REFERENCES league(id_league)
        )
    """)
    conn.commit()
    conn.close()

def normalize_text(text):
    """
    Convierte a minúsculas, elimina tildes y espacios extra.
    Ej: "Atlético de Madrid" -> "atletico de madrid"
    """
    if not text:
        return ""
    
    # 1. A minúsculas
    text = text.lower()
    
    # 2. Normalización Unicode (separar letras de tildes: 'á' -> 'a' + '´')
    text = unicodedata.normalize('NFD', text)
    
    # 3. Filtrar caracteres que no sean marcas diacríticas (eliminar las tildes separadas)
    text = "".join(c for c in text if unicodedata.category(c) != 'Mn')
    
    # 4. Eliminar espacios al inicio/final
    return text.strip()

def insert_players_from_dataframe(df_porteros, df_campo):
    """
    Limpia las tablas de jugadores e inserta los nuevos datos normalizando nombres
    y usando un diccionario de alias para emparejar diferencias entre Web y API.
    """
    conn = sqlite3.connect("soccer.db")
    cursor = conn.cursor()

    print("--- Iniciando actualización de jugadores ---")

    # 1. LIMPIEZA PREVIA (Borrar datos antiguos)
    cursor.execute("DELETE FROM field_players")
    cursor.execute("DELETE FROM goalkeepers")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='field_players'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='goalkeepers'")
    conn.commit()

    # 2. CARGAR MAPA DE EQUIPOS (Con Normalización)
    equipos_db = cursor.execute("SELECT name, id, league_id FROM teams").fetchall()
    
    mapa_equipos = {}
    for fila in equipos_db:
        nombre_original = fila[0]
        id_equipo = fila[1]
        id_liga = fila[2]
        
        clave_normalizada = normalize_text(nombre_original)
        mapa_equipos[clave_normalizada] = {'id': id_equipo, 'league_id': id_liga}

    ALIAS_EQUIPOS = {
        "atletico de madrid": "atletico madrid",
        "sevilla fc": "sevilla",
        "brighton hove albion" : "brighton & hove albion",
        "bolonia" : "bologna",
        "genova" : "genoa",
        "1 fc heidenheim 1846" : "1. fc heidenheim 1846",
        "1 fc union berlin" : "1. fc union berlin",
        "f c augsburgo" : "fc augsburg",
        "st pauli" : "st. pauli"
    }

    def obtener_ids(nombre_equipo_df):
        # 1. Normalizamos lo que viene del DataFrame (ej: "Atletico De Madrid" -> "atletico de madrid")
        nombre_limpio = normalize_text(nombre_equipo_df)
        
        # 2. Aplicamos el parche del diccionario si existe en nuestros alias
        if nombre_limpio in ALIAS_EQUIPOS:
            nombre_limpio = ALIAS_EQUIPOS[nombre_limpio]
            
        # 3. Buscamos en la base de datos
        datos = mapa_equipos.get(nombre_limpio)
        if datos:
            return datos['id'], datos['league_id']
        else:
            print(f"⚠️ AVISO: No se ha encontrado el equipo '{nombre_equipo_df}' en la BD. Sus jugadores no se insertarán.")
            return None, None

    # 3. INSERTAR JUGADORES DE CAMPO
    sql_campo = """
        INSERT INTO field_players (
            name, dorsal, position, age, nationality, height, weight,
            games_played, starts, subs, goals, assists, shots_on_target,
            fouls_committed, fouls_received, yellow_cards, red_cards,
            team_id, league_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    batch_campo = []
    
    for row in df_campo.iter_rows(named=True):
        team_id, league_id = obtener_ids(row['EQUIPO'])

        if team_id:
            batch_campo.append((
                row['NOMBRE'], row['DORSAL'], row['POS'], row['EDAD'], row['NAC'],
                row['ALTURA_M'], row['PESO_KG'], row['PARTIDOS_JUGADOS'],
                row['TITULAR'], row['SUPLENTE'], row['GOLES'], row['ASISTENCIAS'],
                row['TIROS_PUERTA'], row['FALTAS_COMETIDAS'], row['FALTAS_RECIBIDAS'],
                row['TARJETAS_AMARILLAS'], row['TARJETAS_ROJAS'],
                team_id, league_id
            ))
    
    print(f"JUGADORES: {len(batch_campo)}")
    if batch_campo:
        cursor.executemany(sql_campo, batch_campo)
        conn.commit()

    # 4. INSERTAR PORTEROS    
    sql_porteros = """
        INSERT INTO goalkeepers (
            name, dorsal, position, age, nationality, height, weight,
            games_played, saves, goals_conceded,
            fouls_committed, fouls_received, yellow_cards, red_cards,
            team_id, league_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    batch_porteros = []
    
    for row in df_porteros.iter_rows(named=True):
        team_id, league_id = obtener_ids(row['EQUIPO'])
        
        if team_id:
            batch_porteros.append((
                row['NOMBRE'], row['DORSAL'], row['POS'], row['EDAD'], row['NAC'],
                row['ALTURA_M'], row['PESO_KG'], row['PARTIDOS_JUGADOS'],
                row['ATAJADAS'], row['GOLES_EN_CONTRA'],
                row['FALTAS_COMETIDAS'], row['FALTAS_RECIBIDAS'],
                row['TARJETAS_AMARILLAS'], row['TARJETAS_ROJAS'],
                team_id, league_id
            ))
            
    print(f"PORTEROS: {len(batch_porteros)}")
    if batch_porteros:
        cursor.executemany(sql_porteros, batch_porteros)
        conn.commit()

    conn.close()