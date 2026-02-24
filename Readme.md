<h1 align="center">🏆 Análisis y Automatización de Datos Futbolísticos</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Polars-000000?style=for-the-badge&logo=polars&logoColor=white" alt="Polars">
  <img src="https://img.shields.io/badge/Plotly-239120?style=for-the-badge&logo=plotly&logoColor=white" alt="Plotly">
</p>

<p align="center">
  <strong>Un proyecto automatizado para la extracción, almacenamiento y visualización de métricas deportivas utilizando la API de ESPN.</strong>
</p>

---

## 📋 Descripción del Proyecto

Este proyecto forma parte de una iniciativa colaborativa orientada a crear un flujo de trabajo completo de datos (*Data Pipeline*). El sistema automatiza la recopilación, limpieza, almacenamiento y gestión de estadísticas en tiempo real de las principales ligas europeas de fútbol:

* 🇪🇸 **LaLiga** (España)
* 🇬🇧 **Premier League** (Inglaterra)
* 🇮🇹 **Serie A** (Italia)
* 🇩🇪 **Bundesliga** (Alemania)

Los datos se estructuran en una base de datos relacional para alimentar posteriores análisis exploratorios (EDA) y cuadros de mando interactivos.

## 🎯 Objetivos

1.  **Automatización:** Extraer datos actualizados desde una fuente oficial (API de ESPN) sin intervención manual.
2.  **Ingeniería de Datos:** Diseñar y mantener una base de datos SQLite estructurada e íntegra.
3.  **Procesamiento Eficiente:** Utilizar Polars para una limpieza y filtrado de datos de alto rendimiento.
4.  **Data Storytelling:** Generar visualizaciones claras que permitan extraer conclusiones tácticas y estadísticas sobre los equipos y ligas.

---

## ⚙️ Arquitectura y Funcionamiento

El flujo del proyecto se divide en las siguientes fases metodológicas:

1.  **Extracción (ETL - Extract):** El script `main.py` realiza peticiones HTTP a los endpoints de la API de ESPN, descargando las clasificaciones y estadísticas crudas en formato JSON.
2.  **Almacenamiento (ETL - Load):** Mediante el módulo `db.py`, la información se procesa y se realiza un *Upsert* (inserción o actualización) en la base de datos relacional `soccer.db`.
3.  **Procesamiento (ETL - Transform):** Para el análisis, utilizamos la función `read_database_uri` de **Polars**. Lanzamos consultas SQL directas para generar DataFrames rápidos y optimizados.
4.  **Filtrado Modular:** A partir del DataFrame maestro, aplicamos métodos `.drop()` y filtros específicos para aislar las variables exactas necesarias para cada visualización, optimizando el consumo de memoria.

<details>
<summary>📂 Ver estructura de directorios</summary>

Obtencion-Almacenamiento-Datos/
├── main.py                         # Script principal (Web Scraping / API requests)
├── carga_datos.py                  # Carga los datos de las diferentes ligas e inserta los datos de los distintos jugadores
├── carga_datos_jugadores.py        # Obtiene los datos de todos los jugadores de las diferentes ligas (Scraping)
├── db.py                           # Gestión y conexión con SQLite
├── soccer.db                       # Base de datos relacional
├── README.md                       # Documentación
└── graficos/                       # HTMLs interactivos generados por Plotly

</details>

---

## 📊 Visualizaciones y Análisis de Datos

> 💡 **Nota:** Haz clic en los títulos de cada gráfico para abrir la **versión interactiva** alojada en GitHub Pages.

- En primer lugar, tenemos un gráfico que representa la <a href="https://davidcaraballobulnes.github.io/Data-Preparation-ESPN-Soccer/graficos/Media_Goles_Partido_Ligas.html">media de goles por partido en cada liga</a>

    <img width="1262" height="1254" alt="Media_Goles_Partido_Ligas" src="https://github.com/user-attachments/assets/948addbe-a311-4682-8f16-116682134143" />

  Podemos ver que la liga en la que se marcan más goles es la Bundeliga (la liga alemana) y la liga en que menos goles se marcan es la Serie A (la liga italiana). Esto puede indicar que en la liga alemana hay mejores delanteros o que en la liga italiana hay mejores defensas y porteros.

- Parecido al gráfico anterior, tenemos la <a href="https://davidcaraballobulnes.github.io/Data-Preparation-ESPN-Soccer/graficos/Media_Puntos_Partidos_Ligas.html">media de puntos por partido en cada liga</a>

  <img width="1262" height="1254" alt="Media_Puntos_Partidos_Ligas" src="https://github.com/user-attachments/assets/042fee63-532f-4780-b15d-63f535702397" />

  Concluimos que está muy reñida la cosa en cuestión de puntos. En todas las ligas se suelen sacar en torno a 1,4 puntos por partido, esto indica que se empata más de lo que se gana.

