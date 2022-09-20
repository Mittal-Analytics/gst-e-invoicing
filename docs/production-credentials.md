# Generating Credentials for Production

Credentials for production consist of:
- Client ID (check below)
- Client Secret (check below)
- API Username (created on https://einvoice1.gst.gov.in)
- API Password (created on https://einvoice1.gst.gov.in)

There are 2 primary ways to get the Client ID and Client Secret in production:
- Direct Access (for companies with turnover > 500 Cr) 
- Through GSP

## Getting credentials from GSP (GST Suvidha Provider)

GSP's have 2 types of integrations:
- **Passthrough GSP APIs:** These APIs use the same headers and encryption as the direct APIs but have a different endpoints
- **ASP APIs:** These are custom APIs provided by the GSP. **These won't work with this library.**

These are the commercials of few of the GSPs we could get details from:
|  **GSP**  | **Min Cost / yr** | **API Calls** | **Passthrough<br>GSP credentials** |
|:---------:|:-------------------:|:-------------:|:------------------------------:|
| ClearTax  |               45000 |         10000 |                    ❌                    |
| GST Zen   |                8500 |         25000 |                    ❌                    |
| Adaequare |                7000 |         10000 |                    ✅                    |
| WebTel |                25000 |         25000 |                    ✅                    |
| TaxPro |                1050 |         5000 |                    ✅                    |
