# Python library for GST's E-invoicing portal

This is the python library for interacting with GST's E-invoicing portal.

## Usage

Install the library:

```bash
pip install gst-e-invoicing
```

Use it in your code:

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

## Technical details

Schema Spec: https://www.cbic.gov.in/resources/htdocs-cbec/gst/notfctn-60-central-tax-english-2020.pdf
Simplified Spec: https://einvoice1.gst.gov.in/Documents/EINVOICE_SCHEMA.xlsx

The key's used in JSON file are CamelCase.  The attributes we use in the Python library are snake_case version of the same.


## Development

Setting up dev environment:

```bash
# create and activate virtual env
python3 -m venv .venv
source .venv/bin/activate

# install requirements
pip install '.[dev]'

# provide credentials
cp .env.sample .env
# edit and update the credentials in .env file
vi .env

# running tests
python -m unittest
```
