import unittest

from authentication.session import Session


class AuthTokenTestCase(unittest.TestCase):
    def test_get_auth_token(self):
        session = Session()
        token = session.get_token()
        status = token.get("Status")
        self.assertEqual(status, 1, msg=token)
