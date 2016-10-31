import unittest
from rets import client
from mock import patch


class ClientTester(unittest.TestCase):

    def test_login(self):
        with patch('rets.client.RETSClient.session.get') as mock_get:
            mock_get.return_value.text = '<RETS ReplyCode="0" ReplyText="Operation Success.">\n' \
                                             '<RETS-RESPONSE>\n' \
                                                 'MemberName=\n' \
                                                 'User=testagent,NULL,NULL\n' \
                                                 'Broker=\n' \
                                                 'MetadataVersion=1.11.75983\n' \
                                                 'MetadataTimestamp=2016-10-28T12:25:16Z\n' \
                                                 'MinMetadataTimestamp=2016-10-28T12:25:16Z\n' \
                                                 'Login=http://mls.com/rets/Login.ashx\n' \
                                                 'Logout=http://mls.com/rets/Logout.ashx\n' \
                                                 'Search=http://mls.com/rets/Search.ashx\n' \
                                                 'GetMetadata=http://mls.com/rets/GetMetadata.ashx\n' \
                                                 'GetObject=http://amls.com/rets/GetObject.ashx\n' \
                                                 'Update=http://mls.com/rets/Update.ashx\n' \
                                                 'PostObject=http://mls.com/rets/PostObject.ashx\n' \
                                             '</RETS-RESPONSE>\n' \
                                         '</RETS>'
            mock_get.return_value.status_code = 200

            rets_client = client.RETSClient(login_url="http://mls.com/rets/login.ashx",
                                            rets_version='RETS/1.7.2',
                                            username='testagent',
                                            password='testpass')

        self.assertIsNotNone(rets_client)

    def test_set_metadata(self):
        pass
