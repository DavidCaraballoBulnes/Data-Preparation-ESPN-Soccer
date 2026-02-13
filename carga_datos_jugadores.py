"""
Módulo de Scraping de Estadísticas de Fútbol (ESPN Deportes).

Descripción:
    Este script extrae información detallada de las plantillas de equipos de fútbol
    de las 4 grandes ligas europeas (LaLiga, Premier League, Serie A, Bundesliga).
    Separa automáticamente a los porteros de los jugadores de campo y procesa
    datos como estatura, peso, dorsal y estadísticas de juego.

Tecnologías:
    - Requests & BeautifulSoup para la extracción HTML.
    - Pandas para la limpieza preliminar y manejo de tablas HTML.
    - Polars para el tipado fuerte y procesamiento eficiente de datos.

Autor: [David Caraballo Bulnes y Adrián García García]
"""

import requests
from bs4 import BeautifulSoup
import polars as pl
import pandas as pd
import time
import random
import re
from io import StringIO
import warnings

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

# Ignoramos advertencias de obsolescencia de Pandas (específicamente sobre read_html)
warnings.simplefilter(action='ignore', category=FutureWarning)

# Cabeceras HTTP para simular un navegador real y evitar bloqueos (User-Agent Spoofing)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

# Diccionario maestro de ligas y sus URLs base en ESPN
LEAGUES_URLS = {
    "LaLiga": "https://espndeportes.espn.com/futbol/equipos/_/liga/ESP.1/laliga",
    "Premier League": "https://espndeportes.espn.com/futbol/equipos/_/liga/ENG.1/premier-league",
    "Serie A": "https://espndeportes.espn.com/futbol/equipos/_/liga/ITA.1/serie-a",
    "Bundesliga": "https://espndeportes.espn.com/futbol/equipos/_/liga/GER.1/bundesliga"
}

# =============================================================================
# 2. FUNCIONES DE EXTRACCIÓN Y LIMPIEZA
# =============================================================================

def get_squad_links(league_name, league_url):
    """
    Obtiene los enlaces a la sección 'Plantel' de todos los equipos de una liga.

    Args:
        league_name (str): Nombre identificativo de la liga (ej: "LaLiga").
        league_url (str): URL de la página principal de la liga en ESPN.

    Returns:
        list: Lista de diccionarios con metadatos del equipo (url, team_name, league_name).
    """
    try:
        resp = requests.get(league_url, headers=HEADERS)
        resp.raise_for_status() # Verifica errores HTTP (404, 500, etc.)
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        squad_links = []
        # Regex para capturar ID numérico y Slug del equipo desde la URL
        # Estructura esperada: /futbol/equipo/_/id/{ID}/{SLUG}
        pattern = re.compile(r"/futbol/equipo/_/id/(\d+)/([\w\.-]+)")
        seen_ids = set()
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            match = pattern.search(href)
            if match:
                team_id = match.group(1)
                team_slug = match.group(2)
                
                # Evitar duplicados procesando cada ID una sola vez
                if team_id not in seen_ids:
                    # Construcción de la URL específica de la plantilla
                    full_url = f"https://espndeportes.espn.com/futbol/equipo/plantel/_/id/{team_id}/{team_slug}"
                    formatted_name = team_slug.replace('-', ' ').replace('esp.', '').title()
                    
                    squad_links.append({
                        "url": full_url,
                        "team_name": formatted_name,
                        "league_name": league_name
                    })
                    seen_ids.add(team_id)
        
        return squad_links
    except Exception as e:
        print(f"Error recuperando equipos de {league_name}: {e}")
        return []

