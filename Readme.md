🏆 Proyecto de Automatización y Almacenamiento de Datos de Fútbol

📋 Descripción del Proyecto

Este proyecto forma parte de una actividad colaborativa cuyo objetivo es automatizar la recopilación, almacenamiento y gestión de datos obtenidos desde fuentes oficiales.
Actualmente, el sistema obtiene información actualizada sobre dos ligas de fútbol utilizando la API pública de ESPN:

✔ LaLiga (España)
✔ Premier League (Inglaterra)

Los datos se almacenan en una base de datos SQLite para su posterior análisis y visualización.

El proyecto consta de un proceso automatizado que:

- Consulta datos de clasificación de equipos desde una API.

- Limpia y organiza los datos obtenidos.

- Los almacena en una base de datos estructurada (soccer.db) para su posterior análisis.

- Genera gráficas comparativas de goles a favor y en contra por liga (funcionalidad extra).

🎯 Objetivos del Proyecto

▪ Automatizar la obtención de datos desde una fuente contrastada (API de ESPN).

▪ Diseñar una estructura de base de datos relacional para almacenar la información.

▪ Implementar funciones de inserción y actualización de datos en SQLite.

▪ Trabajar de forma colaborativa con control de versiones mediante GitHub.

🧩 Estructura del Proyecto

📂 Obtencion-Almacenamiento-Datos
├── main.py		# Script principal que obtiene y procesa los datos de varias ligas
├── db.py		# Módulo encargado de la gestión de la base de datos
├── soccer.db		# Base de datos SQLite donde se almacenan los datos
└── Readme.md		# Documento de descripción del proyecto

⚙️ Funcionamiento

1. Obtención de datos (main.py)

El script realiza una solicitud HTTP a la API de ESPN para obtener información sobre la clasificación de los equipos de LaLiga y la Premier League:

ligas_urls = {
    "LaLiga": "https://site.web.api.espn.com/apis/v2/sports/soccer/esp.1/standings",
    "Premier League": "https://site.web.api.espn.com/apis/v2/sports/soccer/eng.1/standings"
}

Posteriormente:

Extrae estadísticas relevantes (partidos jugados, victorias, derrotas, puntos, etc.).

Estructura los datos en un diccionario.

Inserta o actualiza la información en la base de datos mediante funciones del módulo db.py.

Genera gráficas separadas para cada liga mostrando goles a favor y en contra por equipo.

2. Gestión de la base de datos (db.py)

El módulo db.py se encarga de:

Crear las tablas (league, teams, stats).

Insertar nuevas ligas y equipos.

Actualizar estadísticas de los equipos.

Evitar duplicación de registros mediante verificaciones previas.

Las tablas tienen las siguientes estructuras:

==========================
      Tabla: league
==========================
| id |   name   |  year  |
|----|----------|--------|
|  1 |  LaLiga  |  2024  |
==========================


=================================================================
						Tabla: teams
=================================================================
|	id	|		name		|		logo		| 	league_id	|
|-------|-------------------|-------------------|---------------|
|	1	|	Real Madrid	    |  	 https://...	|	    1		|
=================================================================


==================================================================================================
        								Tabla: stats
==================================================================================================
| id | team_id  | points | played | goals_against | goals_for | wins | draws | losses | position |
|----|----------|--------|--------|---------------|-----------|------|-------|--------|----------|
|  1 |    1     |   85   |   38   |       30      |     70    |  27  |   4   |    7   |     1    |
==================================================================================================


🧠 Tecnologías Utilizadas

+ Python 3

+ SQLite3

+ Requests (para acceder a la API)

+ JSON (para estructurar la respuesta de la API)

+ Matplotlib (para generar gráficas)

+ GitHub (para control de versiones y trabajo colaborativo)


🚀 Ejecución del Proyecto

1. Clonar el repositorio

git clone https://github.com/4drian04/Obtencion-Almacenamiento-Datos.git
cd proyecto_futbol

2. Instalar dependencias

pip install requests matplotlib

3. Ejecutar el script principal

python main.py


Esto creará (si no existe) la base de datos soccer.db y almacenará los datos obtenidos desde la API.


📊 Funcionalidades Extra

- Generación de gráficas por liga (goles a favor y en contra).

- Soporte para múltiples ligas (actualmente LaLiga y Premier League).


📈 Posibles Ampliaciones

+ Agregar más fuentes de datos:

	- Otras ligas (liga alemana, argentina, etc.)

+ Automatizar la actualización periódica mediante tareas programadas.

+ Ampliar el modelo de datos para incluir jugadores y estadísticas individuales.

+ Permitir el histórico de datos para mantener los datos de años y temporadas anteriores.


👥 Autores


Proyecto desarrollado por Adrián García García, David Caraballo Bulnes, Pablo Baeza Gómez, Eva María García Gálvez.
