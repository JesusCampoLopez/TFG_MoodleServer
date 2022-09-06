#!/usr/bin/env python3

import argparse
import sys
import os
import subprocess
import entregas
import hojacalificaciones
import time
import re

# Permite la ejecución del script desde la ruta del proyecto, basado en el codigo fuente
# de la libreria
sys.path.append(os.path.realpath('.'))

from moodleteacher.connection import MoodleConnection      # NOQA
from moodleteacher.users import MoodleUser      # NOQA
from moodleteacher.courses import MoodleCourse      # NOQA
from moodleteacher.requests import MoodleRequest      # NOQA
from moodleteacher.assignments import MoodleAssignment 

if __name__ == '__main__':
	
	# Preparamos la conexion a nuestro servidor de Moodle
    	# Recuperamos los datos del moodlehost y el token del usuario a través del fichero de configuracion
	
	configuracion = open("ConfiguracionUsuario.txt","r")
	datos = configuracion.readlines()
	
	moodleHost = datos[10].split("->")[1].rstrip()
	tokenUsuario = datos[7].split("->")[1].rstrip()
	
	conn = MoodleConnection(moodle_host=moodleHost, token=tokenUsuario)


	# Añado los argumentos id del curso y nombre de la tarea
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--courseid", help="Course ID (check view.php?id=...).", required=True, type=int)
	parser.add_argument("-a", "--assignmentname", help="Assignment name (check the name of the assignment).", required=True, type=str)
	args = parser.parse_args()
	
	course = MoodleCourse.from_course_id(conn, args.courseid)
	assignment = MoodleAssignment.from_assignment_name(course, args.assignmentname)
	
	# Comprobamos si existe la tarea
	if assignment is None:
		print("No existe ninguna tarea con ese nombre")
		exit() 
	
	# Establecemos el directorio donde se almacenan todas las entregas
	path = "Entregas_" + args.assignmentname
	
	while(True):
		for submission in assignment.submissions():
			user = MoodleUser.from_userid(conn, submission.userid)
			bool = entregas.existenModificaciones(conn, assignment, user.id_)
			if bool:
				
				# Descargamos la entrega del usuario del que se necesita recalificar
				u, f = entregas.descargaPorUsuario(conn, course, assignment, user.id_)
				
				# Esta es la ruta donde se almacena la entrega del usuario
				totalpath = path + "/" + args.assignmentname + "_" + u.fullname.replace(" ","") + "/" + f
					
				# Ejecutamos la herramienta correspondiente para calificar la entrega del usuario
				r = subprocess.call(["./intro_sw_static_check.sh",totalpath,"config.yaml"])
				fb = ''
				
				# Definimos la ruta donde se almacena el fichero de retroalimentacion
				nombrecompleto = user.fullname.replace(" ","")
				carpeta = assignment.name + '_' + nombrecompleto
				fichero = path + "/" + carpeta + "/output/analysis.html"
					
				# Subimos el fichero de retroalimentación y almacenamos el id de su draft area
				p = subprocess.check_output(["curl", "-X", "POST", "-F", "file_1=@" + fichero,
						"http://127.0.0.1/moodle/webservice/upload.php?token=f51e7fedd7a08f0bb11fc2a10d8598c1"])
				a = p.decode('utf-8')
				b = re.findall(r'\d+',a)
				itemid = b[2]
				
				# Subimos la calificación del usuario junto con su retroalimentacion al servidor de Moodle
				hojacalificaciones.subirNota(conn, assignment, user.id_, r, fb, itemid)
		
		# Esperamos 30 segundos para volver a comprobar si han habido modificaciones
		time.sleep(30)
	
	
	
