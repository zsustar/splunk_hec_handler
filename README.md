# Features
1. Log messages to Splunk via HTTP Event Collector (HEC).  See [Splunk HEC Documentation](http://docs.splunk.com/Documentation/Splunk/latest/Data/AboutHEC)
2. All messages are logged as '_json' sourcetype by default.
3. A dictionary with 'log_level' and 'message' keys are constructed for logging records of type string.

![String log record representation in Splunk](https://github.com/vavarachen/splunk_http_handler/blob/master/resources/str_record.png)

4. Dictionary objects are preserved as JSON.

![Dictionary log record representation in Splunk](https://github.com/vavarachen/splunk_http_handler/blob/master/resources/dict_record.png)

5. If log record (dict) does not contains a '_time' field,  one is added with the value set to current time.

# Examples

## Basic
```
import logging
from splunk_hec_handler import SplunkHecHandler
logger = logging.getLogger('SplunkHecHandlerExample')
logger.setLevel(logging.DEBUG)

# If using self-signed certificate, set ssl_verify to False
# If using http, set proto to http
splunk_handler = SplunkHecHandler('splunkfw.domain.tld',
                    'EA33046C-6FEC-4DC0-AC66-4326E58B54C3',
                    port=8888, proto='https', ssl_verify=True,
                    source="HEC_example")
logger.addHandler(splunk_handler)

# Following should result in a Splunk entry of
#    { log_level: INFO
#      message: Testing Splunk HEC Info message
#    }

logger.info("Testing Splunk HEC Info message")

# Following should result in a Splunk entry of
#    { app: my demo
#      error codes: [
#        1
#        23
#        ]
#    log_level: ERROR
#    severity: low
#    user: foobar
#    }

dict_obj = {'user': 'foobar', 'app': 'my demo', 'severity': 'low', 'error codes': [1, 23]}
logger.error(dict_obj)
```

