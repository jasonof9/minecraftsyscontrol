import boto3

#this should return a string that matches a classname in 9w.css
def logLineStyle(rawLogLine):
	if rawLogLine.find('joined the game') >= 0 or rawLogLine.find('left the game') >= 0:
		return 'logjoinleave'
	elif rawLogLine.find('fell from a high') >= 0:
		return 'logdeath'
	else:
		return 'logline'


#[17:12:08] [Server thread/INFO]: srhannah52 has made the advancement [We Need to Go Deeper]
#[17:15:46] [Server thread/INFO]: srhannah52 has completed the challenge [Return to Sender]


def getMCServerStatus(instanceid='i-0cd6873f151ca215e'):
	client = boto3.client('ec2', region_name='us-east-1')


	filters = [{
	'Name': 'instance-id',
	'Values': [instanceid]
	}]

	response = client.describe_instances(Filters=filters)

	print(response['Reservations'][0]['Instances'][0]['State']['Name'])


def getAWSInstanceStatus(aws_instance):
	client = boto3.client('ec2', region_name='us-east-1')
        response = client.describe_instance_status(InstanceIds=[aws_instance])

        if len(response['InstanceStatuses']) == 0:
                status = ''
        else:
                status = response['InstanceStatuses'][0]['InstanceState']['Name']

	return status
