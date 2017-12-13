* Example of usage
```
from splunk_http_handler import SplunkHttpHandler
import logging

log = logging.getLogger('')
log.addHandler(SplunkHttpHandler(host, token))
log.setLevel('INFO')
log.info("Testing")
```
You should see the log message in your Splunk search.

Additiona parameters can be passed to specify port, protocol, ssl verification, source, sourcetype, and hostname.

for example:

```
log.addHandler(SplunkHttpHandler(host, token, port=8080, protocol='https', ssl_verify=True))
```
