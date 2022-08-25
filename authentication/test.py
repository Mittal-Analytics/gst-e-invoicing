import unittest

from dotenv import dotenv_values

from authentication.session import Session

CONFIG = dotenv_values(".env")


class AuthTokenTestCase(unittest.TestCase):
    def setUp(self):
        self.session = Session(
            gstin=CONFIG["GSTIN"],
            client_id=CONFIG["CLIENT_ID"],
            client_secret=CONFIG["CLIENT_SECRET"],
            username=CONFIG["USERNAME"],
            password=CONFIG["PASSWORD"],
            public_key=CONFIG["PUBLIC_KEY"],
            is_sandbox=True,
        )

    def test_get_auth_token(self):
        auth_response = self.session.get_token()
        status = auth_response.get("Status")
        self.assertEqual(status, 1, msg=auth_response)

    def test_get_party_details(self):
        party_gstin_details = self.session.get_party_details(
            party_gstin=CONFIG["GSTIN"]
        )
        self.assertEqual(party_gstin_details.get("Gstin"), CONFIG["GSTIN"])
        self.assertEqual(
            party_gstin_details.get("TradeName"),
            "MITTAL ANALYTICS PRIVATE LIMITED",
        )
        self.assertEqual(
            party_gstin_details.get("AddrBnm"), "NIKHILESH PALACE"
        )
        self.assertEqual(party_gstin_details.get("AddrLoc"), "LUCKNOW")
        self.assertEqual(party_gstin_details.get("DtReg"), "2017-07-01")
