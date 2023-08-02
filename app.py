from flask import Flask, render_template, request, Response, Markup, redirect
import boto3, json, os, time, settings, datetime, mc_util, servers
from datetime import timedelta
import querymc as QM
from markupsafe import escape


application = Flask(__name__)


@application.route('/')
def index():
        return dash('town')


@application.route('/<server>')
def dash(server):
        targetserver = servers.SERVERS[escape(server)]
        serverinfo = {}
        serverinfo['servername'] = targetserver['name']
        serverinfo['bgimage'] = targetserver['bgimage']
        serverinfo['newspage'] = targetserver['news']

        serverstatus = {}

        instance_status = mc_util.getAWSInstanceStatus(targetserver['aws_instance_id'])
        if instance_status:
                try:
                        serverstatus = QM.querymcserver(targetserver['server_address'])
                except:
                        serverstatus = []

        serverinfo['serverstatus'] = serverstatus
        serverinfo['instancestatus'] = instance_status

#       mc_util.getServerStatus(serverinfo, settings.TOWN_SERVER_INFO['aws_instance_id'], 'waterworld.nine-walkers.com')

        mxmode = settings.AWS_CONFIG['maintenance']
        return render_template('serverpage.html',value=serverinfo['serverstatus'],serverstatusdict=serverstatus,thisserver=targetserver,serverdict=servers.SERVERS,mx=mxmode,serverdata=serverinfo,serverurl=escape(server))




@application.route('/hometest')
def index2():
        client = boto3.client('ec2', region_name='us-east-1')
        r = client.describe_instance_status(InstanceIds=[settings.AWS_CONFIG['mcinstance']])
        serverstatus = {}

        if len(r['InstanceStatuses']) == 0:
                i = ''
        else:
                i = r['InstanceStatuses'][0]['InstanceState']['Name']
                serverstatus = QM.querymcserver('minecraft.nine-walkers.com')

        return render_template('home3.html',value=i,serverstatusdict=serverstatus)


@application.route('/<server>/logs',methods=['GET'])
def logview(server):
        loglines = []
        showfulllogs = request.args.get('logtype',default='')
        filename = servers.SERVERS[escape(server)]['logpath'] + '/latest.log'
        file = open(filename, "r")
        loglines.append(Markup('<strong>Date: '))
        loglines.append(time.strftime('%Y-%m-%d', time.localtime(os.path.getmtime(filename))))
        loglines.append(Markup('</strong>'))
        lastline = ''
        duplinecount = 0
        for line in file:
                if (line[10:50] != lastline[10:50]) or (showfulllogs):
                        linetime = (line[1:9])
                        if linetime:
                                try:
                                        lineactualtime = datetime.datetime.strptime(linetime, '%H:%M:%S')
                                        linelocaltime = lineactualtime + timedelta(hours=-5)
                                        localminute = str(linelocaltime.minute)
                                        localsecond = str(linelocaltime.second)
                                        if len(localminute) == 1:
                                                localminute = '0' + localminute
                                        if len(localsecond) == 1:
                                                localsecond = '0' + localsecond
                                        #print (linelocaltime)
                                        style = mc_util.logLineStyle(line)
                                        lineformatted = '[' +  str(linelocaltime.hour) + ':' + localminute + ':' + localsecond + '] ' +  str.replace(str.replace(line[10:], '<', '&lt;'), '>','&gt;')
                                        lineformatted = Markup('<span style = \"' + style + '\">' + lineformatted + '</span>')
                                except:
                                        lineformatted = line
                                if duplinecount > 0:
                                        loglines.append(Markup('<a href = "/logs?logtype=full"><span>+ ' +  str(duplinecount) + ' more</span></a>'))
                                        duplinecount = 0
                        loglines.append(lineformatted)
                        lastline = line
                else:
                        duplinecount += 1
        loglines.append(Markup('<br/> <br/>'))
#       loglines.append( time.strftime('%Y-%m-%d', time.localtime(os.path.getmtime('/home/admin/mc_logs/latest.log'))))
        return render_template('logs.html', value=loglines, serverurl = escape(server), serverdict = servers.SERVERS, thisserver = servers.SERVERS[escape(server)])


@application.route('/about')
def about():
        return render_template('about.html')

#todo ; add try/except
@application.route('/serverstatus')
def serverstatus():
        client = boto3.client('ec2', region_name='us-east-1')
        #response = client.describe_instance_status(InstanceIds=[settings.AWS_CONFIG['mcinstance']])
        response = client.describe_instances(InstanceIds=[settings.AWS_CONFIG['mcinstance']])
        
        #strResponse = json.dumps(response)
        strResponse = response
        return Response(strResponse, mimetype='text/json')

#todo - add try/except
@application.route('/startserver',methods=['GET','POST'])
def startserver():
        returnedData = ''
        servertype = ''

        if(request.args):
                try:
                        servertype = request.args['servername']
                except:
                        servertype = ''

        print(servertype)
        targetserver = servers.SERVERS[servertype]

        instanceid = targetserver['aws_instance_id']
        instancename = request.args['servername']

        client = boto3.client('ec2', region_name='us-east-2')
        r = client.describe_instance_status(InstanceIds=[instanceid])
        if len(r['InstanceStatuses']) == 0:
                i = 'instance down'
        else:
                i = r['InstanceStatuses'][0]['InstanceState']['Name']

        if i == 'running':
                returnedData = 'alreadyrunning'
        else:
                if not returnedData:
                         result = client.start_instances(InstanceIds=[instanceid])
                         returnedData = json.dumps(result)
        return render_template('startserver.html', value=returnedData, server=servertype, serverdict=servers.SERVERS, thisserver = targetserver)


@application.route('/stopserver',methods=['GET','POST'])
def stopserver():
        returnedData = ''
#request.data
#       if not returnedData:
#               returnedData = request.args.get('hello','')
#               if not returnedData:
#                       returnedData = 'no data'
        servertype = ''

        if(request.args):
                try:
                        servertype = request.args['servername']
                except:
                        servertype = ''

        targetserver = servers.SERVERS[servertype]

        instancename = 'mcinstance'
        instanceid = targetserver['aws_instance_id']
        serverurl = targetserver['server_address']

        client = boto3.client('ec2', region_name='us-east-2')
        r = client.describe_instance_status(InstanceIds=[instanceid])
        if len(r['InstanceStatuses']) == 0:
                        returnedData = 'Server is already down!'
        else:
                        returnedData = r['InstanceStatuses'][0]['InstanceState']['Name']

        if returnedData == 'running':
                #do another check to be sure no one is online
                serverstatus = QM.querymcserver(serverurl)
                if serverstatus['playersonline'] != 0:
                        returnedData = 'Someone is online - not stopping the server!'
                else:
                                        result = client.stop_instances(InstanceIds=[instanceid])
                                        returnedData = json.dumps(result)

        return render_template('stopserver.html', value=returnedData, serverdict=servers.SERVERS, thisserver = targetserver)






@application.route('/mcstatus')
def mcstatus():
        return QM.queryninewalkers()

@application.route('/playersonline')
def playersonline():

        playerlist = ''
        playerarray = QM.queryplayersonly('minecraft.nine-walkers.com')
        for s in playerarray:
                playerlist += s 
                playerlist += ';'
        return playerlist


@application.errorhandler(404)
def handle404(e):
        return e

@application.errorhandler(500)
def handle500(e):
        return str(e)

@application.route('/robots.txt')
def robots():
        return render_template('robots.html')



if __name__ == '__main__':
        application.run()
