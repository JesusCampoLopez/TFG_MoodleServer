#!/usr/bin/env python3

import argparse
import sys
import os
import pathlib

# Permitimos la ejecución de secuencias de comandos desde la raiz del proyecto
# en función del código fuente
sys.path.append(os.path.realpath('.'))


# Importamos las clases que vamos a usar
from moodleteacher.connection import MoodleConnection
from moodleteacher.courses import MoodleCourse
from moodleteacher.assignments import MoodleAssignment 
from moodleteacher.users import MoodleUser

if __name__ == '__main__':
	#import logging
	#logging.basicConfig(level=logging.DEBUG)

    # Preparamos la conexión a nuestro Moodle
    # La etiqueta interactive nos asegura que se le pregunta al usuario por sus credenciales
    # antes de realizar la conexion, los cuales seran almacenados en ~/.moodleteacher para la próxima conexión
	conn = MoodleConnection(interactive=True)
	
	# Añado los argumentos id del curso y nombre de la tarea
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--courseid", help="Course ID (check view.php?id=...).", required=True, type=int)
	parser.add_argument("-a", "--assignmentname", help="Assignment name (check the name of the assignment).", required=True, type=str)
	parser.add_argument("-u", "--useremail", help="User email (check moodle profile of the user...).", required=True, type=str)
	parser.add_argument("-g", "--grade", help="Grade (Introduce the grade you want to give).", required=True, type=int)
	args = parser.parse_args()

	# Creamos los objetos de curso y assignment correspondientes en funcion de los argumentos recibidos
	course = MoodleCourse.from_course_id(conn, args.courseid)
	assignment = MoodleAssignment.from_assignment_name(course, args.assignmentname)
	
	for submission in assignment.submissions():
		user = MoodleUser.from_userid(conn, submission.userid)
		if user.email == args.useremail:
			username = user.fullname
			userSubmission = submission
		
	
	userSubmission.save_grade(args.grade)
	print('Se ha evaluado correctamente la tarea ' + args.assignmentname + ' a el usuario ' + username)
