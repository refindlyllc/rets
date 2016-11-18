from rets.configuration import Configuration
from rets.session import Session
import unittest


class SessionTester(unittest.TestCase):

    def test_session(self):
        c = Configuration('1.7.2')
        c.login_url = os.environ.get('RETS_LOGIN_URL')
        c.username = os.environ.get('RETS_USER')
        c.password = os.environ.get('RETS_PASS')
        s = Session(c)
        self.assertIsNotNone(s)
        s.login()
        system = s.get_system_metadata()
        print(system)