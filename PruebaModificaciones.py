#!/usr/bin/env python3
#
# Example for retrieving submission details
#

import argparse
import sys
import os
import subprocess
import descargarEntregas
import hojacalificaciones
import existenModificaciones
import time

# Allow execution of script from project root, based on the library
# source code
sys.path.append(os.path.realpath('.'))

from moodleteacher.connection import MoodleConnection      # NOQA
from moodleteacher.users import MoodleUser      # NOQA
from moodleteacher.courses import MoodleCourse      # NOQA
from moodleteacher.requests import MoodleRequest      # NOQA
from moodleteacher.assignments import MoodleAssignment 

if __name__ == '__main__':
	#import logging
	#logging.basicConfig(level=logging.DEBUG)

    	# Prepare connection to your Moodle installation.
    	# The flag makes sure that the user is asked for credentials, which are then
    	# stored in ~/.moodleteacher for the next time.
	conn = MoodleConnection(interactive=True)


	#Añado los argumentos id del curso y nombre de la tarea
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--courseid", help="Course ID (check view.php?id=...).", required=True, type=int)
	parser.add_argument("-a", "--assignmentname", help="Assignment name (check the name of the assignment).", required=True, type=str)
	args = parser.parse_args()
	
	course = MoodleCourse.from_course_id(conn, args.courseid)
	assignment = MoodleAssignment.from_assignment_name(course, args.assignmentname)
	activo = True
	
	#Establecemos el directorio donde se almacenan todas las entregas
	path = "Entregas_" + args.assignmentname
	
	while(activo):
		for submission in assignment.submissions():
			user = MoodleUser.from_userid(conn, submission.userid)
			bool = existenModificaciones.modificaciones(conn, args.courseid, args.assignmentname, user.id_)
			if bool:
				u, f = descargarEntregas.descargarEntregas(conn, args.courseid, args.assignmentname)
				
				#Descargamos la hoja de calificaciones de dicha tarea
				hojacalificaciones.descarga(conn, args.courseid, args.assignmentname)
				
				#Este diccionario contendra la tupla del id del usuario y su respectiva nota en la tarea
				diccionario = {}
				
				#Recorremos todas las entregas realizadas por los alumnos
				for i in range(len(u)):
					#Esta sera la ruta del alumno correspondiente a esta iteracion
					totalpath = path + "/" + args.assignmentname + "_" + u[i].fullname.replace(" ","") + "/" + f[i]
					
					#Ejecutamos la herramienta correspondiente para calificar la entrega
					r = subprocess.call(["./intro_sw_static_check.sh",totalpath,"config.yaml"])
					
					#Actualizamos el diccionarios, con el par id de usuario y su nota
					diccionario[u[i].id_] = r
				
				nombreArchivo = 'Calificaciones_' + args.assignmentname + '.csv'
				
				# Una vez calificadas todas las entregas con la herramienta, actualizamos nuestra
				# hoja de calificaciones apuntando las notas	
				hojacalificaciones.apuntarNotas(diccionario, nombreArchivo)
				
				#Una vez actualizadas las notas en la hoja de calificaciones, a partir de la misma subimos las notas a Moodle
				hojacalificaciones.subir(conn, args.courseid, args.assignmentname)
		time.sleep(30)
	
	
	
