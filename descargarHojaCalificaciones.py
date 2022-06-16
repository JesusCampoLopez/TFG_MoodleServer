#!/usr/bin/env python3

import argparse
import sys
import os
import csv
import datetime
import re	#Para eliminar las etiquetas html de un texto

# Permitimos la ejecución de secuencias de comandos desde la raiz del proyecto
# en función del código fuente
sys.path.append(os.path.realpath('.'))

# Funcion que sirve para eliminar todas las etiquetas html de un texto introducido para poder rescatar
# el texto correspondiente a los comentarios de las entregas de los usuarios en una tarea
def strip_tags(valor):
	return re.sub(r'<[^>]*?>', '', valor)

# Funcion para calcular el nombre del mes a partir de un nombre dado en ingles
def calculaMes(name):
	if name == 'January':
		name = 'enero'
	elif name == 'February':
		name = 'febrero'
	elif name == 'March':
		name = 'marzo'	
	elif name == 'April':
		name = 'abril'	
	elif name == 'May':
		name = 'mayo'	
	elif name == 'June':
		name = 'junio'	
	elif name == 'July':
		name = 'julio'	
	elif name == 'August':
		name = 'agosto'	
	elif name == 'September':
		name = 'septiembre'	
	elif name == 'October':
		name = 'octubre'	
	elif name == 'November':
		name = 'noviembre'	
	elif name == 'December':
		name = 'diciembre'
	
	return name
	
	
# Funcion para calcular el nombre de un dia de la semana en función de un entero, donde el 0 es lunes y el 6 domingo
def calculaDia(day):
	if day == 0:
		day = 'lunes'
	elif day == 1:
		day = 'martes'
	elif day == 2:
		day = 'miércoles'
	elif day == 3:
		day = 'jueves'
	elif day == 4:
		day = 'viernes'
	elif day == 5:
		day = 'sábado'
	elif day == 6:
		day = 'domingo'
	
	return day


from moodleteacher.connection import MoodleConnection      # NOQA
from moodleteacher.courses import MoodleCourse      # NOQA
from moodleteacher.assignments import MoodleAssignment 
from moodleteacher.users import MoodleUser      # NOQA
from moodleteacher.requests import MoodleRequest

if __name__ == '__main__':
	#import logging
	#logging.basicConfig(level=logging.DEBUG)

    # Preparamos la conexión a nuestro Moodle
    # La etiqueta interactive nos asegura que se le pregunta al usuario por sus credenciales
    # antes de realizar la conexion, los cuales seran almacenados en ~/.moodleteacher para la próxima conexión
	conn = MoodleConnection(interactive=True)


	# Creamos un argumento para introducir el id del curso y otro para introducir el nombre de la tarea
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--courseid", help="Course ID (check view.php?id=...).", required=True, type=int)
	parser.add_argument("-a", "--assignmentname", help="User email (check moodle profile of the user...).", required=True, type=str)
	args = parser.parse_args()
	
	# Obtenemos la tarea en función del curso y su nombre
	course = MoodleCourse.from_course_id(conn, args.courseid)
	assignment = MoodleAssignment.from_assignment_name(course, args.assignmentname)
	
	# Creamos un fichero nuevo de tipo csv para replicar la hoja de calificaciones de Moodle
	with open('Calificaciones.csv', 'w') as csvfile:
		fieldnames = ['Identificador', 'Nombre completo', 'Dirección de correo', 'Estado', 'Calificación', 
				'Calificación máxima', 'La calificación puede ser cambiada', 'Última modificación (entrega)',
				'Última modificación (calificación)', 'Comentarios de retroalimentación']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		
		# Creamos los campos cabecera del fichero
		writer.writeheader()
		
		# Recorremos todos los usuarios del curso para recopilar sus datos acerca de esta tarea
		for userid in course.users:
			params = {'assignid': assignment.id_, 'userid': userid}
			
			# Obtenemos todos los datos relacionados con la entrega de dicho usuario en esta tarea
			substatus = MoodleRequest(conn, 'mod_assign_get_submission_status').post(params).json()
			
			# Guardamos el usuario
			user = MoodleUser.from_userid(conn, userid)
			
			# Si el usuario es el profesor no recopilamos ningún dato
			if user.fullname != 'Ramon Gonzalez Gomez':
			
				nombrecompleto = user.fullname
				correo = user.email
				identificador = 'Participante' + str(user.id_)
				calificacionmaxima = 100
				fechaEntrega = '-'
				fechaCalificacion = '-'
				comentarios = ''
				nota = ''
				
				# Averiguamos si se puede editar la calificación o no
				if (substatus['lastattempt']['caneditowner']) == True:
					cambiada = 'Sí'
				else:
					cambiada = 'No'
				
				# Averiguamos si el usuario ha realizado la entrega de la tarea
				estado = substatus['lastattempt']['submission']['status']
				if estado == 'new':
					estado = 'Sin entrega'
				else:
					# En caso de haberla entregado, rescatamos los datos de la entrega en concreto
					calificado = substatus['lastattempt']['gradingstatus']
					
					ultmod = datetime.datetime.fromtimestamp(substatus['lastattempt']['submission']['timemodified'])
					diaMod = calculaDia(ultmod.weekday())
					mesMod = calculaMes(ultmod.strftime("%B"))
					
					# Calculamos la fecha de entrega de la tarea de este usuario
					fechaEntrega = (diaMod + ', ' + str(ultmod.day) + ' de ' + mesMod + ' de ' + str(ultmod.year) + 
						', ' + str(ultmod.hour) + ":" + str(ultmod.minute))
					
					# Comprobamos si la tarea esta calificada o no
					if calificado == 'notgraded':
						estado = 'Enviado para calificar'
					else:
						# En caso de estar calificada, almacenamos la nota y la fecha de la calificación
						estado = 'Enviado para calificar - Calificado'
						nota = substatus['feedback']['grade']['grade']
						ultcal = datetime.datetime.fromtimestamp(substatus['feedback']['grade']['timemodified'])
						diaCal = calculaDia(ultcal.weekday())
						mesCal = calculaMes(ultcal.strftime("%B"))
						fechaCalificacion = (diaCal + ', ' + str(ultcal.day) + ' de ' + mesCal + 
							' de ' + str(ultcal.year) + ', ' + str(ultcal.hour) + ":" + str(ultcal.minute))
						
						# También guardamos los comentarios de retroalimentación en caso de haberlos
						comentarios = strip_tags(substatus['feedback']['plugins'][0]['editorfields'][0]['text'])
				
				# Finalmente escribimos todos los datos que hayamos podido recopilar sobre los usuarios respecto a la tarea
				writer.writerow({'Identificador': identificador,
					  'Nombre completo': nombrecompleto,
					  'Dirección de correo': correo,
					  'Estado': estado,
					  'Calificación': nota,
					  'Calificación máxima': '100',
					  'La calificación puede ser cambiada': cambiada,
					  'Última modificación (calificación)': fechaCalificacion,
					  'Última modificación (entrega)': fechaEntrega,
					  'Comentarios de retroalimentación': comentarios})
		
	
	print('FICHERO CREADO')



