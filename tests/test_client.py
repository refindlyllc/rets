import unittest
from rets import client
from mock import patch


class ClientTester(unittest.TestCase):

    def test_login(self):
        with patch('rets.client.RETSClient.session.get') as mock_get:
            with open('tests/xml_responses/login_response_success.xml') as f:
                res = ''.join(f.readlines())
            mock_get.return_value.text = res
            mock_get.return_value.status_code = 200

            rets_client = client.RETSClient(login_url="http://mls.com/rets/login.ashx",
                                            rets_version='RETS/1.7.2',
                                            username='testagent',
                                            password='testpass')

        self.assertIsNotNone(rets_client)

    def test_set_metadata(self):
        pass
