import requests
import db
import matplotlib.pyplot as plt

r = requests.get("https://site.web.api.espn.com/apis/v2/sports/soccer/esp.1/standings").json()

# Se indica las estadísticas que queremos guardar en la base de datos
estadisticas = ["gamesPlayed", "losses", "pointDifferential", "points", "pointsAgainst", "pointsFor", "ties", "rank", "wins"]
# Queremos guardar en una lista la liga y el año, los goles a favor y en contra (para hacer posteriormente una gráfica) y la lista de equipos
liga = []
golesAFavor = []
golesEnContra = []
listaEquipos = []
equipos = {"equipos": {}}
liga.append(r["abbreviation"]) # Añadimos el nombre de la liga y el año
liga.append(r["children"][0]["abbreviation"])
for equipo in r["children"][0]["standings"]["entries"]: # Recorremos todos los equipos de la liga para obtener sus atributos
    nombreEquipo = equipo["team"]["name"] # Obtenemos el nombre
    equipos["equipos"][nombreEquipo] = {}
    equipos["equipos"][nombreEquipo]["nombre"] = equipo["team"]["name"] # Obtenemos y guardamos el nombre del equipo
    equipos["equipos"][nombreEquipo]["league"] = liga[0] # Guardamos la liga en el diccionario
    equipos["equipos"][nombreEquipo]["logo"] = equipo["team"]["logos"][0]["href"] # Obtenemos y guardamos el logo del equipo
    equipos["equipos"][nombreEquipo]["estadisticas"] = {} # Creamos u diccionario dentro de estadisticas para guardar las estadísticas
    listaEquipos.append(nombreEquipo) # Guardamos el nombre del equipo para poder mostrarlo luego en la gráfica
    for estadistica in equipo["stats"]: # Recorremos las estadísticas del equipo
        if estadistica["name"] in estadisticas: # Si el nombre de las estadísticas se encuentran dentro del array creado anteriormente, obtendremos dicha estadística
            equipos["equipos"][nombreEquipo]["estadisticas"][estadistica["name"]] = int(estadistica["value"]) # Guardamos el nombre de la estaadística y el valor
            if estadistica["name"] == "pointsFor": # Si el nombre es pontsFor (goles a favor), lo guardamos en la lista de goles a favor
                golesAFavor.append(int(estadistica["value"]))
            elif estadistica["name"] == "pointsAgainst": # Si es pointsAgainst (goles en contra), lo guardamos en la lista de goles en contra
                golesEnContra.append(int(estadistica["value"]))

db.create_tables() # Creamos las tablas correspondientes
db.insert_leagues(liga) # Insertamos la liga
db.insert_teams(list(equipos.values())[0]) # Insertamos los equipos correspondiente obtenido anteriormente


plt.barh(listaEquipos, golesAFavor, color='skyblue') # Creamos la gráfica para los goles a favor, ponemos en el eje y los equipos y en el eje x los goles (si pongo los equipos en el eje x, no caben cuando se minimiza la gráfica)
plt.xlabel('Goles a favor') # Se pone un título al eje x
plt.ylabel('Equipos') # Un título al eje y
plt.title('Goles a favor de los equipo de la liga') # Un título para la gráfica
plt.show() # Se muestra

plt.barh(listaEquipos, golesEnContra, color='skyblue') # En este caso hacemos lo mismo pero para los goles en contra
plt.xlabel('Goles en contra')
plt.ylabel('Equipos')
plt.title('Goles en contra de los equipo de la liga')
plt.show()