#!/usr/bin/python
# Colin Reese
# 12/18/2012
#
# This script resets the controldata.db database 

import os
import time
from pilib import sqlitemultquery
 

filedir = ""
onewiredir = "/var/1wire/"
outputdir = "/var/www/data/"

################################################
# Main control database

database = '/var/www/data/controldata.db'

# Create databases entries or leave them empty?    
addentries=True

querylist=[]
runquery=False

answer =raw_input('Rebuild status table (y/N)?')
if answer=='y':
    runquery=True

    ### SystemStatus table 

    table='systemstatus'
    querylist.append('drop table if exists ' + table)
    querylist.append("create table " + table + " (picontrolenabled real default 0, picontrolstatus real default 0, picontrolfreq real default 15 , lastpicontrolpoll text, inputsreadenabled real default 1, inputsreadstatus real default 0, inputsreadfreq real default 15, lastinputspoll text, enableoutputs real default 0, sessioncontrolenabled real, sessioncontrolstatus real,systemmessage text)")

    if addentries:
        querylist.append("insert into " + table + " values (0,0,15,'',1,0,15,'',0,1,0,'')")

answer =raw_input('Rebuild indicators table (y/N)?')
if answer=='y':
    runquery=True

    ### Indicators table 
    ## not built yet

    table='indicators'
    querylist.append('drop table if exists ' + table)
    querylist.append("create table " + table + " ( name text primary key, type text, status int, detail text)")
    addentries=True

    if addentries:
        querylist.append("insert into " + table + " values ('SPI_RGB1_R', 'SPI', 0,'red')")
        querylist.append("insert into " + table + " values ('SPI_RGB1_G', 'SPI', 0,'green')")
        querylist.append("insert into " + table + " values ('SPI_RGB1_B', 'SPI', 0,'blue')")
        querylist.append("insert into " + table + " values ('SPI_RGB2_R', 'SPI', 0,'red')")
        querylist.append("insert into " + table + " values ('SPI_RGB2_G', 'SPI', 0,'green')")
        querylist.append("insert into " + table + " values ('SPI_RGB2_B', 'SPI', 0,'blue')")
        querylist.append("insert into " + table + " values ('SPI_RGB3_R', 'SPI', 0,'red')")
        querylist.append("insert into " + table + " values ('SPI_RGB3_G', 'SPI', 0,'green')")
        querylist.append("insert into " + table + " values ('SPI_RGB3_B', 'SPI', 0,'blue')")
        querylist.append("insert into " + table + " values ('SPI_RGB4_R', 'SPI', 0,'red')")
        querylist.append("insert into " + table + " values ('SPI_RGB4_G', 'SPI', 0,'green')")
        querylist.append("insert into " + table + " values ('SPI_RGB4_B', 'SPI', 0,'blue')")
        querylist.append("insert into " + table + " values ('SPI_SC_R', 'SPI', 0,'red')")
        querylist.append("insert into " + table + " values ('SPI_SC_G', 'SPI', 0,'green')")
        querylist.append("insert into " + table + " values ('SPI_SC_B', 'SPI', 0,'blue')")
        querylist.append("insert into " + table + " values ('SPI_SC_Y', 'SPI', 0,'yellow')")

answer =raw_input('Rebuild outputs table (y/N)?')
if answer=='y':
    runquery=True

    ### Outputs table 

    table='outputs'
    querylist.append('drop table if exists ' + table)
    querylist.append("create table " + table + " ( id text primary key, interface text, type text, address text, enabled integer default 0, name text unique, mode text default 'manual', status integer default 0, ontime string, offtime string, minontime real, minofftime real)")
    addentries=True
    if addentries:
        querylist.append("insert into " + table + " values ('GPIO1', 'GPIO', 'GPIO', '18', 0, 'output1', 'manual', 0,'','',0,0)")
        querylist.append("insert into " + table + " values ('GPIO2', 'GPIO', 'GPIO', '23', 0, 'output2', 'manual', 0,'','',0,0)")
        querylist.append("insert into " + table + " values ('GPIO3', 'GPIO', 'GPIO', '24', 0, 'output3', 'manual', 0,'','',0,0)")
        querylist.append("insert into " + table + " values ('GPIO4', 'GPIO', 'GPIO', '25', 0, 'output4', 'manual', 0,'','',0,0)")
        querylist.append("insert into " + table + " values ('GPIO5', 'GPIO', 'GPIO', '4', 0, 'output5', 'manual', 0,'','',0,0)")
        querylist.append("insert into " + table + " values ('GPIO6', 'GPIO', 'GPIO', '17', 0, 'output6', 'manual', 0,'','',0,0)")
        querylist.append("insert into " + table + " values ('GPIO7', 'GPIO', 'GPIO', '21', 0, 'output7', 'manual', 0,'','',0,0)")
        querylist.append("insert into " + table + " values ('GPIO8', 'GPIO', 'GPIO', '22', 0, 'output8', 'manual', 0,'','',0,0)")

