import boto3
import datetime
#import mcstatus.querymc as QM

#this should return a string that matches a classname in 9w.css
def logLineStyle(rawLogLine):
    baseEventStyle = 'font-weight:bold'
    event = interestingLogLine(rawLogLine)
    returnedStyle = ''
    if event == 'death':
        returnedStyle = baseEventStyle + ';color:red'
    elif event == 'serverstart':
        returnedStyle = baseEventStyle + ';color:lime'
    elif event == 'joinedleft':
        returnedStyle = baseEventStyle + ';color:white'
    elif event == 'servertrouble':
        returnedStyle = baseEventStyle + ';color:yellow'
    elif event == 'advancement':
        returnedStyle = baseEventStyle + ';color:purple'
    
    return returnedStyle

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

def interestingLogLine(logline):
    #todo - put these into a file and read it in
    interesting = {
            'Starting minecraft server version' : 'serverstart',
            'Done (' : 'serverstart',
            'joined the game' : 'joinedleft',
            'Can\'t keep up!' : 'servertrouble',
            'left the game' : 'joinedleft',
            'has made the advancement' : 'advancement',
            'has completed the challenge' : 'advancement',
            'was shot by' : 'death',
            'was pricked to death' : 'death',
            'walked into a cactus whilst trying to escape' : 'death',
            'was roasted in dragon breath' : 'death',
            'drowned' : 'death',
            'suffocated in a wall' : 'death',
            'was squished too much' : 'death',
            'was squashed by' : 'death',
            'experienced kinetic energy' : 'death',
            'removed an elytra while flying whilst trying to escape' : 'death',
            'blew up' : 'death',
            'was blown up by' : 'death',
            'hit the ground too hard' : 'death',
            'fell from a high place' : 'death',
            'fell off a ladder' : 'death',
            'fell off some vines' : 'death',
            'fell out of the water' : 'death',
            'fell into a patch of fire' : 'death',
            'fell into a patch of cacti' : 'death',
            'was doomed to fall' : 'death',
            'fell too far and was finished by' : 'death',
            'was shot off some vines by' : 'death',
            'was shot off a ladder by' : 'death',
            'was blown from a high place by' : 'death',
            'was squashed by a falling anvil' : 'death',
            'was squashed by a falling block' : 'death',
            'was killed by magic' : 'death',
            'went up in flames' : 'death',
            'burned to death' : 'death',
            'was burnt to a crisp whilst fighting' : 'death',
            'walked into fire whilst fighting' : 'death',
            'went off with a bang' : 'death',
            'tried to swim in lava' : 'death',
            'was struck by lightning' : 'death',
            'discovered the floor was lava' : 'death',
            'walked into danger zone due to' : 'death',
            'was slain by' : 'death',
            'got finished off by' : 'death',
            'was fireballed by' : 'death',
            'was killed by' : 'death',
            'was killed by even more magic' : 'death',
            'starved to death' : 'death',
            'was poked to death by a sweet berry bush' : 'death',
            'was killed trying to hurt' : 'death',
            'was impaled by' : 'death',
            'fell out of the world' : 'death',
            'fell from a high place and fell out of the world' : 'death',
            'didn\'t want to live in the same world as' : 'death',
            'withered away' : 'death',
            'was pummeled by' : 'death',
            'died' : 'death'
            }
    for item in interesting:
        if logline.find(item) >= 0:
            #print(interesting[item])
            return interesting[item]
            

def translateTime(timeToTranslate):
    translatedTime = datetime.datetime.now
    print(translatedTime.strftime('%B'))

def getServerStatus(serverinfo, instance_id, serverfqdn='minecraft.nine-walkers.com'):

    serverstatus = {}
    instance_status = ''
    try:
        instance_status = getAWSInstanceStatus(instance_id)
    except:
        instance_status = ''

    if instance_status:
        try:
            serverstatus = QM.querymcserver(serverfqdn)
        except:
            serverstatus = []

    serverinfo['serverstatus'] = serverstatus
    serverinfo['instancestatus'] = instance_status
