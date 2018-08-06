import json
import logging
import time
import requests
import ast
import socket


class SplunkHecHandler(logging.Handler):
    """
    This module returns a python logging handler capable of sending logs records to a Splunk HTTP Event Collector
    listener.  Log records can be simple string or dictionary.  In the latter case, if the sourcetype is configured
    to be _json (or variant), JSON format of the log message will be preserved.

    Example:
        import logging
        from splunk_hec_handler import SplunkHecHandler
        logger = logging.getLogger('SplunkHecHandlerExample')
        logger.setLevel(logging.DEBUG)
        # If using self-signed certificate, set ssl_verify to False
        # If using http, set proto to http
        splunk_handler = splunk_http_handler.SplunkHttpHandler('splunkfw.domain.tld',
                            'EA33046C-6FEC-4DC0-AC66-4326E58B54C3',
                            port=8888, proto='https', ssl_verify=True,
                            source="HEC_example")
        logger.addHandler(splunk_handler)
        '''
        Following should result in a Splunk entry with _time set to current timestamp.
            { log_level: INFO
              message: Testing Splunk HEC Info message
            }
        '''
        logger.info("Testing Splunk HEC Info message")

        '''
        Following should result in a Splunk entry with _time of Monday, August 6, 2018 4:33:43 AM, and contain two
        custom fields (color, api_endpoint). Custom fields can be seen in verbose mode.
            { app: my demo
              error codes: [
                1
                23
                34
                456
                ]
            log_level: ERROR
            severity: low
            user: foobar
            }
        '''
        # See http://dev.splunk.com/view/event-collector/SP-CAAAE6P for 'fields'
        # To use fields, sourcetype must be specified and must allow for indexed field extractions
        dict_obj = {'time': 1533530023, 'fields': {'color': 'yellow', 'api_endpoint': '/results'},
                    'user': 'foobar', 'app': 'my demo', 'severity': 'low', 'error codes': [1, 23, 34, 456]}
        logger.error(dict_obj)

    Splunk remote logging configuration
    http://docs.splunk.com/Documentation/SplunkCloud/latest/Data/UsetheHTTPEventCollector
    http://docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector
    """
    URL_PATTERN = "{0}://{1}:{2}/services/collector/event"
    TIMEOUT = 2

    def __init__(self, host, token, **kwargs):
        """
        Creates a python logging handler, capable of sending logs to Splunk server
        :param host: Splunk server hostname or IP
        :param token: Splunk HEC Token
        (http://docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector#About_Event_Collector_tokens)
        :param \**kwargs:
            See below

        :keyword Arguments:
            port: 0-65535 port number of Splunk HEC listener
            proto: http | https
            ssl_verify: True|False.  Use False for self-signed certificates
            source: Override source value specified in Splunk HEC configuration.  None by default.
            sourcetype: Override sourcetype value specified in Splunk HEC configuration.  None by default.
            hostname: Specify custom host value.  Defaults to hostname returned by socket.gethostname()

            Any additional kwargs (to support future splunk API changes) are added to emitted log record.
            Unsupported kwargs are ignored by Splunk.
        """
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
            # Testing connectivity
            s = socket.socket()
            s.settimeout(self.TIMEOUT)
            s.connect((self.host, self.port))

            # Socket accessible.  Establish requests session
            self.r = requests.session()
            self.r.max_redirects = 1
            self.r.verify = self.ssl_verify
            self.r.headers['Authorization'] = "Splunk {}".format(self.token)
            logging.Handler.__init__(self)
        except Exception as e:
            logging.error("Failed to connect to remote Splunk server (%s:%s). Exception: %s"
                          % (self.host, self.port, e))
        else:
            s.close()

    def emit(self, record):
        """
        Send log record to Splunk HEC listener
        :param record: string or dictionary. String record is logged as 'message' in Splunk.
        Dictionary is preserved as JSON object.  log_level is set to requested log level.
        :return: None
        """
        url = self.URL_PATTERN.format(self.proto, self.host, self.port)

        body = {'log_level': record.levelname}
        try:
            if record.msg.__class__ == dict:
                # If record.msg is dict, leverage it as is
                body.update(ast.literal_eval(str(record.msg)))
            elif record.msg.count('{}') > 0:
                # handle log messages with positional arguments
                for arg in record.args:
                    record.msg = record.msg.replace('{}', str(arg), 1)
                body.update({'message': record.msg})
            elif len(record.args) > 0:
                # for log messages with string formatting
                body.update({'message': record.msg % record.args})
            else:
                body.update({'message': record.msg})
        except Exception as e:
            logging.debug("Log record emit exception raised. Exception: %s " % e)
            body.update({'message': record.msg})

        event = dict({'host': self.hostname, 'source': self.source,
                      'sourcetype': self.sourcetype, 'event': body, 'fields': {}})
        event.update(self.kwargs)

        # fields
        # This specifies explicit custom fields that are separate from the main "event" data.
        # This method is useful if you don't want to include the custom fields with the event data,
        # but you want to be able to annotate the data with some extra information, such as where it came from.
        # http://dev.splunk.com/view/event-collector/SP-CAAAFB6
        if list(body.keys()).count('fields') and hasattr(body['fields'], 'items'):
            # Splunk indexing of event fails if field isn't str value
            for k,v in body.pop('fields').items():
                event['fields'][k] = str(v)

        # Use timestamp from event if available
        if hasattr(body, 'time'):
            event['time'] = body['time']
        elif list(body.keys()).count('time'):
            event['time'] = body.pop('time')
        else:
            event['time'] = time.time()

        data = json.dumps(event, sort_keys=True)

        try:
            req = self.r.post(url, data=data, timeout=self.TIMEOUT)

            req.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logging.debug("Failed to emit record to Splunk server (%s:%s).  Exception raised: %s"
                          % (self.host, self.port, e))