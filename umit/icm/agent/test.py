#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Zhongjie Wang <wzj401@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

try:
    execfile("F:\\workspace\\PyWork\\icm-agent\\umit\\icm\\agent\\UmitImporter.py")
except:
    pass

__all__ = ['test_by_id', 'test_name_by_id', 'WebsiteTest', 'ServiceTest']

TEST_PACKAGE_VERSION = '1.0'
TEST_PACKAGE_VERSION_INT = 1

import hashlib
import re
import sys
import time

from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, ClientCreator, ClientFactory
from twisted.web.client import Agent, HTTPDownloader
from twisted.web.http_headers import Headers
from twisted.web._newclient import ResponseDone

from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
from umit.icm.agent.rpc.message import *

if sys.platform == "win32":
    # On Windows, the best timer is time.clock()
    default_timer = time.clock
else:
    # On most other platforms the best timer is time.time()
    default_timer = time.time

def generate_report_id(list_):
    m = hashlib.md5()
    for item in list_:
        m.update(str(item))
    report_id = m.hexdigest()
    return report_id

########################################################################
class Test(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

    def prepare(self, param):
        """Setup parameters and prepare for running"""
        raise NotImplementedError('You need to implement this method')

    def execute(self):
        raise NotImplementedError('You need to implement this method')

########################################################################
class WebsiteTest(Test):
    def __init__(self):
        """Constructor"""
        self.url = None
        self.status_code = 0
        self.pattern = None
        self._agent = Agent(reactor)

    def prepare(self, param):
        """Prepare for the test"""
        self.url = param['url']
        if 'pattern' in param:
            self.pattern = re.compile(param['pattern'])

    def execute(self):
        """Run the test"""
        g_logger.info("Testing website: %s" % self.url)
        defer_ = self._agent.request('GET',
                                    self.url,
                                    Headers({'User-Agent':
                                             ['ICM Website Test']}),
                                    None)
        self.time_start = default_timer()
        defer_.addCallback(self._handle_response)
        defer_.addErrback(self._handle_err)
        return defer_
    
    def _handle_err(self, failure):
        g_logger.critical('>>> %s' % failure)
        self.status_code = response.code
        g_logger.critical(self.status_code)
        g_logger.critical(dir(response))

    def _handle_response(self, response):
        """Result Handler (generate report)"""
        time_end = default_timer()
        self.status_code = response.code
        self.response_time = time_end - self.time_start
        #print(self.url)
        #print(str(self.status_code) + ' ' + response.phrase)
        #print("Response time: %fs" % (self.response_time))
        #print(response.headers)
        report = self._generate_report()

        theApp.statistics.tests_done = theApp.statistics.tests_done + 1
        if 1 in theApp.statistics.tests_done_by_type:
            theApp.statistics.tests_done_by_type[1] = \
                  theApp.statistics.tests_done_by_type[1] + 1
        else:
            theApp.statistics.tests_done_by_type[1] = 0

        if response.code == 200:
            if self.pattern is not None:
                response.deliverBody(ContentExaminer(self.url,
                                                     self.pattern))
        return report

    def _generate_report(self):
        report = WebsiteReport()
        report.header.agentID = theApp.peer_info.ID
        report.header.timeUTC = int(time.time())
        report.header.timeZone = 8
        report.header.testID = 1
        report.header.reportID = generate_report_id([report.header.agentID,
                                                     report.header.timeUTC,
                                                     report.header.testID])
        #report.header.traceroute
        report.report.websiteURL = self.url
        report.report.statusCode = self.status_code
        report.report.responseTime = (int)(self.response_time * 1000)
        #...
        theApp.statistics.reports_generated = \
              theApp.statistics.reports_generated + 1
        return report

    class ContentExaminer(Protocol):
        def __init__(self, url, pattern):
            """Constructor"""
            self.url = url
            self.content = ""
            self.pattern = pattern

        def dataReceived(self, bytes):
            self.content = ''.join((self.content, bytes))

        def connectionLost(self, reason):
            if reason.check(ResponseDone):
                match = self.pattern.search(self.content)
                if (match is not None):
                    g_logger.info("Content unchanged.")
                else:
                    g_logger.info("Content changed.")
            else:
                g_logger.error("The connection was broken. [%s]" % self.url)

########################################################################
class ServiceTest(Test):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.service = None
        self._done = False

    def prepare(self, param):
        self.service = param['service']

    def execute(self):
        g_logger.info("Testing service: %s" % self.service)
        self.defer_ = defer.Deferred()
        return self.defer_

########################################################################
class FTPTest(Test):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.service_name = 'ftp'
        self.host = None
        self.port = 21
        self.username = 'anonymous'
        self.password = 'icm-agent@umitproject.org'

    def prepare(self, param):
        self.host = param['host']
        if 'port' in param:
            self.port = param['port']
        if 'username' in param:
            self.username = param['username']
        if 'password' in param:
            self.password = param['password']

    def execute(self):
        from twisted.protocols.ftp import FTPClient
        creator = ClientCreator(reactor, FTPClient, self.username, self.password)
        d = creator.connectTCP(self.host, self.port)
        d.addCallback(self._connectionMade)
        d.addErrback(self._connectionFailed)
        self.time_start = default_timer()

    def _connectionMade(self, ftpClient):
        # execute pwd cmd
        ftpClient.pwd().addCallbacks(self._success, self._fail)

    def _connectionFailed(self, f):
        print(f)
        self.status_code = -1
        time_end = default_timer()
        self.response_time = time_end - self.time_start
        self._generate_report()

    def _success(self, response):
        print(response)
        self.status_code = 0
        time_end = default_timer()
        self.response_time = time_end - self.time_start
        self._generate_report()

    def _fail(self, error):
        print(error)
        self.status_code = -1
        time_end = default_timer()
        self.response_time = time_end - self.time_start
        self._generate_report()

    def _generate_report(self):
        report = ServiceReport()
        report.header.agentID = theApp.peer_info.ID
        report.header.timeUTC = int(time.time())
        report.header.timeZone = 8
        report.header.testID = 2
        report.header.reportID = generate_report_id([report.header.agentID,
                                                     report.header.timeUTC,
                                                     report.header.testID])
        #report.header.traceroute
        report.report.serviceName = self.service_name
        report.report.statusCode = self.status_code
        report.report.responseTime = (int)(self.response_time * 1000)
        #...
        theApp.statistics.reports_generated = \
              theApp.statistics.reports_generated + 1
        return report

########################################################################
class SMTPTest(Test):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.service_name = 'smtp'

    def prepare(self, param):
        pass

    def execute(self):
        pass

########################################################################
class POP3Test(Test):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.service_name = 'pop3'

    def prepare(self, param):
        pass

    def execute(self):
        pass

########################################################################
class IMAPTest(Test):
    """"""
    from twisted.mail import imap4

    class SimpleIMAP4Client(imap4.IMAP4Client):
        greetDeferred = None

        def connectionMade(self):
            print("connected.")

        def connectionLost(self, reason):
            print(reason)

        def serverGreeting(self, caps):
            print(caps)

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.service_name = 'imap'
        self.host = None
        self.port = 143
        self.username = ''
        self.password = ''

    def prepare(self, param):
        self.host = param['host']
        if 'port' in param:
            self.port = param['port']
        #if 'username' in param:
            #self.username = param['username']
        #if 'password' in param:
            #self.password = param['password']

        self.factory = ClientFactory()
        self.factory.protocol = self.SimpleIMAP4Client()

    def execute(self):
        reactor.connectTCP(self.host, self.port, self.factory)

    def _success(self, data):
        print(data)

    def _fail(self, failure):
        print(failure)


test_by_id = {
    0: Test,
    1: WebsiteTest,
    2: ServiceTest,
    3: FTPTest,
    4: SMTPTest,
    5: POP3Test,
    6: IMAPTest,
}

test_name_by_id = {
    0: 'Test',
    1: 'WebsiteTest',
    2: 'ServiceTest',
    3: 'FTPTest',
    4: 'SMTPTest',
    5: 'POP3Test',
    6: 'IMAPTest',
}

ALL_TESTS = ['WebsiteTest', 'FTPTest', 'SMTPTest', 'POP3Test', 'IMAPTest']
SUPPORTED_SERVICES = ['FTP', 'SMTP', 'POP3', 'IMAP']
#import inspect
#clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
#for clsname,cls in clsmembers:
    #if clsname.endswith('Test') and clsname != 'Test':
        #ALL_TESTS.append(clsname)


if __name__ == "__main__":
    #test1 = WebsiteTest()
    #test1.prepare({'url': 'http://www.baidu.com', 'pattern': 'baidu'})
    #test1.execute()
    #test2 = WebsiteTest()
    #test2.prepare({'url': 'https://www.alipay.com', 'pattern': 'baidu'})
    #test2.execute()
    #test3 = FTPTest()
    #test3.prepare({'host': 'ftp.secureftp-test.com', 'port': 21,
                   #'username': 'test', 'password': 'test'})
    #test3.execute()
    test4 = IMAPTest()
    test4.prepare({'host': 'imap.gmail.com'})
    test4.execute()

    reactor.callLater(5, reactor.stop)
    reactor.run()
    g_logger.info("finished")