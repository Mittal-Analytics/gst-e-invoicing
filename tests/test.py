import unittest
import uuid

from dotenv import dotenv_values

from src.gst_irn import (
    Session,
    get_doc_dtls,
    get_ewb_dtls,
    get_item,
    get_tran_dtls,
    get_val_dtls,
    qr,
)
from src.gst_irn.codes import States
from src.gst_irn.converters import to_buyer
from src.gst_irn.generators import get_invoice, get_seller_dtls
from src.gst_irn.session import RequestError
from tests.snapshot import compare_snapshot

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
        session.generate_token()
        self.assertTrue(session._auth_token)
        self.assertTrue(session._auth_sek)

    def test_get_party_details(self):
        session = Session(
            gstin=CONFIG["GSTIN"],
            client_id=CONFIG["CLIENT_ID"],
            client_secret=CONFIG["CLIENT_SECRET"],
            username=CONFIG["USERNAME"],
            password=CONFIG["PASSWORD"],
            public_key=CONFIG["PUBLIC_KEY"],
            is_sandbox=True,
        )
        session.generate_token()
        details = session.get_gst_info("29AAACP7879D1Z0")
        self.assertEqual(
            details.get("TradeName"), "TALLY SOLUTIONS PVT LTD", msg=details
        )
        self.assertEqual(
            details.get("AddrBnm"), "AMR TECH PARK II B", msg=details
        )
        self.assertEqual(details.get("AddrLoc"), "HONGASANDRA")
        self.assertEqual(details.get("DtReg"), "2017-07-01")

    def test_generate_e_invoice(self):
        session = Session(
            gstin=CONFIG["GSTIN"],
            client_id=CONFIG["CLIENT_ID"],
            client_secret=CONFIG["CLIENT_SECRET"],
            username=CONFIG["USERNAME"],
            password=CONFIG["PASSWORD"],
            public_key=CONFIG["PUBLIC_KEY"],
            is_sandbox=True,
        )
        session.generate_token()

        place_of_supply = States.KARNATAKA.value
        seller_dtls = get_seller_dtls(
            gstin=CONFIG["GSTIN"],
            lgl_nm="Foobar",
            addr1="foobar",
            loc="foobar",
            pin=226001,
            stcd=States.UTTAR_PRADESH.value,
        )
        buyer_info = session.get_gst_info("29AWGPV7107B1Z1")
        buyer_dtls = to_buyer(buyer_info, place_of_supply)

        invoice = get_invoice(
            tran_dtls=get_tran_dtls(),
            doc_dtls=get_doc_dtls(
                typ="inv",
                no=str(uuid.uuid4())[:16],
                dt="12/11/2021",
            ),
            seller_dtls=seller_dtls,
            buyer_dtls=buyer_dtls,
            item_list=[
                get_item(
                    sl_no="1",
                    is_servc="Y",
                    hsn_cd="998431",
                    unit_price=100,
                    tot_amt=100,
                    ass_amt=100,
                    gst_rt=12.0,
                    igst_amt=12,
                    tot_item_val=112,
                )
            ],
            val_dtls=get_val_dtls(
                ass_val=100,
                igst_val=12,
                tot_inv_val=112,
            ),
            ewb_dtls=get_ewb_dtls(
                distance=10,
            ),
        )
        einvoice = session.generate_e_invoice(invoice)
        self.assertTrue("Irn" in einvoice, msg=einvoice)

    def test_qr_code(self):
        qr_code = "eyJhbGciOiJSUzI1NiIsImtpZCI6IkVEQzU3REUxMzU4QjMwMEJBOUY3OTM0MEE2Njk2ODMxRjNDODUwNDciLCJ0eXAiOiJKV1QiLCJ4NXQiOiI3Y1Y5NFRXTE1BdXA5NU5BcG1sb01mUElVRWMifQ.eyJkYXRhIjoie1wiU2VsbGVyR3N0aW5cIjpcIjA5QUFKQ003MTkxRTFaNVwiLFwiQnV5ZXJHc3RpblwiOlwiMjlBV0dQVjcxMDdCMVoxXCIsXCJEb2NOb1wiOlwiMzVkN2RmOGQtZmNlNy00OVwiLFwiRG9jVHlwXCI6XCJJTlZcIixcIkRvY0R0XCI6XCIxMi8xMS8yMDIxXCIsXCJUb3RJbnZWYWxcIjoxMTIsXCJJdGVtQ250XCI6MSxcIk1haW5Ic25Db2RlXCI6XCI5OTg0MzFcIixcIklyblwiOlwiMzk5N2Q2ZGJlNTg1ZGJmYzkzYTg1NWNmMmFhZDFhNDEyYWM3ZGYwMjMxYWI3ODc1ODUxYTE1ZTFiYTNmNGRmNFwiLFwiSXJuRHRcIjpcIjIwMjItMDktMDkgMTM6MzM6MDBcIn0iLCJpc3MiOiJOSUMifQ.RPd1hjjuky7Xcs550YTUXXISjrd-g11OrUZn1pS9uDq1Er-wHNeFmWmI72kEbYsL-tofo5mepnqAVKfJDeUZlGk_s597IiZMobmJb2yvEtbPiOs5Hy7lTQav3iD3XtdWIoKp26WqH1RBSCAQQEpzRwMCVO6G7oh9Uq5kf4GI1wuyj0aJT7ThNOrsM5cEyAoDTfdWvkr9MJdNLFt7mBaLMfEAyHe4DJEWJaPENJoicRwifon6FV7zGXcz1Wbxjg12o31470vaaKs2niOD-GBpkQ7W0p-Ac47CG8u2Z_q6QdFflAAWYVzGINwff_bioyXFDVdzt7RJwCDY_a7RKVvd8g"

        html = qr.get_qr_code_image_html(qr_code)
        compare_snapshot(html, "tests/test_assets/qr_code.html")

    def test_get_e_invoice_by_irn(self):
        session = Session(
            gstin=CONFIG["GSTIN"],
            client_id=CONFIG["CLIENT_ID"],
            client_secret=CONFIG["CLIENT_SECRET"],
            username=CONFIG["USERNAME"],
            password=CONFIG["PASSWORD"],
            public_key=CONFIG["PUBLIC_KEY"],
            is_sandbox=True,
        )
        session.generate_token()

        invoice = {
            "Version": "1.1",
            "TranDtls": {"TaxSch": "GST", "SupTyp": "B2B"},
            "DocDtls": get_doc_dtls(
                typ="inv",
                no=str(uuid.uuid4())[:16],
                dt="12/09/2022",
            ),
            "SellerDtls": {
                "Gstin": "09AAJCM7191E1Z5",
                "LglNm": "MITTAL ANALYTICS PRIVATE LIMITED",
                "Addr1": "NIKHILESH PALACE FIRST FLOOR 17/4 ASHOK MARG",
                "Loc": "LUCKNOW",
                "Pin": 226001,
                "Stcd": "9",
            },
            "BuyerDtls": {
                "Gstin": "37AABCA7365E2ZP",
                "LglNm": "AVANTI FEEDS LIMITED",
                "Pos": "37",
                "Addr1": ", VEMULURU ROAD",
                "Loc": "VEMULURU",
                "Pin": 534350,
                "Stcd": "37",
            },
            "ItemList": [
                {
                    "SlNo": "4",
                    "IsServc": "Y",
                    "HsnCd": "998431",
                    "UnitPrice": 100,
                    "IgstAmt": 12,
                    "TotAmt": 100,
                    "AssAmt": 100,
                    "GstRt": 12.0,
                    "TotItemVal": 112,
                }
            ],
            "ValDtls": {"TotInvVal": 112, "AssVal": 100, "IgstVal": 12},
            "EwbDtls": {"Distance": 10},
        }
        einvoice = session.generate_e_invoice(invoice)

        # assert duplicate IRN is raised for same document
        with self.assertLogs("src.gst_irn.session", level="ERROR") as cm:
            with self.assertRaises(RequestError) as err:
                _ = session.generate_e_invoice(invoice)
        msg, resp = err.exception.args
        self.assertEqual(msg, "action failed")
        self.assertTrue(resp["InfoDtls"][0]["Desc"]["Irn"], einvoice["Irn"])

        # verify document by sending irn
        duplicate = session.get_e_invoice_by_irn(einvoice["Irn"])
        self.assertEqual(duplicate, einvoice)
