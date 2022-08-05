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

def modificaciones(conn, courseid, assignmentname, userid):
	
	course = MoodleCourse.from_course_id(conn, courseid)
	assignment = MoodleAssignment.from_assignment_name(course, assignmentname)
	
	params = {'assignid': assignment.id_, 'userid': userid}
			
	# Obtenemos todos los datos relacionados con la entrega de dicho usuario en esta tarea
	response = MoodleRequest(conn, 'mod_assign_get_submission_status').post(params).json()
	
	# Averiguamos si el usuario ha realizado la entrega de la tarea
	estado = response['lastattempt']['submission']['status']
	if estado == 'new':
		print("El alumno introducido no ha realizado ninguna entrega a dicha tarea")
		return False
	else:
		fechaMod = response['lastattempt']['submission']['timemodified']
		calificado = response['lastattempt']['gradingstatus']
		if calificado == 'notgraded':
			print("El alumno introducido ha realizado la entrega pero no ha sido calificado todavía")
			return True
		else:
			fechaCal = response['feedback']['grade']['timemodified']
	
	if (fechaMod > fechaCal):
		print("Se necesita recalificar la entrega del alumno")
		return True
	else:
		print("No se necesita recalificar la entrega del alumno")
		return False
		
		
		
	
