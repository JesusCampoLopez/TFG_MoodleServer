# TFG_MoodleServer
Trabajo de Fin de Grado de Jesús Campo López

Este repositorio contiene una extensión de la libreria MoodleTeacher, la cual se ha utilizado para crear diferentes funciones para manipular y poder descargar, subir o actualizar calificaciones en un servidor de Moodle, gracias a los Web Services. Encontramos dos ficheros principales, entregas y hojacalificaciones, los cuales contienen las principales funciones que van a ser utilizadas con el fin de subir las calificaciones de los alumnos sobre una tarea en Moodle.

A su vez, tenemos dos scripts de python que hacen uso de estas diferentes funciones para dos casos de uso distintos. En primer lugar tenemos 'PruebaGeneral', enfocado en el caso de uso de una tarea del Moodle cuya evaluación sea única, es decir, que no se va a modificar. Y en último lugar tenemos 'PruebaModificaciones', el cual está orientado a una tarea en la cual la evaluación será continúa ya que los alumnos podrán modificar la entrega.

Explicación de los ficheros:

**'entregas.py'**

Librerias que requiere: sys, os, csv, datetime, re, subprocess, json, pathlib

Este fichero python contiene todas las funciones relacionadas con las entregas, desde descargarlas hasta comprobar si existen modificaciones en las mismas.

***descargaTodas:*** Esta función descarga las entregas sobre una tarea de todos los usuarios.

***descargaPorUsuario:*** Descarga la entrega sobre una tarea de un unico usuario que se pasa como parámetro

***existenModificaciones:*** Comprueba si han habido modificaciones en una entrega de un usuario y devuelve 'true' si se necesita recalificar la entrega.


**'hojaCalificaciones.py'**


Librerias que requiere: sys, os, pathlib, re, shutil

Este fichero python contiene todas las funciones relacionadas con las hojas de calificaciones, tanto para descargarlas desde el servidor Moodle,
como subir notas al mismo Servidor desde estas hojas de calificaciones.

***calculaMes***: Se trata de una función complementaria, la cual devuelve el nombre del dia del mes, a partir de un nobre dado en inglés

***calculaDia***: Se trata de una función complementaria, la cual devuelve el nombre del dia de la semana, a partir de un numero del 0 al 6

***subirNota***: Función que sube la calificación de un alumno a una tarea del servidor Moodle, así como el feedback correspondiente

***descarga***: Descarga la hoja de calificaciones correspondiente a la tarea pasada como parametro

***subir***: Sube las calificaciones al seervidor de Moodle a partir de la hoja de calificaciones, a todos los alumnos cuyas notas esten anotadas en la propia hoja de calificaciones, junto a su feedback correspondiente

***apuntarNotas***: Anota las notas de los alumnos en una hoja de calificaciones a partir de un diccionario que contiene la tupla id del usuario y su calificacion


**PRUEBAS**
Como se ha explicado previamente, encontramos dos pruebas diferentes, las cuales se explican a continuación:

***PruebaGeneral.py***: En este script de python se realiza un proceso el cual descarga todas las entregas de una misma tarea de un curso del servidor Moodle al cual nos conectamos, posteriormente descarga las hojas de calificaciones, aplica una herramienta de ejemplo la cual califica cada una de las entregas y genera ficheros de retroalimentacio los cuales se guardan en directorios específicos, anota dichas calificaciones en la hoja de calificaciones previamente descargada y por último sube las calificaciones y los ficheros de retroalimentacion al servidor de Moodle a partir de la hoja de calificaciones. Este proceso se realiza tan solo una vez, por lo que está enfocado a tareas las cuales sean de evaluación única, es decir, que las calificaciones de los alumnos en dichas tareas serán definitivas y no se admitirán modificaciones.

***PruebaModificaciones.py***: En este script de python se corre un bucle constante en el cual se comprrueba una a una cada entrega de todos los alumnos sobre una misma tarea de Moodle y se revisa si existe alguna modificación en la misma, en caso de haber alguna modificación, se descarga la nueva entrega de ese alumno, se vuelve a calificar en este caso con nuestra herramienta de ejemplo, y posteriormente se actualiza su calificación en el servidor Moodle. Estas comprobaciones se realizan cada periodo de 30 segundos. El enfoque de este script es para utilizarlo en tareas las cuales sean de evaluación continua, es decir, que los alumnos puedan modificar sus entregas y volver a recibir una nueva calificación.


