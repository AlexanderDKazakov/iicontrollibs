#!/usr/bin/env python

__author__ = "Colin Reese"
__copyright__ = "Copyright 2016, Interface Innovations"
__credits__ = ["Colin Reese"]
__license__ = "Apache 2.0"
__version__ = "1.0"
__maintainer__ = "Colin Reese"
__email__ = "support@interfaceinnovations.org"
__status__ = "Development"

import os
import sys
import inspect

top_folder = \
    os.path.split(os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0])))[0]
if top_folder not in sys.path:
    sys.path.insert(0, top_folder)


class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


def killprocbyname(name):
    import subprocess
    try:
        result = subprocess.check_output(['pgrep','hamachi'])
    except:
        # Error thrown means hamachi is not running
        print('catching error')
    else:
        split = result.split('\n')
        # print(split)
        for pid in split:
            if pid:
                # print(pid)
                subprocess.call(['kill', '-9', str(pid.strip())])
    return


def log(logfile, message, reqloglevel=1, currloglevel=1):
    from iiutilities.datalib import gettimestring
    if currloglevel >= reqloglevel:
        logfile = open(logfile, 'a')
        logfile.writelines([gettimestring() + ' : ' + message + '\n'])
        logfile.close()


class gmail:
    def __init__(self, server='smtp.gmail.com', port=587, subject='default subject', message='default message',
                 login='cupidmailer@interfaceinnovations.org', password='cupidmail', recipient='info@interfaceinnovations.org', sender='CuPID Mailer'):
        self.server = server
        self.port = port
        self.message = message
        self.subject = subject
        self.sender = sender
        self.login = login
        self.password = password
        self.recipient = recipient
        self.sender = sender

    def send(self):
        import smtplib

        headers = ['From:' + self.sender,
                  'Subject:' + self.subject,
                  'To:' + self.recipient,
                  'MIME-Version: 1.0',
                  'Content-Type: text/plain']
        headers = '\r\n'.join(headers)

        session = smtplib.SMTP(self.server, self.port)

        session.ehlo()
        session.starttls()
        session.ehlo
        session.login(self.login, self.password)

        session.sendmail(self.sender, self.recipient, headers + '\r\n\r\n' + self.message)
        session.quit()