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
        pretransfer_time = c.getinfo(pycurl.PRETRANSFER_TIME)
        redirect_time = c.getinfo(pycurl.REDIRECT_TIME)
        redirect_count = c.getinfo(pycurl.REDIRECT_COUNT)
        size_download = c.getinfo(pycurl.SIZE_DOWNLOAD)
        speed_download = c.getinfo(pycurl.SPEED_DOWNLOAD)
        content_length_download = c.getinfo(pycurl.CONTENT_LENGTH_DOWNLOAD)
        num_connects = c.getinfo(pycurl.NUM_CONNECTS)
        total_time = c.getinfo(pycurl.TOTAL_TIME)
        c.close()

        # format data
        data = { "dns_time": dns_time, 
                 "conn_time": conn_time,
                 "starttransfer_time": starttransfer_time,
                 "pretransfer_time": pretransfer_time,
                 "redirect_time": redirect_time,
                 "redirect_count": redirect_count,
                 "size_download": size_download,
                 "speed_download": speed_download,
                 "content_length_download": content_length_download,
                 "num_connects": num_connects,
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