answer =raw_input('Rebuild network table (y/N)?')
if answer=='y':
    runquery=True

    ### Network settings table 

    table='network'
    querylist.append('drop table if exists ' + table)
    querylist.append("create table " + table + " (nettype text, addtype text, address text, gateway text)")

    querylist.append("insert into " + table + " values ('station','static','192.168.1.40','192.168.1.1')")

answer =raw_input('Rebuild ioinfo table (y/N)?')
if answer=='y':
    runquery=True

    ### Inputs Info Table 

    table='ioinfo'
    querylist.append('drop table if exists ' + table)
    querylist.append("create table " + table + " (ioid text primary key, inputname text)")

answer =raw_input('Rebuild inputsdata table (y/N)?')
if answer=='y':
    runquery=True

    ### InputData Table 

    table='inputsdata'
    querylist.append('drop table if exists ' + table)
    querylist.append("create table " + table + " (id text primary key, interface text, type text, address text, value real, unit text, polltime text, enabled real default 1, name text unique)")

answer =raw_input('Rebuild algorithms table (y/N)?')
if answer=='y':
    runquery=True

    ### Controlalgorithms table

    table='controlalgorithms'
    querylist.append('drop table if exists ' + table)
    querylist.append("create table " + table + " (name text primary key, type text, maxposrate real default 0, maxnegrate real default 0, derivativemode text default time, derivativeperiod real default 0, integralmode text default time, integral period real default 0, proportional real default 1, integral real default 0, derivative real default 0, deadbandhigh real default 0, deadbandlow real default 0, dutypercent real default 0, dutyperiod real default 1)")

    if addentries:
        querylist.append("insert into " + table + " values ('on/off 1', 'on/off with deadband',1,1,0,0,0,0,0,1)")

answer =raw_input('Rebuild algorithmtypes table (y/N)?')
if answer=='y':
    runquery=True

    ### Channels table

    table='algorithmtypes'
    querylist.append('drop table if exists ' + table)
    querylist.append("create table " + table + " ( name text )") 

    if addentries:
        querylist.append("insert into " + table + " values ( 'on/off with deadband')") 

answer =raw_input('Rebuild channels table (y/N)?')
if answer=='y':
    runquery=True

    ### Channels table

    table='channels'
    querylist.append('drop table if exists ' + table)
    querylist.append("create table " + table + " ( channelindex integer primary key, name text unique, controlinput text , enabled integer default 0, outputsenabled integer default 0, controlupdatetime text, controlalgorithm text default 'on/off 1', controlrecipe text default 'none', recipestage integer default 0, recipestarttime real default 0, recipestagestarttime real default 0, setpointvalue real, controlvalue real, controlvaluetime text, positiveoutput text, negativeoutput text, action real default 0, mode text manual, statusmessage text, logpoints real)")

    if addentries:
        querylist.append("insert into " + table + " values (1, 'channel 1', 'none', 0, 0, '', 'on/off 1', 'none',0,0,0,65, '', '', 'output1', 'output2', 0, 'auto', '', 1000)")

if runquery:
    print(querylist)
    sqlitemultquery(database,querylist)

############################################
# authlog 


############################################
# device info 

runquery="False"
database = '/var/www/data/systemdata.db'
querylist=[]
 
answer =raw_input('Rebuild network table (y/N)?')
if answer=='y':
    runquery="True"

    table='network'
    querylist.append('drop table if exists ' + table)
    querylist.append("create table " + table + " ( IPAddress text, gateway text, WANaccess text, networkSSID text)") 
    querylist.append("insert into " + table + " values ( '', '','','' )")

answer =raw_input('Rebuild metadata table (y/N)?')
if answer=='y':
    runquery="True"

    table='metadata'
    querylist.append('drop table if exists ' + table)
    querylist.append("create table " + table + " (  devicename text, groupname text)") 
    querylist.append("insert into " + table + " values ( 'My CuPID', 'None' )")

answer =raw_input('Rebuild versions table (y/N)?')
if answer=='y':
    runquery=True

    ### About table

    table='versions'
    querylist.append('drop table if exists ' + table)
    querylist.append("create table " + table + " ( item text primary key,  version text, versiontime text, updatetime text)")

if runquery:
    print(querylist)

    sqlitemultquery(database,querylist)

############################################
# recipesdata

runquery=False
database = '/var/www/data/recipedata.db'
querylist=[]
 
answer =raw_input('Rebuild recipes table (y/N)?')
if answer=='y':
    runquery="True"

    table='stdreflow'
    querylist.append('drop table if exists ' + table)
    querylist.append("create table " + table + " ( stagenumber integer default 1, stagelength real default 0, setpointvalue real default 0, lengthmode text default 'setpoint', controlalgorithm text default 'on/off 1')") 
    if addentries:
        querylist.append("insert into " + table + " values ( 1, 300, 40, 'setpoint','on/off 1')")
        querylist.append("insert into " + table + " values ( 2, 600, 60, 'setpoint','on/off 1')")
        querylist.append("insert into " + table + " values ( 3, 600, 100, 'setpoint','on/off 1')")
        querylist.append("insert into " + table + " values ( 4, 300, 40, 'setpoint','on/off 1')")

if runquery:
    print(querylist)

    sqlitemultquery(database,querylist)

