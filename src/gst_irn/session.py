import base64
import datetime as dt
import json
import logging
import os
from hashlib import md5
from pathlib import Path
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


def _get_auth_token(session, force_regenerate_token):
    app_key = _get_app_key()
    url = f"{session.base_url}/eivital/v1.04/auth"
    # request headers
    headers = {
        "client-id": session.client_id,
        "client-secret": session.client_secret,
        "gstin": session.gstin,
    }
    if session.gsp_headers:
        headers.update(session.gsp_headers)

    # request payload
    payload = {
        "UserName": session.username,
        "Password": session.password,
        "AppKey": app_key,
        "ForceRefreshAccessToken": force_regenerate_token,
    }
    # convert payload to json string
    payload = json.dumps(payload)

    # base64 encoding of payload
    payload = base64.b64encode(payload.encode())

    # encrypt using e-Invoice public Key
    payload = crypto.encrypt_with_rsa_pub_key(payload, session.public_key)

    payload = {"Data": payload}
    response = requests.post(url, json=payload, headers=headers)

    data = _get_data_from_response(response, encryption_key=None)
    return data, app_key


def _get_store_path(cache_dir, session):
    # prepare dictionary of all session variables
    attr_dict = {
        a: getattr(session, a)
        for a in dir(session)
        if not a.startswith("_") and not callable(getattr(session, a))
    }

    # create a hash for session values
    repr = json.dumps(attr_dict, sort_keys=True)
    cache_key = md5(repr.encode()).hexdigest()

    filename = f"{cache_key}.json"
    store_path = Path(cache_dir) / filename
    return store_path


def _get_stored_token(cache_dir, session):
    store_path = _get_store_path(cache_dir, session)
    try:
        stored_token = json.loads(store_path.read_text())

        # check expiry
        expiry = dt.datetime.strptime(
            stored_token["expiry_time"], "%Y-%m-%d %H:%M:%S"
        )
        if expiry < (dt.datetime.now() + dt.timedelta(minutes=10)):
            stored_token = None

        # return tuple of token and sek
        else:
            stored_token = (stored_token["token"], stored_token["sek"])
    except Exception:
        stored_token = None
    return stored_token


def _store_token(cache_dir, session, expiry_time):
    store_path = _get_store_path(cache_dir, session)
    try:
        store_path.parent.mkdir(parents=True, exist_ok=True)
        obj = {
            "token": session._auth_token,
            "sek": session._auth_sek,
            "expiry_time": expiry_time,
        }
        store_path.write_text(json.dumps(obj))
    except Exception:
        pass


class Session:
    def __init__(
        self,
        gstin,
        client_id,
        client_secret,
        username,
        password,
        public_key,
        base_url="https://einv-apisandbox.nic.in",
        gsp_headers=None,
    ):
        self.gstin = gstin
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.public_key = public_key

        self.base_url = base_url
        self.gsp_headers = gsp_headers

        self._auth_token = None
        self._auth_sek = None

    def generate_token(
        self, force_regenerate_token=False, cache_dir="tokens_cache"
    ):
        stored_token = _get_stored_token(cache_dir, self)
        if stored_token and not force_regenerate_token:
            self._auth_token, self._auth_sek = stored_token
        else:
            data, app_key = _get_auth_token(self, force_regenerate_token)
            self._auth_token = data["AuthToken"]
            self._auth_sek = _get_decrypted_sek(data["Sek"], app_key)

            # cache token
            expiry_time = data["TokenExpiry"]
            _store_token(cache_dir, self, expiry_time)

    def _get_request_headers(self):
        headers = {
            "client-id": self.client_id,
            "client-secret": self.client_secret,
            "gstin": self.gstin,
            "user_name": self.username,
            "AuthToken": self._auth_token,
        }
        if self.gsp_headers:
            headers.update(self.gsp_headers)
        return headers

    def get(self, url, headers_extra=None):
        """
        sends get request to the given url along with authentication headers
        returns decrypted response
        """
        if not self._auth_sek:
            raise GenerateTokenError()

        headers = self._get_request_headers()
        if headers_extra:
            headers.update(headers_extra)

        response = requests.get(url, headers=headers)
        return _get_data_from_response(response, encryption_key=self._auth_sek)

    def post(self, url, data, headers_extra=None):
        """
        sends post request to the given url
        - adds authentication headers
        - encrypts the payload

        returns decrypted response
        """
        if not self._auth_sek:
            raise GenerateTokenError()

        # convert payload to json string
        data = json.dumps(data)
        payload = data.encode()

        # encrypt payload
        payload = crypto.encrypt_with_aes(payload, self._auth_sek)
        payload = {"Data": payload}
        headers = self._get_request_headers()
        if headers_extra:
            headers.update(headers_extra)

        response = requests.post(url, json=payload, headers=headers)
        return _get_data_from_response(response, encryption_key=self._auth_sek)

    def get_gst_info(self, party_gstin):
        """
        fetches and returns info for the given gst number
        """
        url = f"{self.base_url}/eivital/v1.04/Master/gstin/{party_gstin}"
        return self.get(url)

    def generate_e_invoice(self, invoice):
        """
        generates and returns e-invoice for given invoice

        e-invoice contains IRN, QR-code and signature
        """
        url = f"{self.base_url}/eicore/v1.03/Invoice"
        return self.post(url, invoice)

    def get_e_invoice_by_irn(self, irn, sup_gstin=None):
        """
        returns e-invoice for an already generated irn
        """
        url = f"{self.base_url}/eicore/v1.03/Invoice/irn/{irn}"
        return self.get(url)
