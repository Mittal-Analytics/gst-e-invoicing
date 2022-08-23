import unittest

from dotenv import dotenv_values

from authentication.session import Session

CONFIG = dotenv_values(".env")


class AuthTokenTestCase(unittest.TestCase):
    def test_get_auth_token(self):
        session = Session(
            gstin=CONFIG["GSTIN"],
            client_id=CONFIG["CLIENT_ID"],
            client_secret=CONFIG["CLIENT_SECRET"],
            username=CONFIG["USERNAME"],
            password=CONFIG["PASSWORD"],
            public_key=CONFIG["PUBLIC_KEY"],
            is_sandbox=True,
        )
        token = session.get_token()
        status = token.get("Status")
        self.assertEqual(status, 1, msg=token)
