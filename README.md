# Python library for GST's E-invoicing portal

This is the python library for interacting with GST's E-invoicing portal.

## Usage

```python
from gst_irn import Session, Invoice, InvoiceItem, InvoiceItemTax, InvoiceItemDiscount

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

session.get_token()

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

# can access 
print(einvoice.json)
# {
#     'qr_code': 'foobar',
#     '...': '...',
# }
```

## Technical details

Schema Spec: https://www.cbic.gov.in/resources/htdocs-cbec/gst/notfctn-60-central-tax-english-2020.pdf
Simplified Spec: https://einvoice1.gst.gov.in/Documents/EINVOICE_SCHEMA.xlsx

The key's used in JSON file are CamelCase.  The attributes we use in the Python library are snake_case version of the same.
