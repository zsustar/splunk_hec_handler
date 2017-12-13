import json
import logging
import time
import requests
import ast
from socket import gethostname

class SplunkHttpHandler(logging.Handler):
    URL_PATTERN = "{0}://{1}:{2}/services/collector"

    def __init__(self, host, token, **kwargs):
        logging.Handler.__init__(self)
        self.host = host
        self.token = token
        if kwargs is not None:
            self.port = kwargs.pop('port') if 'port' in kwargs.keys() else 8080
            self.proto = kwargs.pop('proto') if 'proto' in kwargs.keys() else 'https'
            self.ssl_verify = kwargs.pop('ssl_verify') if 'ssl_verify' in kwargs.keys() else True
            self.source = kwargs.pop('source') if 'source' in kwargs.keys() else None
            self.sourcetype = kwargs.pop('sourcetype') if 'sourcetype' in kwargs.keys() else None
            self.hostname = kwargs.pop('hostname') if 'hostname' in kwargs.keys() else gethostname()
            # Remaining args
            self.kwargs = kwargs.copy()

    def emit(self, record):
        url = self.URL_PATTERN.format(self.proto, self.host, self.port)

        body = { 'log_level': record.levelname }
        try:
            # If record.msg is dict, leverage it as is
            body.update(ast.literal_eval(str(record.msg)))
        except:
            body.update({ 'message': record.msg })

        event = dict({'host': self.hostname, 'source': self.source, 'sourcetype': self.sourcetype, 'event': body})
        event.update(self.kwargs)

        # Use timestamp from event if available
        if body.has_key('time'):
            event['time'] = body['time']
        else:
            event['time'] = time.time()

        data = json.dumps(event, sort_keys=True)

        try:
            r = requests.post(url, data=data, headers={ 'Authorization': "Splunk {}".format(self.token) },
                              verify=self.ssl_verify)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print e
