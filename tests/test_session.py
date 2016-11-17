from rets.configuration import Configuration
from rets.session import Session
import unittest


class SessionTester(unittest.TestCase):

    def test_session(self):
        c = Configuration('1.7.2')
        c.login_url = 'http://matrix.swflamls.com/rets/login.ashx'
        c.username = "bDNFRMcGreevy2013"
        c.password = "eidcmw092"
        s = Session(c)
        self.assertIsNotNone(s)
        s.login()
        system = s.get_system_metadata()
        print(system)