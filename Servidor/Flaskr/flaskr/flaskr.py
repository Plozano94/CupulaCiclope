# all the imports
import servidorConf
import threading
from flask import Flask, request, session, g, redirect, url_for, \
	 abort, render_template, flash, Response
from contextlib import closing
import serial
import subprocess
import os

from camera import VideoCamera
# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
# create our little application :)
app = Flask(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'some_really_long_random_string_here'
logged= None
if servidorConf.board==1:
	ser = serial.Serial('/dev/ttyACM0', 9600)
else:	
	print 'Controller board is not activated'
def cameraServer():
	os.chdir("/home/trex/TFG/mjpg/mjpg-streamer/")
        print('Video streaming starting on pid',  os.getpid())
        os.system('/home/trex/TFG/mjpg/mjpg-streamer/mjpg_streamer -i "./input_uvc.so -d /dev/video0" -o "./output_http.so -w ./www" ')

if servidorConf.camera==1:
	newPid=os.fork()
	if newPid==0:
		cameraServer()	
def send(message,ser):
	if servidorConf.board==1:
		message='&'+message+'#'
		ser.write(message)


@app.route('/command', methods=['GET','POST'])
def command():
	error=None
	global logged
	if not logged:
		abort(401)
	if request.method == 'POST':
		message=request.form['command']
		print message
		#print 'Enviado'
		t = threading.Thread(target=send, args=(message,ser,))
    		t.start()
		#ser.write(message)
	return render_template('command.html', error=error)	

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != USERNAME:
			str(request.form['username'])
			error = 'Invalid username'
		elif request.form['password'] != PASSWORD:
			error = 'Invalid password'
		else:
			global logged
			logged  = True
			#session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('command'))
	return render_template('login.html', error=error)


@app.route('/logout')
def logout():
	global logged 
	logged = None
	#session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))
  

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=4000)    
