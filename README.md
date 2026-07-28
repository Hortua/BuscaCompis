

\# Buscacompis



Buscacompis es una aplicación que recomienda compañeros de estudio a partir de la

compatibilidad entre estudiantes, calculada con conceptos de matemáticas discretas

(conjuntos, relaciones y grafos). El sistema modela a cada estudiante como un

conjunto de materias, horario disponible y hobbies, calcula la similitud entre

estudiantes con el índice de Jaccard, y representa al grupo completo como un grafo

de compatibilidad sobre el cual se generan recomendaciones y se detectan grupos de

estudio.



Proyecto individual del curso Matemáticas Discretas I.



\## Integrante



\- Julián Camilo Hortúa Franco



\## Requisitos



\- Python 3.10 o superior

\- pip



\## Instalación





1\. Clona el repositorio:

```bash

&#x20;  git clone https://github.com/Hortua/BuscaCompis.git

&#x20;  cd BuscaCompis

```



2\. Instala las dependencias (debe hacerse desde la raíz del repositorio, donde está `requirements.txt`):

```bash

&#x20;  pip install -r requirements.txt

```



\## Ejecución



\*\*Importante:\*\* El programa usa una ruta relativa (`../data/estudiantes.csv`) para

leer los datos, por lo que es necesario ubicarse dentro de la carpeta `src/`

antes de ejecutar cualquiera de los siguientes comandos.



\### Interfaz interactiva 



```bash

cd src

streamlit run BuscaCompis.py

```



Esto abre la aplicación en el navegador, donde se puede visualizar el grafo,

agregar estudiantes, ajustar el umbral de compatibilidad y ver recomendaciones.



\### Notebook de desarrollo

> Si no tienes Jupyter instalado, puedes instalarlo con `pip install jupyter`.



```bash

cd src

jupyter notebook buscacompis.ipynb

```



El archivo `buscacompis.ipynb` contiene la lógica de cálculo desarrollada y

probada de forma aislada (Jaccard, construcción del grafo, análisis de

propiedades).



\## Ejemplo de uso



1\. Ejecuta la interfaz con `streamlit run BuscaCompis.py`.

2\. Selecciona un estudiante en el panel de "Recomendación de compañeros" para ver

&#x20;  sus tres compañeros más compatibles y qué tienen en común con cada uno.

3\. Ajusta el umbral de compatibilidad en la barra lateral para ver cómo cambia el

&#x20;  grafo (más o menos conexiones).

4\. Usa el formulario de la barra lateral para agregar un nuevo estudiante y ver

&#x20;  cómo se integra al grafo.



\## Datos



Los datos de ejemplo de los 20 estudiantes simulados están en `data/estudiantes.csv`,

con las columnas `id`, `nombre`, `carrera`, `materias`, `hobbies` y

`horario\_disponible` ; los tres últimos campos usan `;` como separador entre

valores. El archivo se carga automáticamente al iniciar la aplicación.



\## Pruebas y verificación



Las pruebas del proyecto están documentadas en el artículo técnico

(`docs/BuscaCompis.pdf`), sección "Pruebas y resultados", e incluyen:



\- Verificación del cálculo de compatibilidad con perfiles idénticos y opuestos.

\- Comparación del grafo generado con distintos umbrales (0.0 a 1.0).

\- Identificación de una limitación conocida en la normalización de datos de

&#x20; entrada (ver sección de Discusión del artículo).



Para reproducir estas pruebas manualmente, pueden ejecutarse las funciones

correspondientes (`suma\_ponderada`, `construir\_grafo`, `encontrar\_no\_transitividad`)

desde `buscacompis.ipynb` con los estudiantes de ejemplo del CSV.



\## Estructura del repositorio



```

BuscaCompis/

├── data/

│   └── estudiantes.csv

├── src/

│   ├── BuscaCompis.py

│   └── buscacompis.ipynb

├── docs/

│   └── BuscaCompis.pdf

├── requirements.txt

└── README.md

```

\## Estado actual del proyecto



El proyecto está funcional: cálculo de compatibilidad, construcción y análisis

del grafo, recomendaciones, detección de grupos de estudio (cliques), y

verificación de simetría/transitividad, todo integrado en una interfaz

interactiva con Streamlit. Como trabajo futuro, queda pendiente la normalización

de los datos de entrada (espacios y mayúsculas) y la posibilidad de cargar datos

reales de estudiantes.



