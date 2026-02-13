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

📊 Gráficas y análisis

- En primer lugar, vemos una gráfica donde podemos ver las victorias y los empates de cada liga
  
  <img width="1520" height="781" alt="newplot" src="https://github.com/user-attachments/assets/9c68af12-fb67-4ce1-bd72-fcd6b74eae89" />

  Podemos ver que en la Serie A es donde más empates hay, mientras que en la Bundesliga es donde menos empates hay. La Premier y LALIGA es un término medio, aunque la diferencia entre todas no es tan grande
  En cuanto a las victorias, la Bundesliga es donde más victorias hay (debido a que tienen menos empates), luego le sigue LALIGA.
  De esto podemos decir que la Bundesliga tiene más partidos decisivos (menos empates), donde los partidos son más ofensivos, mientras que la Serie A los equipos, es posible que jueguen con un bloque defensivo     mayor. La liga en el que podemos decir que hay un equilibrio entre el bloque defensivo y ofensivo es en la Premier, ya que su porcentaje de victorias y empates son muy parejos

- Luego, podemos ver una gráfica donde observamos la correlación entre los goles de diferencia y los puntos por partido de cada equipo de cuatro ligas distintas

  <img width="1520" height="781" alt="newplot" src="https://github.com/user-attachments/assets/1cf59d8a-0e35-439e-853d-4c9429554ee5" />

  En esta gráfica podemos ver que, cuanto mayor son los goles de diferencia, mayor son los puntos por partido, pero lo interesante de esta gráfica es mirar en ciertos sectores de la gráfica donde hay equipos que   tienen el mismo gol de diferencia pero hay algunos que tienen menos puntos por goles que otros. Un ejemplo que podemos ver en la gráfica es el Espanyol y el Elche, donde ambos tienen los mismos goles de          diferencia, pero el Espanyol tiene más puntos por partidos que el Elche, esto se pueden llamar casos "injustos", pero podemos deducir que existe la posibilidad de que el Elche ha perdido muchos partidos por un   gol de diferencia y en otros partidos ha metido muchos goles a favor, mientras que el Espanyol ha ganado muchos partidos por un gol de diferencia, y en otros pocos haya perdido por 2-3 goles en contra, de esta   forma ambos tienen los mismos goles de diferencia, pero el Espanyol más puntos por partidos

- Por otro lado, podemos ver una <a href="https://davidcaraballobulnes.github.io/Data-Preparation-ESPN-Soccer/">gráfica donde se compara los goles a favor y en contra de cada equipo</a>

  <img width="1520" height="781" alt="newplot" src="https://github.com/user-attachments/assets/cfb11dff-49e3-4ff2-9971-81bb1c199123" />

  La gráfica esta dividida en diferentes secciones, para ello he obtenido la media de los goles a favor y en contra y con esas medias he añadidos las líneas que separan en diferentes sectores. Podemos visualizar   los equipos que tienen mala/buena defensa y mal/buen ataque. Viendo las diferentes secciones, podemos ver que la liga que tiene mejores ataques es la Premier, donde diez equipos se encuentran en la parte de la   derecha (donde se encuentran los equipos con mejores ataques), luego le sigue la Bundesliga con 9 equipos, mientras que el equipo que tienen menos equipos en la sección de buenos ataques es la Serie A. Por       otro lado, las ligas con mejores defensas es LALIGA y la Serie A con 11 equipos en la parte inferior donde se encuentran los equipos con mejores defensas. La liga que peor defensa tiene según la gráfica es la    Bundesliga, donde tiene solo 7 equipos con buenos defensas, y 4 de ellos se encuentran muy cerca de la frontera, por lo que si la media cambia, podrían cambiar de sección

- Por otra parte, podemos observar esta gráfica, que nos muestra el promedio de goles en contra por liga

  <img width="1520" height="781" alt="newplot" src="https://github.com/user-attachments/assets/fe498ef7-3727-459d-a6a5-c00011f6ba09" />

  Podemos observar que, donde más goles encajados hay es en la Bundesliga, superando por mucho el promedio total de los goles encajados de las 4 ligas estudiadas. Esto nos hace ver que lo analizado anteriormente   (Bundesliga peores defensas y menos empates) tenga sentido, ya que tiene más goles encajados. Por otro lado, la liga que menos goles encajados tiene es la Serie A, que relacionado con gráficas anteriores         podemos concluir que tiene sentido, ya que es la liga que más empates hay y menos equipos tienen buen ataque. En cuanto a LALIGA y la Premier League, podemos ver que siguen un equilibro, aunque la Premier        supera por poco la media global de goles encajados
  
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

python mainV2.py
👥 Autores


Proyecto desarrollado por Adrián García García, David Caraballo Bulnes.









