#!/usr/bin/env python3

import sys
import os
import csv
import datetime
import re
import subprocess
import json
import pathlib

from moodleteacher.connection import MoodleConnection      # NOQA
from moodleteacher.courses import MoodleCourse      # NOQA
from moodleteacher.assignments import MoodleAssignment 
from moodleteacher.users import MoodleUser      # NOQA
from moodleteacher.requests import MoodleRequest

# Permitimos la ejecución de secuencias de comandos desde la raiz del proyecto
# en función del código fuente
sys.path.append(os.path.realpath('.'))


def strip_tags(valor):
	"""
        Elimina todas las etiquetas html de un texto introducido.
        """
	return re.sub(r'<[^>]*?>', '', valor)


def calculaMes(name):
	"""
        Funcion para calcular el nombre del mes a partir de un nombre dado en inglés.
        """

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
	
	

def calculaDia(day):
	"""
        Funcion para calcular el nombre de un dia de la semana en función de un entero, donde el 0 es lunes y el 6 domingo.
        """
        
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


def subirNota(conn, assignment, userid, grade, fb, draftareaid):
	"""
        Sube la calificación y el feedback (Tanto en texto como en archivo de retroalimentacion) correspondiente
        de un usuario a una tarea de un curso determinado
        
        Args:
            conn:        	El objeto de MoodleConnection.
            assignment: 	El objeto de la tarea.
            userid:     	Id del usuario al que se evalúa.
            grade:      	Calificación de la tarea.
            fb:     		Feedback en texto de la entrega.
            draftareaid:     	Id del draft area donde se almacena el archivo de retroalimentación.
        """
        
	userSubmission = None
	
	# Recorremos todas las entregas hasta encontrar la deseada, y subimos su calificación y feedback correspondiente
	for submission in assignment.submissions():
		user = MoodleUser.from_userid(conn, submission.userid)
		if str(user.id_) == str(userid):
			username = user.fullname
			userSubmission = submission
			userSubmission.save_grade(grade, draftareaid, feedback=fb)
			print('Se ha evaluado correctamente la tarea ' + assignment.name + ' a el usuario ' + username)
			return
	
	print('No hay ninguna entrega del usuario a esta tarea')


def descarga(conn, course, assignment):
	"""
        Descarga la hoja de calificaciones de la tarea indicada, con el formato original de la misma
        
        Args:
            conn:        	El objeto de MoodleConnection.
            course:    	El objeto del curso.
            assignment: 	El objeto de la tarea.
	"""
	
	
	# Definimos el nombre que tendra el fichero de la hoja de calificaciones
	nombreHoja = 'Calificaciones_' + assignment.name + '.csv'
	
	# Creamos un fichero nuevo de tipo csv para replicar la hoja de calificaciones de Moodle
	with open(nombreHoja, 'w') as csvfile:
		
		# Definimos los campos de cabecera que tendrá la hoja de calificaciones
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
			
			configuracion = open("ConfiguracionUsuario.txt","r")
			nombreProfesor = configuracion.readlines()[4].split("->")[1].rstrip()
			
			# Si el usuario es el profesor no recopilamos ningún dato
			if user.fullname != nombreProfesor:
			
				nombrecompleto = user.fullname
				correo = user.email
				identificador = user.id_
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

	
def subir(conn, assignment):
	"""
        Sube las calificaciones de la tarea indicada a partir de su hoja de calificaciones.
        
        Args:
            conn:        	El objeto de MoodleConnection.
            assignment: 	El objeto de la tarea.
	"""
	
	# Definimos el nombre del directorio que contiene las entregas
	ruta = 'Entregas' + '_' + assignment.name
	
	# Nombre del fichero de la hoja de calificaciones de dicha tarea
	nombreHoja = 'Calificaciones_' + assignment.name + '.csv'
	
	with open(nombreHoja, newline='') as File:  
		reader = csv.reader(File)
		head = next(reader)

		# Comprobamos que el fichero no esta vacío
		if head is not None:
			for row in reader:
				iduser = row[0]
				nota = 0.00001	# Nota del alumno
				fb = ''	# Comentarios de feedback para la nota
				if row[9]:
					# De la fila 9 obtenemos el comentario de feedback en caso de que haya
					fb = row[9]
				if row[4]:
					# De la fila 4 obtenemos la calificación en caso de que haya
					nota = float(row[4])
					nombrecompleto = row[1].replace(" ","")
					carpeta = assignment.name + '_' + nombrecompleto
					fichero = ruta + "/" + carpeta + "/output/analysis.html"
					
					#Recuperamos los datos de la ip del servidor y el token del usuario
					configuracion = open("ConfiguracionUsuario.txt","r")
					datos = configuracion.readlines()
						
					moodleHost = datos[10].split("->")[1].rstrip()
					tokenUsuario = datos[7].split("->")[1].rstrip()
					
					# Subimos el fichero de retroalimentación y almacenamos el id de su draft area
					p = subprocess.check_output(["curl", "-X", "POST", "-F", "file_1=@" + fichero,
						moodleHost + "/webservice/upload.php?token=" + tokenUsuario])
					a = p.decode('utf-8')
					b = re.findall(r'\d+',a)
					itemid = b[2]
					
					# Subimos al Moodle la calificación y el feedback correspondiente
					subirNota(conn, assignment, iduser, nota, fb, itemid)
				
	
	print('Calificaciones subidas satisfactoriamente')

def apuntarNotas(calificaciones, nombreHoja):
	"""
        Escribe las calificaciones correspondientes en una hoja de calificaciones a partir de un diccionario cuya llave es el id del
        usuario y el contenido es su calificación en la tarea
        
        Args:
            calificaciones: 	Diccionario que contiene la tupla id del usuario y calificación
            nombreArchivo:	Nombre del fichero de la hoja de calificaciones
	"""
	
	# Leemos el contenido de la hoja de calificaciones y lo almacenamos
	with open(nombreHoja, newline='') as File:  
		reader = csv.reader(File)
		data = [line for line in reader]
	
	# Modificamos el contenido en función de los datos contenidos en el diccionario 'calificaciones' y 
	# lo sobreescribimos en la hoja de calificaciones		
	with open(nombreHoja, 'w') as csvfile:
		for linea in data:
			if (linea[0] != "Identificador") and (int(linea[0]) in calificaciones.keys()):
				linea[4] = calificaciones[int(linea[0])]
		cabecera = data[0]
		writer = csv.DictWriter(csvfile, fieldnames=cabecera)
		writer.writeheader()
		data.pop(0)
		
		for alu in data:
			writer.writerow({cabecera[0]: alu[0], cabecera[1]: alu[1], cabecera[2]: alu[2], cabecera[3]: alu[3],
				cabecera[4]: alu[4], cabecera[5]: alu[5], cabecera[6]: alu[6], cabecera[7]: alu[7],
				cabecera[8]: alu[8], cabecera[9]: alu[9]})
