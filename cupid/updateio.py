#!/usr/bin/env python

__author__ = 'Colin Reese'
__copyright__ = 'Copyright 2014, Interface Innovations'
__credits__ = ['Colin Reese']
__license__ = 'Apache 2.0'
__version__ = '1.0'
__maintainer__ = 'Colin Reese'
__email__ = 'support@interfaceinnovations.org'
__status__ = 'Development'


def updateiodata(database):
    # This recreates all input and output tables based on the interfaces table.
    # Thus way we don't keep around stale data values. We could at some point incorporate
    # a retention feature that keeps them around in case they disappear temporarily.
    # It also reads the elements if they are enabled and it's time to read them

    import pilib
    import traceback
    import RPi.GPIO as GPIO

    allowedGPIOaddresses = [18, 23, 24, 25, 4, 17, 21, 22]

    logconfig = pilib.getlogconfig()

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    tables = pilib.gettablenames(pilib.controldatabase)
    if 'interfaces' in tables:
        interfaces = pilib.readalldbrows(pilib.controldatabase, 'interfaces')
    else:
        pilib.writedatedlogmsg(pilib.iolog, 'interfaces table not found. Exiting', 1,
                               logconfig['iologlevel'])
        return
    if 'inputs' in tables:
        previnputs = pilib.readalldbrows(pilib.controldatabase, 'inputs')

        # Make list of IDs for easy indexing
        previnputids = []
        for input in previnputs:
            previnputids.append(input['id'])
    else:
        previnputs = []
        previnputids = []

    if 'outputs' in tables:
        prevoutputs = pilib.readalldbrows(pilib.controldatabase, 'outputs')

        # Make list of IDs for easy indexing
        prevoutputids = []
        prevoutputvalues = []
        for output in prevoutputs:
            prevoutputids.append(output['id'])
            prevoutputvalues.append(output['value'])
    else:
        prevoutputs = {}
        prevoutputids = []

    if 'defaults' in tables:
        defaults = pilib.readalldbrows(pilib.controldatabase, 'defaults')[0]
        defaultinputpollfreq = defaults['inputpollfreq']
        defaultoutputpollfreq = defaults['outputpollfreq']
    else:
        defaults = []
        defaultinputpollfreq = 60
        defaultoutputpollfreq = 60

    if 'indicators' in tables:
        indicatornames = []
        previndicators = pilib.readalldbrows(pilib.controldatabase, 'indicators')
        for indicator in previndicators:
            indicatornames.append(indicator['name'])
    else:
        previndicators = []
        indicatornames = []

    # We drop all inputs and outputs and recreate
    # Add all into one query so there is no time when the IO don't exist.

    querylist = []
    querylist.append('delete from inputs')
    querylist.append('delete from outputs')

    # This is temporary. Clearing the table here and adding entries below can result in a gap in time
    # where there are no database indicator entries. This is not too much of a problem with indicators, as we
    # update the hardware explicitly after we add the entries. If the interface queries the table during
    # this period, however, we could end up with an apparently empty table.
    # The reason they are updated within the table rather than compiling
    pilib.sqlitequery(pilib.controldatabase, 'delete from indicators')

    owfsupdate = False
    for interface in interfaces:
        if interface['interface'] == 'I2C':
            pilib.writedatedlogmsg(pilib.iolog, 'Processing I2C interface' + interface['name'], 3,
                                   logconfig['iologlevel'])
            if interface['enabled']:
                pilib.writedatedlogmsg(pilib.iolog, 'I2C Interface ' + interface['name'] + ' enabled', 3,
                                       logconfig['iologlevel'])
                if interface['type'] == 'DS2483':
                    pilib.writedatedlogmsg(pilib.iolog, 'Interface type is DS2483', 3,
                                           logconfig['iologlevel'])
                    owfsupdate = True
        elif interface['interface'] == 'USB':
            pilib.writedatedlogmsg(pilib.iolog, 'Processing USB interface' + interface['name'], 3,
                                   logconfig['iologlevel'])
            if interface['enabled']:
                pilib.writedatedlogmsg(pilib.iolog, 'USB Interface ' + interface['name'] + ' enabled', 3,
                                       logconfig['iologlevel'])
                if interface['type'] == 'DS9490':
                    pilib.writedatedlogmsg(pilib.iolog, 'Interface type is DS9490', 3,
                                           logconfig['iologlevel'])
                    owfsupdate = True
        elif interface['interface'] == 'LAN':
            pilib.writedatedlogmsg(pilib.iolog, 'Processing LAN interface' + interface['name'], 3,
                                   logconfig['iologlevel'])
            if interface['enabled']:
                pilib.writedatedlogmsg(pilib.iolog, 'LAN Interface ' + interface['name'] + ' enabled', 3,
                                       logconfig['iologlevel'])
                if interface['type'] == 'MBTCP':
                    pilib.writedatedlogmsg(pilib.iolog, 'Interface ' + interface['name'] + ' type is MBTCP',
                                           3, logconfig['iologlevel'])

                    try:
                        mbentries = processMBinterface(interface, prevoutputs, prevoutputids, previnputs, previnputids, defaults, logconfig)
                    except:
                        pilib.writedatedlogmsg(pilib.iolog,
                                               'Error processing MBTCP interface ' + interface['name'], 0,
                                               logconfig['iologlevel'])
                        errorstring = traceback.format_exc()
                        pilib.writedatedlogmsg(pilib.iolog,
                                               'Error of kind: ' + errorstring, 0,
                                               logconfig['iologlevel'])
                    else:
                        pilib.writedatedlogmsg(pilib.iolog,
                                               'Done processing MBTCP interface ' + interface['name'], 3,
                                               logconfig['iologlevel'])
                        querylist.extend(mbentries)

        elif interface['interface'] == 'GPIO':
            try:
                address = int(interface['address'])
            except KeyError:
                pilib.writedatedlogmsg(pilib.iolog, 'GPIO address key not found for ' + interface['name'], 1,
                                       logconfig['iologlevel'])
                continue

            pilib.writedatedlogmsg(pilib.iolog, 'Processing GPIO interface ' + str(interface['address']), 3,
                                   logconfig['iologlevel'])

            if address in allowedGPIOaddresses:
                pilib.writedatedlogmsg(pilib.iolog, 'GPIO address' + str(address) + ' allowed', 4,
                                       logconfig['iologlevel'])

                # Check if interface is enabled
                if interface['enabled']:
                    GPIOentries = processGPIOinterface(interface, prevoutputs, prevoutputvalues, prevoutputids,
                                                       previnputs, previnputids, defaults, logconfig)
                    querylist.extend(GPIOentries)
                else:
                    pilib.writedatedlogmsg(pilib.iolog, 'GPIO address' + str(address) + ' disabled', 4,
                                           logconfig['iologlevel'])
                    GPIO.setup(address, GPIO.IN)
            else:
                pilib.writedatedlogmsg(pilib.iolog,
                                       'GPIO address' + str(address) + ' not allowed. Bad things can happen. ', 4,
                                       logconfig['iologlevel'])
        elif interface['interface'] == 'SPI0':
            pilib.writedatedlogmsg(pilib.iolog, 'Processing SPI0', 1, logconfig['iologlevel'])
            if interface['type'] == 'SPITC':
                import readspi

                spidata = readspi.readspitc(0)
                spitcentries = readspi.recordspidata(database, spidata)
                querylist.extend(spitcentries)

            if interface['type'] == 'CuPIDlights':
                import spilights

                spilightsentries, setlist = spilights.getCuPIDlightsentries('indicators', 0, previndicators)
                querylist.extend(spilightsentries)
                spilights.updatelightsfromdb(pilib.controldatabase, 'indicators', 0)
                spilights.setspilights(setlist, 0)

        elif interface['interface'] == 'SPI1':
            pilib.writedatedlogmsg(pilib.iolog, 'Processing SPI1', 1, logconfig['iologlevel'])

            if interface['type'] == 'CuPIDlights':
                import spilights

                spilightsentries, setlist = spilights.getCuPIDlightsentries('indicators', 1, previndicators)
                querylist.extend(spilightsentries)
                spilights.setspilights(setlist, 1)

    # Set tables
    querylist.append(pilib.makesinglevaluequery('systemstatus', 'lastiopoll', pilib.gettimestring()))

    if owfsupdate:
        from owfslib import runowfsupdate

        devices, owfsentries = runowfsupdate(execute=False)
        querylist.extend(owfsentries)

    pilib.writedatedlogmsg(pilib.iolog, 'Executing query:  ' + str(querylist), 5, logconfig['iologlevel'])
    try:
        pilib.sqlitemultquery(pilib.controldatabase, querylist)
    except:
        errorstring = traceback.format_exc()
        pilib.writedatedlogmsg(pilib.iolog, 'Error executing query, message:  ' + errorstring, 0, logconfig['iologlevel'])
        pilib.writedatedlogmsg(pilib.errorlog, 'Error executing updateio query, message:  ' + errorstring)
        pilib.writedatedlogmsg(pilib.errorlog, 'Query:  ' + str(querylist))


