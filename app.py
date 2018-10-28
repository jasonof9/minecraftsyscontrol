from flask import Flask, render_template, request, send_from_directory
import boto3, json

application = Flask(__name__)

@application.route('/')
def index():
	loglines = []
	filename = "/home/admin/mc_logs/latest.log"
	file = open(filename, "r")
	for line in file:
   		loglines.append(line)
	return render_template('home.html', value=loglines)

@application.route('/ov/<path:path>')
def send_ov(path):
    return send_from_directory('ov', path)

@application.route('/about')
def about():
	return render_template('about.html')

@application.route('/serverstatus')
def serverstatus():
	client = boto3.client('ec2', region_name='us-east-1')
	response = client.describe_instance_status(InstanceIds=['i-0407af6e7e8d3ba3e'])
	return str(response)

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
