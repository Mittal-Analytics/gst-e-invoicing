import json
import unittest

from dotenv import dotenv_values

from authentication.session import (
    Session,
    doc_dtls,
    ewb_dtls,
    get,
    item_dtls,
    ship_dtls,
    tran_dtls,
    val_dtls,
)

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
        auth_data = self.session.get_auth_data()
        self.assertEqual(("AuthToken" in auth_data), True)
        self.assertEqual(("Sek" in auth_data), True)

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

    def test_generate_e_invoice(self):
        party_gstin = "29AWGPV7107B1Z1"
        invoice = self.session.generate_e_invoice(
            party_gstin=party_gstin,
            tran_dtls=get(
                tran_dtls,
                tax_sch="GST",
            ),
            doc_dtls=get(
                doc_dtls,
                typ="inv",
                no="doc/0001",
                dt="12/11/2021",
            ),
            item_list=get(
                item_dtls,
                sl_no="1",
                is_servc="Y",
                hsn_cd="998431",
                unit_price=100,
                igst_amt=12,
                tot_amt=100,
                ass_amt=100,
                gst_rt=12.0,
                tot_item_val=112,
            ),
            val_dtls=get(
                val_dtls,
                ass_val=100,
                tot_inv_val=112,
            ),
            ewb_dtls=get(
                ewb_dtls,
                distance=10,
            ),
        )
        self.assertEqual(invoice.get("Status"), 1)
