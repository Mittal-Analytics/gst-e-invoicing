import base64
import json
import logging
import os
from pprint import pformat

import requests

from . import crypto

logger = logging.getLogger(__name__)


def _get_decrypted_sek(sek, app_key):
    decrypted_sek = crypto.decrypt_with_aes(sek, app_key, raw=True)

    # handle base64 encoding
    decrypted_sek = base64.b64encode(decrypted_sek).decode()
    return decrypted_sek


def _get_app_key() -> str:
    """
    creates a random app_key of 32 byte
    """
    aes_key = os.urandom(32)
    readable = base64.b64encode(aes_key).decode()
    return readable


class RequestError(Exception):
    pass


class GenerateTokenError(Exception):
    pass


def _raise_formatted_error(err, msg):
    fmt_err = pformat(err, indent=4)
    logger.error(fmt_err)
    raise RequestError(msg, err)


def _get_data_from_response(response, *, encryption_key):
    if response.status_code == 200:
        response = response.json()
        if response["Status"] == 1:
            data = response["Data"]
            if encryption_key:
                data = crypto.decrypt_with_aes(data, encryption_key)
                data = json.loads(data)
            return data
        else:
            _raise_formatted_error(response, "action failed")
    else:
        _raise_formatted_error(response.text, f"status {response.status_code}")


class Session:
    def __init__(
        self,
        gstin,
        client_id,
        client_secret,
        username,
        password,
        public_key,
        is_sandbox=True,
    ):
        self.gstin = gstin
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.public_key = public_key

        self._base_url = "https://einv-apisandbox.nic.in" if is_sandbox else ""

        self._auth_token = None
        self._auth_sek = None

    def generate_token(self, force_regenerate_token=False):
        app_key = _get_app_key()
        url = f"{self._base_url}/eivital/v1.04/auth"
        # request headers
        headers = {
            "client-id": self.client_id,
            "client-secret": self.client_secret,
            "gstin": self.gstin,
        }

        # request payload
        payload = {
            "UserName": self.username,
            "Password": self.password,
            "AppKey": app_key,
            "ForceRefreshAccessToken": force_regenerate_token,
        }
        # convert payload to json string
        payload = json.dumps(payload)

        # base64 encoding of payload
        payload = base64.b64encode(payload.encode())

        # encrypt using e-Invoice public Key
        payload = crypto.encrypt_with_rsa_pub_key(payload, self.public_key)

        payload = {"Data": payload}
        response = requests.post(url, json=payload, headers=headers)

        data = _get_data_from_response(response, encryption_key=None)
        self._auth_token = data["AuthToken"]
        self._auth_sek = _get_decrypted_sek(data["Sek"], app_key)

    def _get_request_headers(self):
        return {
            "client-id": self.client_id,
            "client-secret": self.client_secret,
            "gstin": self.gstin,
            "user_name": self.username,
            "AuthToken": self._auth_token,
        }

    def get_gst_info(self, party_gstin):
        """
        fetches and returns info for the given gst number
        """
        if not self._auth_sek:
            raise GenerateTokenError()

        url = f"{self._base_url}/eivital/v1.04/Master/gstin/{party_gstin}"

        headers = self._get_request_headers()
        response = requests.get(url, headers=headers)
        return _get_data_from_response(response, encryption_key=self._auth_sek)

    def generate_e_invoice(self, invoice):
        """
        generates and returns e-invoice for given invoice

        e-invoice contains IRN, QR-code and signature
        """
        if not self._auth_sek:
            raise GenerateTokenError()

        url = f"{self._base_url}/eicore/v1.03/Invoice"

        # convert payload to json string
        data = json.dumps(invoice)
        payload = data.encode()

        # encrypt payload
        payload = crypto.encrypt_with_aes(payload, self._auth_sek)
        payload = {"Data": payload}
        headers = self._get_request_headers()
        response = requests.post(url, json=payload, headers=headers)
        return _get_data_from_response(response, encryption_key=self._auth_sek)

    def get_e_invoice_by_irn(self, irn, sup_gstin=None):
        """
        returns e-invoice for an already generated irn
        """
        url = f"{self._base_url}/eicore/v1.03/Invoice/irn/{irn}"
        headers = self._get_request_headers()
        if sup_gstin:
            headers["sup_gstin"] = sup_gstin
        response = requests.get(url, headers=headers)
        return _get_data_from_response(response, encryption_key=self._auth_sek)