def updateioinfo(database, table):
    from pilib import readalldbrows, sqlitedatumquery, sqlitemultquery

    tabledata = readalldbrows(database, table)
    querylist = []
    for item in tabledata:
        itemid = item['id']
        name = sqlitedatumquery(database, 'select name from ioinfo where id=\'' + itemid + '\'')
        querylist.append(database, 'update ' + table + ' set name=\'' + name + '\' where id = \'' + itemid + '\'')
    if querylist:
        sqlitemultquery(querylist)


def testupdateio(times):
    from pilib import controldatabase

    for i in range(times):
        updateiodata(controldatabase)


def processMBinterface(interface, prevoutputs, prevoutputids, previnputs, previnputids, defaults, logconfig):
    from netfun import readMBcodedaddresses, MBFCfromaddress
    import pilib
    # get all modbus reads that have the same address from the modbus table
    try:
        modbustable = pilib.readalldbrows(pilib.controldatabase, 'modbustcp')
    except:
        pilib.writedatedlogmsg(pilib.iolog, 'Error reading modbus table', 0, logconfig['iologlevel'])
    else:
        pilib.writedatedlogmsg(pilib.iolog, 'Read modbus table', 4, logconfig['iologlevel'])

    querylist = []
    for entry in modbustable:
        # Get name from ioinfo table to give it a colloquial name
        # First we have to give it a unique ID. This is a bit difficult with modbus

        if entry['mode'] == 'read':
            shortmode = 'R'
        elif entry['mode'] == 'write':
            shortmode = 'W'
        elif entry['mode'] == 'readwrite':
            shortmode = 'RW'
        else:
            pilib.writedatedlogmsg(pilib.iolog, 'modbus mode error', 1, logconfig['iologlevel'])
        try:
            mbid = entry['interfaceid'] + '_' + str(entry['register']) + '_' + str(entry['length']) + '_' + shortmode
        except KeyError:
            pilib.writedatedlogmsg(pilib.iolog, 'Cannot form mbid due to key error', 0, logconfig['iologlevel'])
            return

        pilib.writedatedlogmsg(pilib.iolog, 'Modbus ID: ' + mbid, 4, logconfig['iologlevel'])

        mbname = pilib.sqlitedatumquery(pilib.controldatabase, "select name from ioinfo where id='" + mbid + "'")
        polltime = pilib.gettimestring()
        if entry['interfaceid'] == interface['id']:
            # For now, we're going to read them one by one. We'll assemble these into block reads
            # in the next iteration
            if entry['mode'] == 'read':

                # Get previous metadata and data
                # Get input settings and keep them if the input previously existed

                if mbid in previnputids:
                    pollfreq = previnputs[previnputids.index(mbid)]['pollfreq']
                    ontime = previnputs[previnputids.index(mbid)]['ontime']
                    offtime = previnputs[previnputids.index(mbid)]['offtime']
                    prevvalue = previnputs[previnputids.index(mbid)]['offtime']
                    prevpolltime = previnputs[previnputids.index(mbid)]['offtime']

                    pilib.writedatedlogmsg(pilib.iolog,
                                           'Restoring values from previous inputids: pollfreq = ' + str(
                                               pollfreq) + ' ontime = ' + str(ontime) + ' offtime = ' + str(
                                               offtime), 3, logconfig['iologlevel'])

                else:
                    # set values to defaults if it did not previously exist
                    try:
                        pollfreq = defaults['defaultinputpollfreq']
                    except:
                        pollfreq = 60
                    ontime = ''
                    offtime = ''
                    prevvalue = ''
                    prevpolltime = ''
                    pilib.writedatedlogmsg(pilib.iolog,
                                           'Setting values to defaults, defaultinputpollfreq = ' + str(pollfreq), 3, logconfig['iologlevel'])

                # Read data
                try:
                    readresult = readMBcodedaddresses(interface['address'], entry['register'], entry['length'])
                except:
                    pilib.writedatedlogmsg(pilib.iolog, 'Uncaught reror reading modbus value', 0, logconfig['iologlevel'])
                else:
                    if readresult['statuscode'] == 0:
                        values = readresult['values']
                        try:
                            FC = MBFCfromaddress(int(entry['register']))
                        except ValueError:
                            pilib.writedatedlogmsg(pilib.iolog, 'Malformed address for FC determination : ' + str(entry['address']), 0, logconfig['iologlevel'])
                        else:
                            pilib.writedatedlogmsg(pilib.iolog, 'Function code : ' + str(FC), 4, logconfig['iologlevel'])
                        returnvalue = 0
                        if len(values) > 0:
                            pilib.writedatedlogmsg(pilib.iolog, 'Multiple values returned', 4, logconfig['iologlevel'])
                            if not entry['bigendian']:
                                try:
                                    values.reverse()
                                except AttributeError:
                                    pilib.writedatedlogmsg(pilib.iolog, 'Error on reverse of MB values: ' + str(values), 0, logconfig['iologlevel'])
                            if entry['format'] == 'float32':
                                import struct
                                byte2 = values[0] % 256
                                byte1 = (values[0] - byte2)/256
                                byte4 = values[1] % 256
                                byte3 = (values[1] - byte4)/256

                                byte1hex = chr(byte1)
                                byte2hex = chr(byte2)
                                byte3hex = chr(byte3)
                                byte4hex = chr(byte4)
                                hexstring = byte1hex + byte2hex + byte3hex + byte4hex

                                returnvalue = struct.unpack('>f',hexstring)[0]
                            else:
                                for index, val in enumerate(values):
                                    if FC in [0, 1]:
                                        returnvalue += val * 2 ** index
                                    elif FC in [3, 4]:
                                        returnvalue += val * 256 ** index
                                    else:
                                         pilib.writedatedlogmsg(pilib.iolog, 'Invalid function code', 0, logconfig['iologlevel'])
                        else:
                            returnvalue = values[0]
                        if entry['options'] != '':
                            options = pilib.parseoptions(entry['options'])
                            if 'scale' in options:
                                # try:
                                    returnvalue = returnvalue * float(options['scale'])
                                # except:
                                #     pilib.writedatedlogmsg(pilib.iolog, 'Error on scale operation', 0, logconfig['iologlevel'])
                            if 'precision' in options:
                                # try:
                                    returnvalue = round(returnvalue, int(options['precision']))
                                # except:
                                #     pilib.writedatedlogmsg(pilib.iolog, 'Error on precision operation', 0, logconfig['iologlevel'])


                        pilib.writedatedlogmsg(pilib.iolog, 'Values read: ' + str(values), 4, logconfig['iologlevel'])
                        pilib.writedatedlogmsg(pilib.iolog, 'Value returned: ' + str(returnvalue), 4, logconfig['iologlevel'])


                        # Contruct entry for newly acquired data
                        querylist.append('insert into inputs values (\'' + mbid + '\',\'' + interface['id'] + '\',\'' +
                            interface['type'] + '\',\'' + str(entry['register']) + '\',\'' + mbname + '\',\'' + str(
                            returnvalue) + "','','" + str(polltime) + '\',\'' + str(pollfreq) + "','" + ontime + "','" + offtime + "')")

                    else:
                        pilib.writedatedlogmsg(pilib.iolog, 'Statuscode ' + str(readresult['statuscode']) + ' on MB read : ' + readresult['message'] , 0, logconfig['iologlevel'])

                        # restore previous value and construct entry if it existed (or not)
                        querylist.append('insert into inputs values (\'' + mbid + '\',\'' + interface['interface'] + '\',\'' +
                            interface['type'] + '\',\'' + str(entry['register']) + '\',\'' + mbname + '\',\'' + str(prevvalue) + "','','" + str(prevpolltime) + '\',\'' + str(pollfreq) + "','" + ontime + "','" + offtime + "')")


    pilib.writedatedlogmsg(pilib.iolog, 'Querylist: ' + str(querylist) , 4, logconfig['iologlevel'])

    return querylist

