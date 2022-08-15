# TFG_MoodleServer
Trabajo de Fin de Grado de Jesús Campo López

Este repositorio contiene una extensión de la libreria MoodleTeacher, la cual se ha utilizado para crear diferentes funciones para manipular y poder descargar, subir o actualizar calificaciones en un servidor de Moodle, gracias a los Web Services. Encontramos dos ficheros principales, entregas y hojacalificaciones, los cuales contienen las principales funciones que van a ser utilizadas con el fin de subir las calificaciones de los alumnos sobre una tarea en Moodle.

A su vez, tenemos dos scripts de python que hacen uso de estas diferentes funciones para dos casos de uso distintos. En primer lugar tenemos 'PruebaGeneral', enfocado en el caso de uso de una tarea del Moodle cuya evaluación sea única, es decir, que no se va a modificar. Y en último lugar tenemos 'PruebaModificaciones', el cual está orientado a una tarea en la cual la evaluación será continúa ya que los alumnos podrán modificar la entrega.

Ahora explico los ficheros:

'entregas.py'

Requiere: sys, os, csv, datetime, re, subprocess, json, pathlib

Este fichero python contiene todas las funciones relacionadas con las entregas, desde descargarlas hasta comprobar si existen modificaciones en las mismas.

descargaTodas: Esta función descarga las entregas sobre una tarea de todos los usuarios.

descargaPorUsuario: Descarga la entrega sobre una tarea de un unico usuario que se pasa como parámetro

existenModificaciones: Comprueba si han habido modificaciones en una entrega de un usuario y devuelve 'true' si se necesita recalificar la entrega.

'hojaCalificaciones.py'

Requiere: sys, os, pathlib, re, shutil

Este fichero python contiene todas las funciones relacionadas con las hojas de calificaciones, tanto para descargarlas desde el servidor Moodle,
como subir notas al mismo Servidor desde estas hojas de calificaciones.

calculaMes:
calculaDia:
subirNota:
descarga:
subir:
apuntarNotas:


