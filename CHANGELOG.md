# Changelog

The changelog was added version 0.3.0 onwards.

## v0.7.1

The helpers provide a function to convert gst_info into buyer dict. Fixed it for dummy GSTs.

## v0.7.0

Removed EWB details from mandatory fields in generator functions.

## v0.6.0

Improved conversion of address from gst_info.

## v0.5.0

Added automatic re-use of auth-token. The auth-token generated at IRP (Invoice Registration Portal) is valid for 6 hours. The portal recommends re-using the same token till expiry. This is automatically done by the library now.

## v0.4.0

Added `session.get` and `session.post` methods. This allows us to use the API with any endpoint.

## v0.3.0

- Added support for passthrough APIs provided by GSPs (GST Suvidha Providers).
- Added docs around GSPs
- Added changelog