def clean_pandas_dataframe(df, team_name, league_name):
    """
    Realiza una limpieza preliminar en Pandas antes de la conversión a Polars.
    
    Tareas principales:
    1. Eliminar filas repetitivas de encabezados.
    2. Separar Nombre y Dorsal usando expresiones regulares.
    3. Insertar metadatos (Equipo, Liga).

    Args:
        df (pd.DataFrame): DataFrame crudo extraído del HTML.
        team_name (str): Nombre del club.
        league_name (str): Nombre de la liga.

    Returns:
        pd.DataFrame: DataFrame limpio y estructurado.
    """
    # Eliminar filas donde el nombre se repite (encabezados intermedios en la tabla HTML)
    if 'NOMBRE' in df.columns:
        df = df[df['NOMBRE'] != 'NOMBRE']
    
    # Estandarización de valores nulos (ESPN usa '--' o '-')
    df = df.replace(['--', '-'], None)
    
    # --- Separación de Dorsal y Nombre ---
    # Regex: (Cualquier caracter al inicio) + (Espacio opcional) + (Dígitos al final)
    jersey_regex = r'(.*?)\s*(\d+)$'
    names_str = df['NOMBRE'].astype(str)
    extraction = names_str.str.extract(jersey_regex)
    
    # Grupo 0: Nombre limpio. Grupo 1: Dorsal numérico.
    df['NOMBRE_LIMPIO'] = extraction[0].fillna(df['NOMBRE']).str.strip()
    df['DORSAL'] = extraction[1] 
    
    # Actualizar columnas
    df['NOMBRE'] = df['NOMBRE_LIMPIO']
    df.drop(columns=['NOMBRE_LIMPIO'], inplace=True)
    
    # Inserción de columnas de metadatos al inicio
    # NOTA: Mantenemos los nombres de columna en ESPAÑOL según requerimiento
    df.insert(0, 'EQUIPO', team_name)
    df.insert(0, 'LIGA', league_name)
    
    # Reordenamiento visual de columnas (Liga, Equipo, Nombre, Dorsal...)
    cols = list(df.columns)
    if 'DORSAL' in cols:
        cols.remove('DORSAL')
        cols.insert(3, 'DORSAL')
        df = df[cols]
        
    return df

def process_team_squad(team_info):
    """
    Descarga y procesa la plantilla de un equipo específico.
    Clasifica las tablas encontradas en 'Porteros' o 'Jugadores de Campo'
    basándose en las columnas estadísticas disponibles.

    Args:
        team_info (dict): Diccionario con url, nombre y liga del equipo.

    Returns:
        tuple: (list[pd.DataFrame] gk_list, list[pd.DataFrame] field_list)
    """
    url = team_info["url"]
    team_name = team_info["team_name"]
    league_name = team_info["league_name"]
    
    try:
        resp = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(resp.content, 'html.parser')
        html_tables = soup.find_all('table')
        
        gk_dfs_list = []
        field_dfs_list = []
        
        for table in html_tables:
            try:
                # Uso de StringIO para evitar advertencias de depreciación de Pandas
                html_io = StringIO(str(table))
                df_temp = pd.read_html(html_io, flavor='bs4')[0]
                df_temp.columns = [str(c).upper() for c in df_temp.columns]
                
                # Normalización del nombre de la primera columna
                if 'NOMBRE' not in df_temp.columns and len(df_temp.columns) > 0:
                    df_temp.rename(columns={df_temp.columns[0]: 'NOMBRE'}, inplace=True)
                
                cols = df_temp.columns
                
                # --- Lógica de Clasificación ---
                # Si tiene 'GA' (Goles Admitidos) -> Es tabla de Porteros
                if 'GA' in cols:
                    gk_dfs_list.append(clean_pandas_dataframe(df_temp, team_name, league_name))
                # Si tiene 'G' (Goles) y Posición -> Es tabla de Jugadores de Campo
                elif ('G' in cols or 'TM' in cols) and 'POS' in cols:
                    field_dfs_list.append(clean_pandas_dataframe(df_temp, team_name, league_name))
            except Exception:
                continue # Si una tabla falla, continuar con la siguiente

        return gk_dfs_list, field_dfs_list
    
    except Exception as e:
        print(f"Error procesando {team_name}: {e}")
        return [], []

