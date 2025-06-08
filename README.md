Autor: Obryan Mazariegos
Calculadora de Métodos Numéricos

Descripción: Una aplicación web desarrollada con Django para calcular raíces de funciones utilizando los métodos de Bisección, Newton-Raphson y Newton-Raphson Modificado.

Características:
* Implementación de métodos de Bisección, Newton-Raphson y Newton-Raphson Modificado métodos.
* Generación de gráficas de la función y la raíz.
* Visualización de la tabla de iteraciones.
* Almacenamiento de cálculos en base de datos.
Tecnologías: Python, Django, HTML, CSS y javascript.

Instalación:
Clonar el repositorio.
Crear y activar un entorno virtual.
Instalar dependencias (pip install -r requirements.txt).
Configurar la base de datos (python manage.py migrate).

Uso:
Iniciar el servidor (python manage.py runserver).
Navegar a la URL principal.
Seleccionar el método deseado.
Introducir la función y los parámetros.
Hacer clic en "Calcular".

Estructura del Proyecto:
Raíz del proyecto:
En la base de todo, esta la carpeta pricipal del mi proyecto Djang, que se llama mysite, dentro de ella 
se encuentra manage.py, que es la herramienta clave para iteractuar con Django, también esta el archivo
settings.py que contine los ajustes generales y urls.py principal que enruta todas las solicitudes web.

La aplicación myapp
Esta aplicación esta dedicada especificamente a la lógica de los métodos numéricos. Dentro de ella se 
encuentran los siguientes archivos importantes:

* static/: Esta carpeta es fundamental para el diseño y la interactividad de mi aplicación, contiene todos
los archivos estáticos que el navegador necesita para renderizar la pagina.
* templates/: Aquí estan todas las plantillas HTML, estas son las páginas web que el usuario ve.
* forms.py: Aqui se define las clases de fomularios HTML, para manejar la entrada de datos del usuario.
* models.py: Aqui se define la estructura de los datos, es decir, las tablas de la base de datos para
almacenar cada cálculo realizado.
* views.py: Aqui es donde se realiza toda la lógica de los métodos númeriocs, procesa el formulario,
interactúa con la base de datos (models.py) y renderiza las plantilas (templates/) para  mostrar los resultados,
incluyendo la raíz aproximada, el númeor de iteraciones, la gráfica y las tablas de iteraciones.  

