# Python library for GST's E-invoicing portal

This is the python library for interacting with GST's E-invoicing portal.

## Usage

```python
from gst_irn import Session, Invoice, InvoiceItem

session = Session(
    'GSTIN',
    client_id='CLIENT_ID',
    client_secret='CLIENT_SECRET',
    username='USERNAME',
    password='PASSWORD',
    app_key='APP_KEY',
    is_sandbox=True,
    force_generate=False,
)

session.generate_token()

# create invoice object
# use Session.get_party to automatically fetch details
# or use Party() to provide details manually
seller = session.get_party('SELLER_GSTIN')
buyer = session.get_party('BUYER_GSTIN')
items = [
    InvoiceItem(
        hsn_sac='HSN_SAC',
    )
]

# provide document details for the invoice
invoice = Invoice(
    no="DOC/0001",
    dt=dt.date(2022, 5, 19),
    items=items,
    seller=seller,
    buyer=buyer,
)

# submit and get the e-invoice
einvoice = session.generate_einvoice(invoice)

# access irn and qr-code
print(einvoice['Irn'])
# prints irn

# print qr-code
from gst_irn.qr import get_qr_code_image_base64
qr_code_image = get_qr_code_image_base64(einvoice['SignedQRCode'])
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
pip install -r requirements/requirements-dev.txt

# provide credentials
cp .env.sample .env
# edit and update the credentials in .env file
vi .env

# running tests
python -m unittest
```
