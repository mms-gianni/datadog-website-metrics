import json
import pycurl
import sys 

from checks import AgentCheck

class Websitestats(AgentCheck):

    def __init__(self, name, init_config, agentConfig, instances=None):

        AgentCheck.__init__(self, name, init_config, agentConfig, instances=instances)

    def check(self, instance):