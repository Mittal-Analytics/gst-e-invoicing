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
)
from src.gst_irn.codes import states
from src.gst_irn.converters import to_buyer
from src.gst_irn.generators import get_invoice, get_seller_dtls

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
        # self.assertTrue(session._auth_sek)

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

        place_of_supply = states.KARNATAKA
        seller_dtls = get_seller_dtls(
            gstin=CONFIG["GSTIN"],
            lgl_nm="Foobar",
            addr1="foobar",
            loc="foobar",
            pin=226001,
            stcd=states.UTTAR_PRADESH,
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
        self.assertTrue("Irn" in einvoice.raw, msg=einvoice)
