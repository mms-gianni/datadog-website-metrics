import json
import pycurl
import sys 

from checks import AgentCheck

class Websitestats(AgentCheck):

    def __init__(self, name, init_config, agentConfig, instances=None):

        AgentCheck.__init__(self, name, init_config, agentConfig, instances=instances)

    def check(self, instance):

        # Make sure plugin is configured
        if instance.get("site", None) is None:
            raise Exception("Check is not configured: add site")
        site = instance.get('site')
        if instance.get("url", None) is None:
            raise Exception("Check is not configured: add url")
        url = instance.get('url')

        # gather data
        devnull = open('/dev/null', 'w')
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)                    #set url
        c.setopt(pycurl.WRITEFUNCTION, devnull.write)
        c.setopt(pycurl.VERBOSE, 0)                  # no output
        c.setopt(pycurl.FOLLOWLOCATION, 1)  
        content = c.perform()                        #execute 
        dns_time = c.getinfo(pycurl.NAMELOOKUP_TIME) #DNS time
        conn_time = c.getinfo(pycurl.CONNECT_TIME)   #TCP/IP 3-way handshaking time
        starttransfer_time = c.getinfo(pycurl.STARTTRANSFER_TIME)  #time-to-first-byte time
        total_time = c.getinfo(pycurl.TOTAL_TIME)  #last requst time
        c.close()

        # format data
        data = { "dns_time": dns_time, 
                 "conn_time": conn_time,
                 "starttransfer_time": starttransfer_time,
                 "total_time": total_time
               }
        self.log.debug(data)

        # send the data
        try:
            for field, value in data.iteritems():
                # self.log.debug(data)
                tags = ['site:%s' % site]
                self.gauge('website.stats.'+field, value, tags=tags)
        except ValueError:
            self.log.error("Failed to save data")
            return