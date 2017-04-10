import json
import logging
import time
import requests
import ast

class SplunkHttpHandler(logging.Handler):
    URL_PATTERN = "http://{0}:{1}/services/collector"

    def __init__(self, host, port, token, hostname='localhost', source='avadel_ims'):
        logging.Handler.__init__(self)
        self.host = host
        self.port = port
        self.token = token
        self.hostname = hostname
        self.source = source

    def emit(self, record):
        url = self.URL_PATTERN.format(self.host, self.port)

        body = { 'log_level': record.levelname }
        try:
            body.update(ast.literal_eval(record.msg))
        except:
            body.update({ 'message': record.msg })

        data = json.dumps({
            'host': self.hostname, 'source': self.source, 'time': time.time(),
            'event': body
        })

        try:
            r = requests.post(url, data=data, headers={ 'Authorization': "Splunk {}".format(self.token) }, verify=False)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print e
