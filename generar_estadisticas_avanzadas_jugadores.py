import pandas as pd
import time
import unicodedata
from understatapi import UnderstatClient
import LanusStats as ls
import Scrapping as sc
import sys
sys.stdout.reconfigure(encoding='utf-8')

# --- EL PARCHE NINJA PARA PANDAS ---
if not hasattr(pd.DataFrame, 'applymap'):
    pd.DataFrame.applymap = pd.DataFrame.map
# -----------------------------------

def limpiar_nombre(nombre):
    """Normaliza los nombres: quita tildes, minúsculas y espacios extra."""
    if pd.isna(nombre):
        return ""
    nombre = str(nombre).lower().strip()
    # Elimina tildes y caracteres especiales comunes
    nombre = ''.join(c for c in unicodedata.normalize('NFD', nombre) if unicodedata.category(c) != 'Mn')
    return nombre

def obtener_datos_understat(temporada="2025"):
    """Descarga los datos base ofensivos y de xG desde Understat (Sin La Liga)."""
    # Hemos quitado 'La_Liga' de aquí
    ligas = ['La_Liga','EPL', 'Bundesliga', 'Serie_A', 'Ligue_1'] 
    todos_los_jugadores = []

    print("\n[1/2] Iniciando descarga masiva desde UnderstatAPI...")

    with UnderstatClient() as understat:
        for liga in ligas:
            print(f"  -> Descargando datos de la liga: {liga}...")
            try:
                data = understat.league(league=liga).get_player_data(season=temporada)
                df_liga = pd.DataFrame(data)
                df_liga['League'] = liga
                todos_los_jugadores.append(df_liga)
                print(f"  ✅ {len(df_liga)} jugadores descargados de {liga}.")
            except Exception as e:
                print(f"  ❌ Error al descargar datos de {liga}: {e}")

    if todos_los_jugadores:
        df_final = pd.concat(todos_los_jugadores, ignore_index=True)
        cols_numericas = ['goals', 'shots', 'xG', 'time', 'assists', 'xA', 'key_passes', 
                          'yellow_cards', 'red_cards', 'npg', 'npxG', 'xGChain', 'xGBuildup']
        
        for col in cols_numericas:
            if col in df_final.columns:
                df_final[col] = pd.to_numeric(df_final[col], errors='coerce')
        
        # Creamos la columna limpia para futuros cruces
        df_final['player_name_limpio'] = df_final['player_name'].apply(limpiar_nombre)
        
        print(f"🎉 Fase 1 completada. {len(df_final)} jugadores en la base de datos.")
        return df_final
    else:
        print("\n⚠️ No se pudieron descargar datos de Understat.")
        return None

def obtener_defensa_fbref(df_base, temporada_fbref="2025-2026"):
    """Descarga las entradas (tackles) desde FBRef y las une al DataFrame base."""
    fbref = sc.Fbref()
    ligas_fbref = {
        'La_Liga': 'La Liga',
        'EPL': 'Premier League',
        'Bundesliga': 'Bundesliga',
        'Serie_A': 'Serie A',
        'Ligue_1': 'Ligue 1'
    }
    
    datos_defensa_fbref = []
    print("\n[2/2] Conectando con Fbref para descargar las Entradas (Tackles)...")

    for liga_understat, liga_fb in ligas_fbref.items():
        exito = False
        intentos = 0
        max_intentos = 3
        
        while not exito and intentos < max_intentos:
            intentos += 1
            print(f"  -> Descargando defensa de: {liga_fb} (Intento {intentos}/{max_intentos})...")
            
            try:
                df_def = fbref.get_player_season_stats(stat="defense", league=liga_fb, season=temporada_fbref)
                
                if isinstance(df_def.columns, pd.MultiIndex):
                    df_def.columns = ['_'.join(col).strip() for col in df_def.columns.values]
                    col_jugador = [c for c in df_def.columns if 'Player' in c][0]
                    col_entradas = [c for c in df_def.columns if 'TklW' in c and 'Tackles' in c][0]
                else:
                    col_jugador = 'Player'
                    col_entradas = 'TklW'

                df_limpio = df_def[[col_jugador, col_entradas]].copy()
                df_limpio.rename(columns={col_jugador: 'player_name', col_entradas: 'tackles'}, inplace=True)
                
                # Creamos la columna limpia
                df_limpio['player_name_limpio'] = df_limpio['player_name'].apply(limpiar_nombre)
                
                datos_defensa_fbref.append(df_limpio)
                exito = True 
                print("  ✅ ¡Éxito! Esperando 10 segundos para la próxima liga...")
                time.sleep(10)
                
            except Exception as e:
                print(f"  ⚠️ Error en el intento {intentos} con {liga_fb}: {e}")
                if intentos < max_intentos:
                    print("  ⏳ Fbref nos cortó la conexión. Esperando 20 segundos...")
                    time.sleep(20)
                else:
                    print(f"  ❌ Se agotaron los intentos para {liga_fb}.")

    if datos_defensa_fbref:
        df_defensa_total = pd.concat(datos_defensa_fbref, ignore_index=True)
        # Eliminamos duplicados quedándonos con el primer registro de cada jugador
        df_defensa_total = df_defensa_total.drop_duplicates(subset=['player_name_limpio'], keep='first')
        
        print("  Cruzando los datos de Fbref con la base general...")
        # Hacemos el merge usando la columna limpia, trayendo solo la columna de tackles
        df_combinado = pd.merge(df_base, df_defensa_total[['player_name_limpio', 'tackles']], on='player_name_limpio', how='left')
        df_combinado['tackles'] = df_combinado['tackles'].fillna(0)
        return df_combinado
    else:
        print("\n⚠️ No se pudieron obtener datos de Fbref. Se devolverá la base original.")
        df_base['tackles'] = 0
        return df_base

def main():
    print("🚀 INICIANDO PIPELINE DE SCOUTING (EPL, BUNDESLIGA, SERIE A, LIGUE 1)...")
    
    # 1. Base Understat
    df_base = obtener_datos_understat(temporada="2025")
    if df_base is None:
        return
        
    # 2. Defensa FBRef
    df_final = obtener_defensa_fbref(df_base, temporada_fbref="2025-2026")
    
    # --- LIMPIEZA FINAL DE COLUMNAS ---
    # Eliminamos la columna de nombres limpios que usamos solo para los cruces
    if 'player_name_limpio' in df_final.columns:
        df_final.drop(columns=['player_name_limpio'], inplace=True)
        
    # Eliminamos posibles duplicados exactos generados por los cruces
    df_final = df_final.drop_duplicates(subset=['player_name', 'League'])
    
    # 3. Guardar archivo
    archivo_salida = "data_output/Estadisticas_Jugadores.csv"
    df_final.to_csv(archivo_salida, encoding="utf-8-sig", index=False)
    print(f"\n🎉 ¡PROCESO FINALIZADO! Base de datos maestra guardada en: {archivo_salida}")

# Punto de entrada del script
if __name__ == "__main__":
    main()