def processGPIOinterface(interface, prevoutputs, prevoutputvalues, prevoutputids, previnputs, previnputids, defaults, logconfig):
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    import pilib

    options = pilib.parseoptions(interface['options'])
    address = int(interface['address'])

    # TODO : respond to more options, like pullup and pulldown

    pilib.writedatedlogmsg(pilib.iolog, 'GPIO address' + str(address) + ' enabled', 4,
                           logconfig['iologlevel'])
    # Get name from ioinfo table to give it a colloquial name
    gpioname = pilib.sqlitedatumquery(pilib.controldatabase, 'select name from ioinfo where id=\'' +
                                                             interface['id'] + '\'')
    polltime = pilib.gettimestring()

    querylist = []
    # Append to inputs and update name, even if it's an output (can read status as input)
    if options['mode'] == 'output':
        pilib.writedatedlogmsg(pilib.iolog, 'Setting output mode for GPIO address' + str(address), 3,
                               logconfig['iologlevel'])
        try:
            GPIO.setup(address, GPIO.OUT)
        except TypeError:
            pilib.writedatedlogmsg(pilib.iolog, 'You are trying to set a GPIO with the wrong variable type : ' +
                                                str(type(address)), 0, logconfig['iologlevel'])
            pilib.writedatedlogmsg(pilib.iolog, 'Exiting interface routine for  ' + interface['id'], 0, logconfig['iologlevel'])
            return

        # Set the value of the gpio.
        # Get previous value if exists
        if interface['id'] in prevoutputids:
            value = prevoutputvalues[prevoutputids.index(interface['id'])]

        else:
            value = 0
        if value == 1:
            GPIO.output(address, True)
            pilib.writedatedlogmsg(pilib.iolog, 'Setting output ON for GPIO address' + str(address), 3,
                                   logconfig['iologlevel'])
        else:
            GPIO.output(address, False)
            pilib.writedatedlogmsg(pilib.iolog, 'Setting output OFF for GPIO address' + str(address), 3,
                                   logconfig['iologlevel'])

        # Get output settings and keep them if the GPIO previously existed
        if interface['id'] in prevoutputids:
            pollfreq = prevoutputs[prevoutputids.index(interface['id'])]['pollfreq']
            ontime = prevoutputs[prevoutputids.index(interface['id'])]['ontime']
            offtime = prevoutputs[prevoutputids.index(interface['id'])]['offtime']
        else:
            try:
                pollfreq = defaults['defaultoutputpollfreq']
            except:
                pollfreq = 60
            ontime = ''
            offtime = ''

        # Add entry to outputs tables
        querylist.append('insert into outputs values (\'' + interface['id'] + '\',\'' +
                         interface['interface'] + '\',\'' + interface['type'] + '\',\'' + str(
            address) + '\',\'' +
                         gpioname + '\',\'' + str(value) + "','','" + str(polltime) + '\',\'' +
                         str(pollfreq) + "','" + ontime + "','" + offtime + "')")
    else:
        GPIO.setup(address, GPIO.IN)
        value = GPIO.input(address)
        pilib.writedatedlogmsg(pilib.iolog, 'Setting input mode for GPIO address' + str(address), 3,
                               logconfig['iologlevel'])

        # Get input settings and keep them if the GPIO previously existed
        if interface['id'] in previnputids:
            pollfreq = previnputs[previnputids.index(interface['id'])]['pollfreq']
            ontime = previnputs[previnputids.index(interface['id'])]['ontime']
            offtime = previnputs[previnputids.index(interface['id'])]['offtime']
            pilib.writedatedlogmsg(pilib.iolog,
                                   'Restoring values from previous inputids: pollfreq = ' + str(
                                       pollfreq) + ' ontime = ' + str(ontime) + ' offtime = ' + str(
                                       offtime), 3, logconfig['iologlevel'])

        else:
            try:
                pollfreq = defaults['defaultinputpollfreq']
            except:
                pollfreq = 60
            ontime = ''
            offtime = ''
            pilib.writedatedlogmsg(pilib.iolog,
                                   'Setting values to defaults, defaultinputpollfreq = ' + str(
                                       pollfreq), 3, logconfig['iologlevel'])
    querylist.append(
        'insert into inputs values (\'' + interface['id'] + '\',\'' + interface['interface'] + '\',\'' +
        interface['type'] + '\',\'' + str(address) + '\',\'' + gpioname + '\',\'' + str(
            value) + "','','" +
        str(polltime) + '\',\'' + str(pollfreq) + "','" + ontime + "','" + offtime + "')")

    return querylist


if __name__ == '__main__':
    from pilib import controldatabase

    updateiodata(controldatabase)