def convert_to_polars(dfs_list, player_type):
    """
    Consolida una lista de DataFrames de Pandas en un único DataFrame de Polars.
    Realiza limpieza de tipos, manejo de unidades (m, kg) y renombrado de columnas.

    Args:
        dfs_list (list): Lista de DataFrames de Pandas.
        player_type (str): "PORTEROS" o "JUGADORES DE CAMPO" para aplicar mapeos específicos.

    Returns:
        pl.DataFrame: DataFrame final procesado y tipado.
    """
    if not dfs_list:
        print(f"No hay datos disponibles para {player_type}.")
        return pl.DataFrame()

    # 1. Unificación y Conversión a String
    # Convertimos todo a string en Pandas para evitar errores de inferencia de tipos (ArrowInvalid)
    # al pasar datos mixtos a Polars.
    df_pd = pd.concat(dfs_list, ignore_index=True).astype(str)
    
    # 2. Creación del DataFrame de Polars
    df_pl = pl.from_pandas(df_pd)
    
    # 3. Restauración de Nulos Reales
    # Convertimos cadenas 'nan', 'None', etc., de vuelta a null real de Polars
    df_pl = df_pl.select([
        pl.col(col).replace(['nan', 'None', '<NA>', '--'], None) 
        for col in df_pl.columns
    ])

    # 4. Limpieza Específica (Estatura y Peso)
    # Eliminamos unidades métricas y convertimos a número
    if 'EST' in df_pl.columns:
        df_pl = df_pl.with_columns(
            pl.col('EST')
            .str.replace(" m", "")
            .str.replace(",", ".")
            .str.strip_chars()
            .cast(pl.Float64, strict=False)
        )
    if 'P' in df_pl.columns:
        df_pl = df_pl.with_columns(
            pl.col('P')
            .str.replace(" kg", "")
            .str.strip_chars()
            .cast(pl.Int64, strict=False)
        )

    # 5. Conversión de Tipos Numéricos (Casting seguro)
    int_cols = ['PJ', 'G', 'A', 'TA', 'TR', 'AP', 'SUB', 'TT', 'FC', 'FS', 'EDAD', 'DORSAL', 'TM', 'GA']
    for col in int_cols:
        if col in df_pl.columns:
            df_pl = df_pl.with_columns(pl.col(col).str.strip_chars().cast(pl.Int64, strict=False))

    # 6. Renombrado de Columnas (Mapeo a Español)
    if player_type == "PORTEROS":
        mapping = {
            "AP": "PARTIDOS_JUGADOS", "A": "ATAJADAS", "GA": "GOLES_EN_CONTRA", 
            "FC": "FALTAS_COMETIDAS", "FS": "FALTAS_RECIBIDAS", "TA": "TARJETAS_AMARILLAS", 
            "TR": "TARJETAS_ROJAS", "P": "PESO_KG", "EST": "ALTURA_M", "A.1": "ASISTENCIAS"
        }
    else: 
        mapping = {
            "AP": "PARTIDOS_JUGADOS", "G": "GOLES", "A": "ASISTENCIAS", 
            "TT": "TITULAR", "SUB": "SUPLENTE", "TM": "TIROS_PUERTA", 
            "FC": "FALTAS_COMETIDAS", "FS": "FALTAS_RECIBIDAS", "TA": "TARJETAS_AMARILLAS", 
            "TR": "TARJETAS_ROJAS", "P": "PESO_KG", "EST": "ALTURA_M"
        }

    # Aplicar renombrado solo a columnas existentes
    clean_map = {k: v for k, v in mapping.items() if k in df_pl.columns}
    df_pl = df_pl.rename(clean_map)
    
    # Eliminar columnas residuales sin nombre
    cols_to_drop = [c for c in df_pl.columns if "UNNAMED" in c.upper()]
    if cols_to_drop:
        df_pl = df_pl.drop(cols_to_drop)
    
    return df_pl

# =============================================================================
# 3. FUNCIÓN PRINCIPAL DE EJECUCIÓN (Interfaz Pública)
# =============================================================================

def load_players():
    """
    Función orquestadora principal. 
    Itera sobre todas las ligas configuradas, extrae los datos de todos los equipos,
    consolida la información y retorna los DataFrames finales.

    Returns:
        tuple: (pl.DataFrame porteros, pl.DataFrame jugadores_campo)
    """
    print("Iniciando proceso de carga de jugadores...")
    master_gk = []
    master_field = []
    
    # Iteración sobre el diccionario de ligas
    for league_name, league_url in LEAGUES_URLS.items():
        print(f"--- Procesando Liga: {league_name} ---")
        
        # 1. Obtener lista de equipos
        teams_list = get_squad_links(league_name, league_url)
        
        # 2. Procesar cada equipo individualmente
        for team_info in teams_list:
            gk_dfs, field_dfs = process_team_squad(team_info)
            
            if gk_dfs: master_gk.extend(gk_dfs)
            if field_dfs: master_field.extend(field_dfs)
            
            # Pausa aleatoria para evitar saturación del servidor (Rate Limiting)
            time.sleep(random.uniform(0.5, 1.5))

    # Retorno de los DataFrames procesados en Polars
    return convert_to_polars(master_gk, "PORTEROS"), convert_to_polars(master_field, "JUGADORES DE CAMPO")