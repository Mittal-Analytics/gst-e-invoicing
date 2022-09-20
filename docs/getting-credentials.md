# Obtaining credentials for using the APIs

There are 2 ways to use the APIs:
1. Through Direct Access (for tax-payers with turnover > ₹500 Crores)
2. Through pass-through APIs from GSPs (for ERP softwares and other tax-payers)

## Using Direct Access

Tax payers with a turnover over ₹ 500 Crores can use APIs directly. There are 4 major credentials:
1. Client ID
2. Client Secret
3. API Username
4. API Password

You need to create the above credentials on sandbox. After testing the APIs on sandbox, you need to submit a report. You can then generate the credentials on production portal too.

## Using pass-through APIs from GSPs

For users who don't have a direct access, they can use the pass-through APIs. Pass-through APIs are a mirror of direct APIs but are provided by a GSP (GST Suvidha Partners).

The APIs provided by GSPs are either passthrough APIs or custom APIs.
- Passthrough APIs: these are mirror of direct APIs. These use the same payloads and encryption like the direct APIs.
- Custom APIs: these are custom APIs with different functionalities than the direct APIs.

These are the commercials and supported APIs of few of the GSPs.

|  **GSP**  | **Cost / year** | **API Calls** | **Provide Passthrough APIs** |
|:---------:|:---------------:|:-------------:|:----------------------------:|
| ClearTax  |          45,000 |        10,000 |             ❌               |
| GST Zen   |           8,500 |        25,000 |             ❌               |
| Adaequare |           7,000 |        10,000 |             ✅               |
| WebTel    |          25,000 |        25,000 |             ✅               |
| TaxPro    |           1,050 |         5,000 |             ✅               |