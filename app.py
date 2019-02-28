from flask import Flask, render_template, request, send_from_directory, Response, Markup
import boto3, json, os, time, settings, datetime
from datetime import timedelta
import mcstatus.querymc as QM


application = Flask(__name__)

@application.route('/')
def index():
        client = boto3.client('ec2', region_name='us-east-1')
        r = client.describe_instance_status(InstanceIds=[settings.AWS_CONFIG['mcinstance']])
	serverstatus = {}

	if len(r['InstanceStatuses']) == 0:
		i = ''
	else:
		i = r['InstanceStatuses'][0]['InstanceState']['Name']
		serverstatus = QM.querymcserver('minecraft.nine-walkers.com')
#	return(i)
	return render_template('home.html',value=i,serverstatusdict=serverstatus)


@application.route('/logs')
def logview():
	loglines = []
	filename = "/home/admin/mc_logs/latest.log"
	file = open(filename, "r")
	loglines.append(Markup('<strong>Date: '))
	loglines.append(time.strftime('%Y-%m-%d', time.localtime(os.path.getmtime(filename))))
	loglines.append(Markup('</strong>'))
	for line in file:
		linetime = (line[1:9])
	        if linetime:
        		lineactualtime = datetime.datetime.strptime(linetime, '%H:%M:%S')
               		linelocaltime = lineactualtime + timedelta(hours=-6)
               		print (linelocaltime)
                	lineformatted = '[' +  str(linelocaltime.hour) + ':' + str(linelocaltime.minute) + ':' + str(linelocaltime.second) + '] ' +  line[10:]
	        loglines.append(lineformatted)

	loglines.append(Markup('<br/> <br/>'))
#	loglines.append( time.strftime('%Y-%m-%d', time.localtime(os.path.getmtime('/home/admin/mc_logs/latest.log'))))
	return render_template('logs.html', value=loglines)

@application.route('/ov/<path:path>')
def send_ov(path):
    return send_from_directory('ov', path)

@application.route('/about')
def about():
	return render_template('about.html')

#todo ; add try/except
@application.route('/serverstatus')
def serverstatus():
	client = boto3.client('ec2', region_name='us-east-1')
	response = client.describe_instance_status(InstanceIds=[settings.AWS_CONFIG['mcinstance']])
	
	strResponse = json.dumps(response)
	return Response(strResponse, mimetype='text/json')

#todo - add try/except
@application.route('/startserver',methods=['GET','POST'])
def startserver():
	returnedData = ""
#request.data
#	if not returnedData:
#		returnedData = request.args.get('hello','')
#		if not returnedData:
#			returnedData = 'no data'

        client = boto3.client('ec2', region_name='us-east-1')
        r = client.describe_instance_status(InstanceIds=[settings.AWS_CONFIG['mcinstance']])
        if len(r['InstanceStatuses']) == 0:
                i = 'instance down'
        else:
                i = r['InstanceStatuses'][0]['InstanceState']['Name']

	if i == 'running':
		returnedData = 'alreadyrunning'
	else:
		if not returnedData:
			 result = client.start_instances(InstanceIds=[settings.AWS_CONFIG['mcinstance']])
			 returnedData = json.dumps(result)
#			returnedData = i
	return render_template('startserver.html', value=returnedData)


@application.route('/overview')
def overviewer():
	return render_template('overview.html')

@application.route('/mcstatus')
def mcstatus():
	return QM.queryninewalkers()

@application.errorhandler(404)
def handle404(e):
	return e

@application.errorhandler(500)
def handle500(e):
	return str(e)

if __name__ == '__main__':
	application.run()