- A continuación, vemos una <a href="https://davidcaraballobulnes.github.io/Data-Preparation-ESPN-Soccer/graficos/Victorias_Empates_Por_Liga.html">gráfica donde podemos ver las victorias y los empates de cada liga</a>

  <img width="1520" height="781" alt="newplot" src="https://github.com/user-attachments/assets/9c68af12-fb67-4ce1-bd72-fcd6b74eae89" />

  Podemos ver que en la Serie A es donde más empates hay, mientras que en la Bundesliga es donde menos empates tiene. La Premier y LALIGA es un término medio, aunque la diferencia entre todas no es tan grande.

  En cuanto a las victorias, la Bundesliga es donde más victorias hay (debido a que tienen menos empates), luego le sigue LALIGA.

  De esto podemos decir que la Bundesliga tiene más partidos decisivos (menos empates), donde los partidos son más ofensivos, mientras que la Serie A los equipos, es posible que jueguen con un bloque defensivo     mayor. La liga en el que podemos decir que hay un equilibrio entre el bloque defensivo y ofensivo es en la Premier, ya que su porcentaje de victorias y empates son muy parejos.

- Luego, podemos ver una <a href="https://davidcaraballobulnes.github.io/Data-Preparation-ESPN-Soccer/graficos/Equipos_Eficientes_GD_Puntos_Por_Partido.html">gráfica donde observamos la correlación entre los goles de diferencia y los puntos por partido de cada equipo de        cuatro ligas distintas</a>

  <img width="1520" height="781" alt="newplot" src="https://github.com/user-attachments/assets/416d18b3-975d-4405-9ad7-669709129ab0" />

  En esta gráfica podemos ver que, cuanto mayor son los goles de diferencia, mayor son los puntos por partido, pero lo interesante de esta gráfica es mirar en ciertos sectores de la gráfica donde hay equipos que   tienen el mismo gol de diferencia pero hay algunos que tienen menos puntos por goles que otros. Un ejemplo que podemos ver en la gráfica es el Espanyol y el Elche, donde ambos tienen los mismos goles de          diferencia, pero el Espanyol tiene más puntos por partidos que el Elche, esto se pueden llamar casos "injustos", pero podemos deducir que existe la posibilidad de que el Elche ha perdido muchos partidos por un   gol de diferencia y en otros partidos ha metido muchos goles a favor, mientras que el Espanyol ha ganado muchos partidos por un gol de diferencia, y en otros pocos haya perdido por 2-3 goles en contra, de esta   forma ambos tienen los mismos goles de diferencia, pero el Espanyol más puntos por partidos.

- Por otro lado, podemos ver una <a href="https://davidcaraballobulnes.github.io/Data-Preparation-ESPN-Soccer/graficos/Ataques_vs_Defensas_Por_Equipo.html">gráfica donde se compara los goles a favor y en contra de cada equipo</a>

  <img width="1520" height="781" alt="newplot" src="https://github.com/user-attachments/assets/2a2c5053-db2c-485f-baaf-1afa6e8d9937" />

  La gráfica esta dividida en diferentes secciones, para ello he obtenido la media de los goles a favor y en contra y con esas medias he añadidos las líneas que separan en diferentes sectores. Podemos visualizar   los equipos que tienen mala/buena defensa y mal/buen ataque. Viendo las diferentes secciones, podemos ver que la liga que tiene mejores ataques es la Premier, donde diez equipos se encuentran en la parte de la   derecha (donde se encuentran los equipos con mejores ataques), luego le sigue la Bundesliga con 9 equipos, mientras que el equipo que tienen menos equipos en la sección de buenos ataques es la Serie A. Por       otro lado, las ligas con mejores defensas es LALIGA y la Serie A con 11 equipos en la parte inferior donde se encuentran los equipos con mejores defensas. La liga que peor defensa tiene según la gráfica es la    Bundesliga, donde tiene solo 7 equipos con buenos defensas, y 4 de ellos se encuentran muy cerca de la frontera, por lo que si la media cambia, podrían cambiar de sección.

- Por otra parte, podemos observar esta gráfica, que nos muestra el <a href="https://davidcaraballobulnes.github.io/Data-Preparation-ESPN-Soccer/graficos/Ligas_Mas_Defensivas.html">promedio de goles en contra por liga</a>

  <img width="1520" height="781" alt="newplot" src="https://github.com/user-attachments/assets/fe498ef7-3727-459d-a6a5-c00011f6ba09" />

  Podemos observar que, donde más goles encajados hay es en la Bundesliga, superando por mucho el promedio total de los goles encajados de las 4 ligas estudiadas. Esto nos hace ver que lo analizado anteriormente   (Bundesliga peores defensas y menos empates) tenga sentido, ya que tiene más goles encajados. Por otro lado, la liga que menos goles encajados tiene es la Serie A, que relacionado con gráficas anteriores         podemos concluir que tiene sentido, ya que es la liga que más empates hay y menos equipos tienen buen ataque. En cuanto a LALIGA y la Premier League, podemos ver que siguen un equilibro, aunque la Premier        supera por poco la media global de goles encajados.

