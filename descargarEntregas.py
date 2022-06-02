#!/usr/bin/env python3
#
# Example for retrieving submission details
#

import argparse
import sys
import os
# Allow execution of script from project root, based on the library
# source code
sys.path.append(os.path.realpath('.'))


from moodleteacher.connection import MoodleConnection      # NOQA
from moodleteacher.courses import MoodleCourse      # NOQA
from moodleteacher.assignments import MoodleAssignment      # NOQA
from moodleteacher.users import MoodleUser      # NOQA
from moodleteacher.files import MoodleFile      # NOQA

if __name__ == '__main__':
	#import logging
    #logging.basicConfig(level=logging.DEBUG)

    # Prepare connection to your Moodle installation.
    # The flag makes sure that the user is asked for credentials, which are then
    # stored in ~/.moodleteacher for the next time.
	conn = MoodleConnection(interactive=True)

	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--courseid", help="Course ID (check view.php?id=...).", required=True, type=int)
	parser.add_argument("-a", "--assignmentid", help="Assignment ID (check view.php?id=...).", required=True, type=int)
	args = parser.parse_args()

	course = MoodleCourse.from_course_id(conn, args.courseid)
	assignment = MoodleAssignment.from_assignment_id(course, args.assignmentid)
        
	for submission in assignment.submissions():
		user = MoodleUser.from_userid(conn, submission.userid)
		os.mkdir(assignment.name + '_' + user.fullname)
		for f in submission.files:
			f.unpack_to('/home/jesuscampo/Descargas/moodleteacher-master/examples/' + assignment.name + '_' + user.fullname + '/', False)
			
	print("Los ficheros han sido descargados en la carpeta Entregas")
