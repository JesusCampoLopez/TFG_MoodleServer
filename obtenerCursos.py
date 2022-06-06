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
	parser.add_argument("-u", "--useremail", help="User email (check moodle profile of the user...).", required=True, type=str)
	args = parser.parse_args()
	
	params = {}
	response = MoodleRequest(
            conn, 'core_course_get_courses_by_field').post(params).json()
	
	i = 0		# Variable que sirve para evitar contabilizar el curso principal de nuestro Moodle.
	ids = []	# Almacenamos los ids de todos los cursos a los que pertence el usuario en cuestión
	
	for c in response['courses']:
		if i > 0:
			course = MoodleCourse.from_course_id(conn, c['id'])		
			user = MoodleUser.from_useremail(conn, args.useremail)
			if course.users[user.id_]:		# Si el usuario pertenece al curso, lo almacenamos en la lista
				ids.append(course.id_)
				print("El alumno " + user.fullname + " pertenece al curso con id = " + str(course.id_))
		i += 1
	
	# Mostramos los ids de todos los cursos a los que pertenece el usuario
	print(ids)
