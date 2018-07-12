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
from splunk_http_handler import SplunkHecHandler
import logging

log = logging.getLogger('')
log.addHandler(SplunkHecHandler(host, token))
log.setLevel('INFO')
log.info("Testing")
```
You should see the log message in your Splunk search.


## HTTPS Example
Additional parameters can be passed to specify port, protocol, ssl verification.

```
log.addHandler(SplunkHecHandler(host, token, port=8080, protocol='https', ssl_verify=True))
```

## Metadata Override
To override source, sourcetype and hostname:

```
log.addHandler(SplunkHecHandler(
                host, token, port=8080, protocol='https', ssl_verify=True,
                source='custom_source_string', sourcetype='valid_sourceytype', hostname='hostname_override'
                ))
```
