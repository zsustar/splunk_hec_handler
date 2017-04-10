* Example of usage
```
from splunk_http_handler import SplunkHttpHandler
import logging

log = logging.getLogger('')
log.addHandler(SplunkHttpHandler(host, port, token, host_name_override, source))
log.setLevel('INFO')
log.info("Testing")
```
You should see the log message in your Splunk search.
