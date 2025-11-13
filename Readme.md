🏆 Proyecto de Automatización y Almacenamiento de Datos de Fútbol

📋 Descripción del Proyecto

Este proyecto forma parte de una actividad colaborativa cuyo objetivo es automatizar la recopilación, almacenamiento y gestión de datos obtenidos desde fuentes oficiales.
En este caso, se ha implementado un sistema que obtiene información actualizada sobre la Liga Española de Fútbol (LaLiga) utilizando la API pública de ESPN, y la almacena en una base de datos SQLite.

El proyecto consta de un proceso automatizado que:

- Consulta datos de clasificación de equipos desde una API.

- Limpia y organiza los datos obtenidos.

- Los almacena en una base de datos estructurada (soccer.db) para su posterior análisis.

🎯 Objetivos del Proyecto

Automatizar la obtención de datos desde una fuente contrastada (API de ESPN).

Diseñar una estructura de base de datos relacional para almacenar la información.

Implementar funciones de inserción y actualización de datos en SQLite.

Trabajar de forma colaborativa con control de versiones mediante GitHub.

🧩 Estructura del Proyecto

📂 Obtencion-Almacenamiento-Datos
├── main.py		# Script principal que obtiene y procesa los datos
├── db.py		# Módulo encargado de la gestión de la base de datos
├── soccer.db		# Base de datos SQLite donde se almacenan los datos
└── Readme.md		# Documento de descripción del proyecto

⚙️ Funcionamiento

1. Obtención de datos (main.py)

El script realiza una solicitud HTTP a la API de ESPN para obtener información sobre la clasificación de los equipos de LaLiga:

r = requests.get("https://site.web.api.espn.com/apis/v2/sports/soccer/esp.1/standings").json()


Posteriormente:

Extrae estadísticas relevantes (partidos jugados, victorias, derrotas, puntos, etc.).

Estructura los datos en un diccionario.

Inserta o actualiza la información en la base de datos mediante funciones del módulo db.py.


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

+ GitHub (para control de versiones y trabajo colaborativo)


🚀 Ejecución del Proyecto

1. Clonar el repositorio

git clone https://github.com/4drian04/Obtencion-Almacenamiento-Datos.git
cd proyecto_futbol

2. Instalar dependencias

pip install requests

3. Ejecutar el script principal

python main.py


Esto creará (si no existe) la base de datos soccer.db y almacenará los datos obtenidos desde la API.


📊 Posibles Ampliaciones

+ Agregar más fuentes de datos:

	- Otras ligas (Liga inglesa, alemana, argentina...)

+ Automatizar la actualización periódica mediante tareas programadas.

+ Crear una interfaz o dashboard para visualizar los datos.

+ Ampliar el modelo de datos para incluir jugadores y estadísticas individuales.

+ Permitir el histórico de datos para mantener los datos de años y temporadas anteriores.


👥 Autores

Proyecto desarrollado por Adrián García García, David Caraballo Bulnes, Pablo Baeza Gómez, Eva María García Gálvez.