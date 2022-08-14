#!/usr/bin/env python3

import sys
import os
import pathlib
import re
import shutil

from pathlib import Path
from moodleteacher.connection import MoodleConnection      # NOQA
from moodleteacher.courses import MoodleCourse      # NOQA
from moodleteacher.assignments import MoodleAssignment      # NOQA
from moodleteacher.users import MoodleUser      # NOQA
from moodleteacher.files import MoodleFile      # NOQA
from moodleteacher.requests import MoodleRequest

# Permitimos la ejecución de secuencias de comandos desde la raiz del proyecto
# en función del código fuente
sys.path.append(os.path.realpath('.'))

def strip_tags(valor):
	"""
        Elimina todas las etiquetas html de un texto introducido.
        """
	return re.sub(r'<[^>]*?>', '', valor)


def descargaTodas(conn, course, assignment):
	"""
        Descarga todas las entregas realizadas por los usuarios sobre la tarea indicada, creando un directorio para cada usuario
        el cual contiene todos los ficheros de su entrega.
        
        Args:
            conn:        	El objeto de MoodleConnection.
            courseid:    	Id del curso de la tarea.
            assignmentname: 	Nombre de la tarea.
        Returns:
            users: 		Lista de los nombres de los usuarios que han realizado la entrega
            ficheros:		Lista de los nombres de los ficheros que han entregado los usuarios
	"""
	
	# Almaceno la ruta del fichero actual
	path = pathlib.Path().absolute()
	
	ficheros = []
	users = []
	
	# Definimos y creamos el directorio que contendrá todas las entregas
	if not os.path.exists('Entregas' + '_' + assignment.name):
		os.mkdir('Entregas' + '_' + assignment.name)
        
	for submission in assignment.submissions():
		# Comprobamos si existe alguna entrega
		if (len(submission.files) != 0):
		
			user = MoodleUser.from_userid(conn, submission.userid)
			
			nombreUsuario = user.fullname.replace(" ","")
			users.append(user)
			
			if os.path.exists('Entregas' + '_' + assignment.name + '/' + assignment.name + '_' + nombreUsuario):
				shutil.rmtree(str(path) + '/' + 'Entregas' + '_' + assignment.name + '/' + assignment.name + '_' + nombreUsuario)
			
			# Creamos un directorio para cada usuario que ha realizado una entrega
			os.makedirs(os.path.join('Entregas' + '_' + assignment.name , assignment.name + '_' + nombreUsuario))
			
			# En caso de tener comentario, mostramos el comentario del usuario por pantalla
			if submission.textfield:
				print("Comentarios de " + nombreUsuario + ":\n" + strip_tags(submission.textfield) + "\n")
			for f in submission.files:
				# Descargamos o descomprimimos los ficheros entregados del alumno en su carpeta correspondiente
				f.unpack_to(str(path) + '/' + 'Entregas' + '_' + assignment.name + '/' + 
					assignment.name + '_' + nombreUsuario + '/', False)
				ficheros.append(f.name)
			
	print("Hay un total de " + str(len(users)) + " entregas realizadas de un total de " + str(len(course.users)-1) + " alumnos matriculados")
	print("\nLos ficheros han sido descargados correctamente")
	
	return users, ficheros
	
	
def descargaPorUsuario(conn, course, assignment, userid):
	"""
        Descarga la entrega de un solo usuario sobre una tarea de un curso, almacenando los ficheros correspondientes
        en un directorio.
        
        Args:
            conn:        	El objeto de MoodleConnection.
            courseid:    	Id del curso de la tarea.
            assignmentname: 	Nombre de la tarea.
            userid:		Id del usuario.
        Returns:
            user: 		Usuario del que buscamos su entrega.
            nombreFichero:	Nombre del fichero de la entrega del usuario.
	"""
	
	# Almaceno la ruta del fichero actual
	path = pathlib.Path().absolute()
	
	nombreFichero = ''
	
	# Definimos y creamos el directorio que contendrá todas las entregas
	if not os.path.exists('Entregas' + '_' + assignment.name):
		os.mkdir('Entregas' + '_' + assignment.name)
        
	for submission in assignment.submissions():
		# Comprobamos si existe alguna entrega que coincida con el id del usuario
		if (len(submission.files) != 0) and (userid == submission.userid):
		
			user = MoodleUser.from_userid(conn, submission.userid)
			
			nombreUsuario = user.fullname.replace(" ","")
			
			if os.path.exists('Entregas' + '_' + assignment.name + '/' + assignment.name + '_' + nombreUsuario):
				shutil.rmtree(str(path) + '/' + 'Entregas' + '_' + assignment.name + '/' + assignment.name + '_' + nombreUsuario)
			
			# Creamos un directorio para cada usuario que ha realizado una entrega
			os.makedirs(os.path.join('Entregas' + '_' + assignment.name , assignment.name + '_' + nombreUsuario))
			
			# En caso de tener comentario, mostramos el comentario del usuario por pantalla
			if submission.textfield:
				print("Comentarios de " + nombreUsuario + ":\n" + strip_tags(submission.textfield) + "\n")
			for f in submission.files:
				# Descargamos o descomprimimos los ficheros entregados del alumno en su carpeta correspondiente
				f.unpack_to(str(path) + '/' + 'Entregas' + '_' + assignment.name + '/' + 
					assignment.name + '_' + nombreUsuario + '/', False)
				nombreFichero = f.name
			
	print("\nLos ficheros han sido descargados correctamente")
	
	return user, nombreFichero
	
	
def existenModificaciones(conn, assignment, userid):
	"""
        Comprueba si existen modificaciones en la entrega de un alumno en una tarea desde la ultima vez que se califico la misma.
        
        Args:
            conn:        	El objeto de MoodleConnection.
            assignment: 	El objeto de la tarea.
            userid:		Id del usuario
        Returns:
            True: 		En caso de que sea necesario calificar o recalificar la entrega
            False:		En caso de que no sea necesario recalificar la entrega
	"""
	
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
