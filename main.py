import requests
import db
import matplotlib.pyplot as plt

# Definimos las ligas que queremos consultar
ligas_urls = {
    "LaLiga": "https://site.web.api.espn.com/apis/v2/sports/soccer/esp.1/standings",
    "Premier League": "https://site.web.api.espn.com/apis/v2/sports/soccer/eng.1/standings",
    "Serie A": "https://site.web.api.espn.com/apis/v2/sports/soccer/ita.1/standings",
    "Bundesliga": "https://site.web.api.espn.com/apis/v2/sports/soccer/ger.1/standings"
}

# Se indica las estadísticas que queremos guardar en la base de datos
estadisticas = ["gamesPlayed", "losses", "pointDifferential", "points", "pointsAgainst", "pointsFor", "ties", "rank", "wins"]

# Recorrer cada liga
for nombre_liga, url in ligas_urls.items():
    r = requests.get(url).json()
    
    # De cada liga queremos guardar en una lista la liga y el año, los goles a favor y en contra (para hacer posteriormente una gráfica) y la lista de equipos
    liga = []
    golesAFavor = []
    golesEnContra = []
    listaEquipos = []
    equipos = {"equipos": {}}
    
    liga.append(r["abbreviation"]) # Añadimos el nombre de la liga y el año
    liga.append(r["children"][0]["abbreviation"])

    # Procesar equipos
    for equipo in r["children"][0]["standings"]["entries"]: # Recorremos todos los equipos de la liga para obtener sus atributos
        nombreEquipo = equipo["team"]["name"] # Obtenemos el nombre
        equipos["equipos"][nombreEquipo] = {}
        equipos["equipos"][nombreEquipo]["nombre"] = equipo["team"]["name"] # Obtenemos y guardamos el nombre del equipo
        equipos["equipos"][nombreEquipo]["league"] = liga[0] # Guardamos la liga en el diccionario
        equipos["equipos"][nombreEquipo]["logo"] = equipo["team"]["logos"][0]["href"] # Obtenemos y guardamos el logo del equipo
        equipos["equipos"][nombreEquipo]["estadisticas"] = {} # Creamos un diccionario dentro de estadisticas para guardar las estadísticas
        listaEquipos.append(nombreEquipo) # Guardamos el nombre del equipo para poder mostrarlo luego en la gráfica
        
        for estadistica in equipo["stats"]: # Recorremos las estadísticas del equipo
            if estadistica["name"] in estadisticas: # Si el nombre de las estadísticas se encuentran dentro del array creado anteriormente, obtendremos dicha estadística
                equipos["equipos"][nombreEquipo]["estadisticas"][estadistica["name"]] = int(estadistica["value"]) # Guardamos el nombre de la estadística y el valor
                if estadistica["name"] == "pointsFor": # Si el nombre es pointsFor (goles a favor), lo guardamos en la lista de goles a favor
                    golesAFavor.append(int(estadistica["value"]))
                elif estadistica["name"] == "pointsAgainst": # Si es pointsAgainst (goles en contra), lo guardamos en la lista de goles en contra
                    golesEnContra.append(int(estadistica["value"]))

    db.create_tables() # Creamos las tablas correspondientes
    db.insert_leagues(liga) # Insertamos la liga
    db.insert_teams(list(equipos.values())[0]) # Insertamos los equipos correspondientes obtenidos anteriormente

    # Gráficas por liga
    plt.barh(listaEquipos, golesAFavor, color='skyblue') # Creamos la gráfica para los goles a favor
    plt.xlabel('Goles a favor') # Se pone un título al eje x
    plt.ylabel('Equipos') # Un título al eje y
    plt.title(f'Goles a favor de los equipos en {nombre_liga}') # Un título para la gráfica con el nombre de la liga
    plt.show() # Se muestra

    plt.barh(listaEquipos, golesEnContra, color='tomato') # Creamos la gráfica para los goles en contra
    plt.xlabel('Goles en contra')
    plt.ylabel('Equipos')
    plt.title(f'Goles en contra de los equipos en {nombre_liga}') # Un título para la gráfica con el nombre de la liga
    plt.show()