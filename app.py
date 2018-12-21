from flask import Flask, render_template, request, send_from_directory, Response
import boto3, json, os, time, settings

application = Flask(__name__)

@application.route('/')
def index():
        client = boto3.client('ec2', region_name='us-east-1')
        r = client.describe_instance_status(InstanceIds=[settings.AWS_CONFIG['mcinstance']])
	if len(r['InstanceStatuses']) == 0:
		i = ''
	else:
		i = r['InstanceStatuses'][0]['InstanceState']['Name']
#	return(i)
	return render_template('home.html',value=i)


@application.route('/logs')
def logview():
	loglines = []
	filename = "/home/admin/mc_logs/latest.log"
	file = open(filename, "r")
	for line in file:
   		loglines.append(line)
	loglines.append('Date: ')
	loglines.append( time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime('/home/admin/mc_logs/latest.log'))))
	return render_template('logs.html', value=loglines)

@application.route('/ov/<path:path>')
def send_ov(path):
    return send_from_directory('ov', path)

@application.route('/about')
def about():
	return render_template('about.html')

@application.route('/serverstatus')
def serverstatus():
	client = boto3.client('ec2', region_name='us-east-1')
	response = client.describe_instance_status(InstanceIds=[settings.AWS_CONFIG['mcinstance']])
	
	strResponse = json.dumps(response)
	return Response(strResponse, mimetype='text/json')


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

@application.errorhandler(404)
def handle404(e):
	return e

@application.errorhandler(500)
def handle500(e):
	return str(e)

if __name__ == '__main__':
	application.run()