- Luego pasamos a los datos de los jugadores, en este caso vemos los <a href="https://davidcaraballobulnes.github.io/Data-Preparation-ESPN-Soccer/graficos/Goles_Asistencias_Extremos.html">goles y asistencias de los mejores extremos del mundo</a>

  <img width="1520" height="781" alt="newplot" src="https://github.com/user-attachments/assets/fbaab59d-cb37-4efc-943c-9a42586033fd" />

  Vemos en un gráfico apilado tanto los goles, como las asistencias de los extremos del mundo, donde en primer lugar está Lamine Yamal, luego le sigue don Vinicius Junior y en tercer lugar Raphinha. A la derecha   podemos observar un gráfico Scatter, pero con los mismos datos, en el que cuanto más alto estes más asistencias tiene, y cuanto más a la derecha en el eje X más goles.

- Además, otro gráfico interesante que mirar acerca de los extremos son las <a href="https://davidcaraballobulnes.github.io/Data-Preparation-ESPN-Soccer/graficos/Faltas_Recibidas_Extremos.html">faltas recibidas por partidos</a>

  <img width="1520" height="781" alt="newplot" src="https://github.com/user-attachments/assets/5fbe9d89-6e90-425d-bb3c-43a958fe56bc" />

  Siendo extremo, los goles no son lo más importante, eso es trabajo del delantero centro, lo más importante jugando en esa posición son las asistencias y las faltas recibidas por partido, ya que eso quiere        decir que el extremo encara mucho, quizas sea un jugador rápido o rápido en conducción, por lo que es díficil de parar, a no ser que sea con faltas, de esta forma, se genera una ventaja al equipo que recibe la   falta. En este caso vemos que, don Vinicius Junior es el que más faltas recibe de todos los extremos analizados, siguiendole Lamine Yamal.


-  Ahora, vamos a ver un gráfico comparando la <a href="https://davidcaraballobulnes.github.io/Data-Preparation-ESPN-Soccer/graficos/Media_Edades_Equipos.html">edad media de la plantilla de cada equipo</a>
  

      <img width="1262" height="900" alt="Media_Edades_Equipos" src="https://github.com/user-attachments/assets/6266c267-a007-4049-a1fb-4f1d5e630fd7" />

      Podemos ver que el Chelsea tiene una media de edad de aproximadamente 22 años. Eso indica que dicho equipo tendrá asegurada la plantilla durante mínimo una década. Por otro lado, tenemos equipos como el Rayo Vallecano y el SC Freiburg, cuya media es de 27 años aproximadamente. Éstos deberán renovar la plantilla de manera más inmediata. 

-  Por último, tenemos un mapa geográfico representando los <a href="https://davidcaraballobulnes.github.io/Data-Preparation-ESPN-Soccer/graficos/Total_Goles_Nacionalidad.html">goles que han marcado los jugadores según su nacionalidad</a>

    <img width="1904" height="939" alt="newplot" src="https://github.com/user-attachments/assets/0af4b27e-196f-4bcd-9958-d43f9091c224" />

    En primer lugar, si nos fijamos en los goles totales, podemos observar que el país ganador es España con una clara diferencia, superando los 300 goles. Esto se debe, en su mayor parte, a la cantidad de jugadores de cada nacionalidad, teniendo éste  más de 400. También, destacan países como Alemania, Inglaterra y Francia, que, pese a tener la mitad de jugadores, han estado cerca. Sin embargo, si nos fijamos en la media de goles por número de jugadores, podemos ver que Canadá y Bosnia y Herzegovina tienen una gran media con respecto a los otros países

---

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3
* **Bases de Datos:** SQLite3
* **Procesamiento de Datos:** Polars
* **Peticiones API:** Requests, JSON
* **Visualización:** Plotly (Gráficos interactivos), Matplotlib
* **Control de Versiones:** Git & GitHub

---

## 🚀 Instalación y Ejecución

Sigue estos pasos para replicar el proyecto en tu entorno local:

1. **Clonar el repositorio:**
   git clone https://github.com/DavidCaraballoBulnes/Data-Preparation-ESPN-Soccer
   cd Data-Preparation-ESPN-Soccer

2. **Instalar las dependencias necesarias:**
   pip install requests matplotlib polars plotly

3. **Ejecutar el script de extracción (ETL):**
   python main.py
   *(Esto consultará la API y poblará/actualizará la base de datos `soccer.db`)*

---

## 👥 Autores

Desarrollado con 💻 y ⚽ por:
* **Adrián García García** - [GitHub](https://github.com/4drian04) | [LinkedIn](https://www.linkedin.com/in/adri%C3%A1n-garc%C3%ADa-garc%C3%ADa-6ab399333/)
* **David Caraballo Bulnes** - [GitHub](https://github.com/DavidCaraballoBulnes) | [LinkedIn](https://www.linkedin.com/in/david-caraballo-bulnes-791968239/)



