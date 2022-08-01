#!/usr/bin/env python3

import argparse
import sys
import os

# Permitimos la ejecución de secuencias de comandos desde la raiz del proyecto
# en función del código fuente
sys.path.append(os.path.realpath('.'))


from moodleteacher.connection import MoodleConnection      # NOQA
from moodleteacher.courses import MoodleCourse      # NOQA
from moodleteacher.users import MoodleUser      # NOQA
from moodleteacher.assignments import MoodleAssignment 
from moodleteacher.requests import MoodleRequest

if __name__ == '__main__':
	#import logging
	#logging.basicConfig(level=logging.DEBUG)

    # Preparamos la conexión a nuestro Moodle
    # La etiqueta interactive nos asegura que se le pregunta al usuario por sus credenciales
    # antes de realizar la conexion, los cuales seran almacenados en ~/.moodleteacher para la próxima conexión
	conn = MoodleConnection(interactive=True)


	# Creamos un argumento para introducir el email del usuario del que se desea obtener los cursos
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--courseid", help="Course ID (check view.php?id=...).", required=True, type=int)
	parser.add_argument("-a", "--assignmentname", help="User email (check moodle profile of the user...).", required=True, type=str)
	parser.add_argument("-u", "--userid", help="User id (check moodle profile of the user...).", required=True, type=int)
	args = parser.parse_args()
	
	course = MoodleCourse.from_course_id(conn, args.courseid)
	assignment = MoodleAssignment.from_assignment_name(course, args.assignmentname)
	
	params = {'assignid': assignment.id_, 'userid': args.userid}
			
	# Obtenemos todos los datos relacionados con la entrega de dicho usuario en esta tarea
	response = MoodleRequest(conn, 'mod_assign_get_submission_status').post(params).json()
	
	# Averiguamos si el usuario ha realizado la entrega de la tarea
	estado = response['lastattempt']['submission']['status']
	if estado == 'new':
		print("El alumno introducido no ha realizado ninguna entrega a dicha tarea")
		exit()
	else:
		fechaMod = response['lastattempt']['submission']['timemodified']
		print(fechaMod)
		calificado = response['lastattempt']['gradingstatus']
		if calificado == 'notgraded':
			print("El alumno introducido ha realizado la entrega pero no ha sido calificado todavía")
			exit()
		else:
			fechaCal = response['feedback']['grade']['timemodified']
			print(fechaCal)
	
	if (fechaMod > fechaCal):
		print("Se necesita recalificar la entrega del alumno")
	else:
		print("No se necesita recalificar la entrega del alumno")
		
		
		
	
