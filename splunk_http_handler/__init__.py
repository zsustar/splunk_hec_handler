import json
import logging
import time
import requests
import ast
import socket

class SplunkHttpHandler(logging.Handler):
    URL_PATTERN = "{0}://{1}:{2}/services/collector"
    TIMEOUT = 2

    def __init__(self, host, token, **kwargs):
        self.host = host
        self.token = token
        if kwargs is not None:
            self.port = kwargs.pop('port') if 'port' in kwargs.keys() else 8080
            self.proto = kwargs.pop('proto') if 'proto' in kwargs.keys() else 'https'
            self.ssl_verify = kwargs.pop('ssl_verify') if 'ssl_verify' in kwargs.keys() else True
            self.source = kwargs.pop('source') if 'source' in kwargs.keys() else None
            self.sourcetype = kwargs.pop('sourcetype') if 'sourcetype' in kwargs.keys() else None
            self.hostname = kwargs.pop('hostname') if 'hostname' in kwargs.keys() else socket.gethostname()
            # Remaining args
            self.kwargs = kwargs.copy()

        try:
            s = socket.socket()
            s.settimeout(self.TIMEOUT)
            s.connect((self.host, self.port))
            self.r = requests.session()
            self.r.max_redirects = 1
            self.r.verify = self.ssl_verify
            self.r.headers['Authorization'] = "Splunk {}".format(self.token)
            logging.Handler.__init__(self)
        except Exception as e:
            logging.error("Failed to connect to remote Splunk server (%s:%s). Exception: %s"
                          % (self.host, self.port, e))
        finally:
            s.close()


    def emit(self, record):
        url = self.URL_PATTERN.format(self.proto, self.host, self.port)

        body = { 'log_level': record.levelname }
        try:
            if record.msg.__class__ == dict:
                # If record.msg is dict, leverage it as is
                body.update(ast.literal_eval(str(record.msg)))
            elif record.msg.count('{}') > 0:
                # handle log messages with positional arguments
                for arg in record.args:
                    record.msg = record.msg.replace('{}', str(arg), 1)
                body.update({ 'message': record.msg })
            elif len(record.args) > 0:
                # for log messages with string formatting
                body.update({ 'message': record.msg % record.args })
            else:
                body.update({ 'message': record.msg })
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
            req = self.r.post(url, data=data, timeout=self.TIMEOUT)

            req.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logging.debug("Failed to emit record to Splunk server (%s:%s).  Exception raised: %s"
                          % (self.host, self.port, e))
