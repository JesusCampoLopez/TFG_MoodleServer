#!/usr/bin/env python3
#
# Example for retrieving submission details
#

import argparse
import sys
import os
import pathlib
import re	#Para eliminar las etiquetas html de un texto

from pathlib import Path
from moodleteacher.connection import MoodleConnection      # NOQA
from moodleteacher.courses import MoodleCourse      # NOQA
from moodleteacher.assignments import MoodleAssignment      # NOQA
from moodleteacher.users import MoodleUser      # NOQA
from moodleteacher.files import MoodleFile      # NOQA

# Allow execution of script from project root, based on the library
# source code
sys.path.append(os.path.realpath('.'))

# Funcion que sirve para eliminar todas las etiquetas html de un texto introducido para poder rescatar
# el texto correspondiente a los comentarios de las entregas de los usuarios en una tarea
def strip_tags(valor):
	return re.sub(r'<[^>]*?>', '', valor)


def descargarEntregas(conn, courseid, assignmentname):
	#import logging
	#logging.basicConfig(level=logging.DEBUG)

    	# Prepare connection to your Moodle installation.
    	# The flag makes sure that the user is asked for credentials, which are then
    	# stored in ~/.moodleteacher for the next time.
	#conn = MoodleConnection(interactive=True)
	
	#Almaceno la ruta del fichero actual
	path = pathlib.Path().absolute()

	#Creamos los objetos de curso y assignment correspondientes en funcion de los argumentos recibidos
	course = MoodleCourse.from_course_id(conn, courseid)
	assignment = MoodleAssignment.from_assignment_name(course, assignmentname)
	
	numAlumnos = 0	#Variable para contabilizar el numero de alumnos que han realizado la entrega para el assignment
	ficheros = []
	users = []
	
	os.mkdir('Entregas' + '_' + assignment.name)
        
	for submission in assignment.submissions():
		#Comprobamos si existe alguna entrega
		if (len(submission.files) != 0):
			numAlumnos += 1
		
			user = MoodleUser.from_userid(conn, submission.userid)
			#Creamos un directorio para almacenar todos los archivos que ha entregado el alumno
			
			nombreUsuario = user.fullname.replace(" ","")
			users.append(user)
			
			os.makedirs(os.path.join('Entregas' + '_' + assignment.name , assignment.name + '_' + nombreUsuario))
			#En caso de tener comentario, mostramos el comentario del usuario por pantalla
			if submission.textfield:
				print("Comentarios de " + nombreUsuario + ":\n" + strip_tags(submission.textfield) + "\n")
			for f in submission.files:
				#Descargamos o descomprimimos los ficheros entregados del alumno en su carpeta correspondiente
				f.unpack_to(str(path) + '/' + 'Entregas' + '_' + assignment.name + '/' + 
					assignment.name + '_' + nombreUsuario + '/', False)
				ficheros.append(f.name)
			
	print("Hay un total de " + str(numAlumnos) + " entregas realizadas de un total de " + str(len(course.users)-1) + " alumnos matriculados")
	print("\nLos ficheros han sido descargados correctamente")
	
	return numAlumnos, users, ficheros
