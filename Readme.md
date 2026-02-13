🏆 Proyecto de Automatización y Almacenamiento de Datos de Fútbol

📋 Descripción del Proyecto

Este proyecto forma parte de una actividad colaborativa cuyo objetivo es automatizar la recopilación, almacenamiento y gestión de datos obtenidos desde fuentes oficiales.
Actualmente, el sistema obtiene información actualizada sobre dos ligas de fútbol utilizando la API pública de ESPN:

✔ LaLiga (España)
✔ Premier League (Inglaterra)
✔ Serie A (Italia)
✔ Bundesliga (Alemania)

Los datos se almacenan en una base de datos SQLite para su posterior análisis y visualización.

El proyecto consta de un proceso automatizado que:

- Consulta datos de clasificación de equipos desde una API.

- Limpia y organiza los datos obtenidos.

- Los almacena en una base de datos estructurada (soccer.db) para su posterior análisis.

- Generar distintos gráficos que comentaremos posteriormente para hacer un análisis de ello y sacar conclusiones.

🎯 Objetivos del Proyecto

▪ Automatizar la obtención de datos desde una fuente contrastada (API de ESPN).

▪ Diseñar una estructura de base de datos relacional para almacenar la información.

▪ Realizar gráficos y hacer un análisis donde sacemos conclusiones claras.

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
    "Premier League": "https://site.web.api.espn.com/apis/v2/sports/soccer/eng.1/standings",
    "Serie A": "https://site.web.api.espn.com/apis/v2/sports/soccer/ita.1/standings",
    "Bundesliga": "https://site.web.api.espn.com/apis/v2/sports/soccer/ger.1/standings"
}

Posteriormente:

Extrae estadísticas relevantes (partidos jugados, victorias, derrotas, puntos, etc.).

Inserta o actualiza la información en la base de datos mediante funciones del módulo db.py.

2. Gestión de la base de datos (db.py)
   
3. Una vez guardada la información en la base de datos, en otro script hacemos una consulta SQL para obtener los datos necesarios que utilizaremos para crear gráficas y hacer análisis

4. Con la función 'read_database_uri' incluimos la consulta y el url de nuestra base de datos SQLITE, de esta froma, obtendremos un dataframe de Polars con la información importante, haciedno asi una limpieza rápida y efectiva

5. Luego, una vez tenemos el dataframe general, por cada gráfico que hagamos hacemos un '.drop' para reducir más el número de variables, ya que para hcer una gráfica u otra, necesitamos un número determinado de variables, por lo que vamos creando dataframes que nos servirá para realizar un análisis u otro

6. Una vez tengamos el dataframe en cuestión, creamos la gráfica correspondiete para hacer el análisis 

🧠 Tecnologías Utilizadas

+ Python 3

+ SQLite3

+ Requests (para acceder a la API)

+ JSON (para estructurar la respuesta de la API)

+ Matplotlib (para generar gráficas)

+ GitHub (para control de versiones y trabajo colaborativo)
  
+ Polars (nos permite guardar la información en DataFrames y generar gráficos)
  
+ Plotly (generar gráficas interactivas)

🚀 Ejecución del Proyecto

1. Clonar el repositorio

git clone https://github.com/4drian04/Obtencion-Almacenamiento-Datos.git
cd proyecto_futbol

2. Instalar dependencias

pip install requests matplotlib

3. Ejecutar el script principal

python main.py


Esto creará (si no existe) la base de datos soccer.db y almacenará los datos obtenidos desde la API.
👥 Autores


Proyecto desarrollado por Adrián García García, David Caraballo Bulnes, Pablo Baeza Gómez, Eva María García Gálvez.


