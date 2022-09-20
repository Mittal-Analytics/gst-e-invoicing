# GST E-Invoicing Python Library

GST E-Invoicing library makes it easy to interact with GST E-Invoicing portal. It allows you to generate IRNs using your custom application.

## Quick Overview

You can install the package using PIP

```bash
pip install gst-e-invoicing
```

You will also need to obtain the API credentials to use the library.

- [Guide for obtaining the API credentials](./getting-credentials.md)

The library supports both the direct access as well as pass-through APIs provided by GSPs.

```python
from gst_irn import Session, get_invoice, get_seller_dtls
from gst_irn.codes import States

with open('public_key.pem') as f:
    public_key = f.read()

session = Session(
    'GSTIN',
    client_id='CLIENT_ID',
    client_secret='CLIENT_SECRET',
    username='USERNAME',
    password='PASSWORD',
    public_key=public_key,
    # use the sandbox url, or production url
    # or pass-through APIs provided by GSPs
    base_url='https://einv-apisandbox.nic.in',
)

session.generate_token()

# create invoice object
# can also use the helper functions for the same
invoice = {
    "Version": "1.1",
    "TranDtls": {"TaxSch": "GST", "SupTyp": "B2B"},
    "DocDtls": {
        "Typ": "inv",
        "No": "221",
        "Dt": "21/09/2021",
    },
    "SellerDtls": {
        "Gstin": "09GSTNUMBER1Z5",
        "LglNm": "PARTY NAME",
        "Addr1": "Seller Address",
        "Loc": "City",
        "Pin": 111111,
        "Stcd": States.UTTAR_PRADESH.value,
    },
    "BuyerDtls": {
        "Gstin": "37GSTNUMBER2ZP",
        "LglNm": "BUYER NAME",
        "Pos": States.KOLKATA.value,
        "Addr1": "Buyer Address",
        "Loc": "City",
        "Pin": 555555,
        "Stcd": States.KOLKATA.value,
    },
    "ItemList": [
        {
            "SlNo": "1",
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

# submit and get the e-invoice
einvoice = session.generate_einvoice(invoice)

# access irn and qr-code
print(einvoice['Irn'])
# prints irn

# print qr-code
from gst_irn.qr import get_qr_code_image_html
qr_code_image = get_qr_code_image_html(einvoice['SignedQRCode'])
qr_code_image
# prints <img src="...">
```
