import unittest
import mock
import ast
import sys
import time
import logging
import json
sys.path.append('../splunk_http_handler')
from splunk_http_handler import SplunkHttpHandler

HOST = 'host'
PORT = 1234
TOKEN = 'token'
HOSTNAME = 'hostname'
TIMESTAMP = time.time()
SOURCE = 'source'
RECORD_PLAIN = 'plain text'
RECORD_DICT = "{ 'dict': 'record' }"
URL = "http://{0}:{1}/services/collector".format(HOST, PORT)

def mock_response(fixture=None, status=200):
    response = mock.Mock()
    if fixture is None:
        response.text = ''
    elif isinstance(fixture, dict):
        response.text = str(fixture)
    else:
        response.text = load_fixture(fixture)
    response.status_code = status
    return response

class TestSplunkHttpHandler(unittest.TestCase):
    def setUp(self):
        self.splunk = SplunkHttpHandler(
            host=HOST,
            port=PORT,
            token=TOKEN,
            hostname=HOSTNAME,
            source=SOURCE
        )

    def test_init(self):
        self.assertIsNotNone(self.splunk)
        self.assertIsInstance(self.splunk, SplunkHttpHandler)
        self.assertIsInstance(self.splunk, logging.Handler)
        self.assertEqual(self.splunk.host, HOST)
        self.assertEqual(self.splunk.port, PORT)
        self.assertEqual(self.splunk.token, TOKEN)
        self.assertEqual(self.splunk.hostname, HOSTNAME)
        self.assertEqual(self.splunk.source, SOURCE)

    @mock.patch('time.time', mock.MagicMock(return_value=TIMESTAMP))
    @mock.patch('splunk_http_handler.requests')
    def test_logging(self, requests):
        log = logging.getLogger('test')
        log.addHandler(self.splunk)
        log.warning('Hello')

        request_payload = json.dumps({
            'host': HOSTNAME,
            'source': SOURCE,
            'time': TIMESTAMP,
            'event': {
                'log_level': 'WARNING',
                'message': 'Hello'
            }
        })

        requests.post.response_value = mock_response()

        requests.post.assert_called_once_with(
            URL,
            headers={ 'Authorization': "Splunk {}".format(TOKEN) },
            verify=False,
            data=request_payload
        )

if __name__ == '__main__':
    unittest.main()
