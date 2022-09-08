import base64
import json
import logging
import os
from pprint import pformat

import requests
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_pem_public_key


def _encrypt_with_rsa_pub_key(message, public_key_str) -> str:
    """
    encrypt message with RSA by given public key
    """
    public_key = load_pem_public_key(public_key_str.encode())
    encrypted_msg = public_key.encrypt(
        plaintext=message, padding=asym_padding.PKCS1v15()
    )
    encoded_encrypted_msg = base64.b64encode(encrypted_msg).decode()
    return encoded_encrypted_msg


def _decrypt_with_aes(message, key) -> bytes:
    """
    decrypts the message using the given key
    """
    message = base64.b64decode(message)
    key = base64.b64decode(key)
    decryptor = Cipher(
        algorithm=algorithms.AES(key=key), mode=modes.ECB()
    ).decryptor()
    decrypted = decryptor.update(message) + decryptor.finalize()
    return decrypted


def _encrypt_with_aes(message, key) -> str:
    """
    encrypts the message with the given AES key
    """
    key = base64.b64decode(key)
    encryptor = Cipher(
        algorithm=algorithms.AES(key=key), mode=modes.ECB()
    ).encryptor()

    # pad the message with PKCS7
    padder = sym_padding.PKCS7(128).padder()
    message = padder.update(message) + padder.finalize()

    # encrypt the message
    message = encryptor.update(message)

    # base64 encode the message
    message = base64.b64encode(message).decode()
    return message


def _get_decrypted_sek(sek, app_key):
    decrypted_sek = _decrypt_with_aes(sek, app_key)
    # unpad - with pkcs7
    unpadder = sym_padding.PKCS7(128).unpadder()
    un_padded = unpadder.update(decrypted_sek)
    un_padded = un_padded + unpadder.finalize()
    # base64 encoding
    decrypted_sek = base64.b64encode(un_padded).decode()
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


def _raise_error(response):
    try:
        err = response.json()
    except Exception:
        try:
            err = response.content
        except Exception:
            err = response

    err = pformat(err, indent=4)
    logging.error(err)
    raise RequestError()


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
        public_key_str = self.public_key
        payload = _encrypt_with_rsa_pub_key(payload, public_key_str)

        payload = {"Data": payload}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            response = response.json()
            data = response["Data"]
            self._auth_token = data["AuthToken"]
            self._auth_sek = _get_decrypted_sek(data["Sek"], app_key)
        else:
            _raise_error(response)

    def _get_request_headers(self):
        return {
            "client-id": self.client_id,
            "client-secret": self.client_secret,
            "gstin": self.gstin,
            "user_name": self.username,
            "AuthToken": self._auth_token,
        }

    def get_gst_info(self, party_gstin):
        if not self._auth_sek:
            raise GenerateTokenError()

        url = f"{self._base_url}/eivital/v1.04/Master/gstin/{party_gstin}"

        headers = self._get_request_headers()
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response = response.json()
            encrypted_data = response["Data"]
            data = (
                _decrypt_with_aes(encrypted_data, self._auth_sek)
                .decode()
                .strip()
            )
            # strip non-printable unicode bytes in the end
            data = "".join(d for d in data if d.isprintable())
            return json.loads(data)
        else:
            _raise_error(response)

    def generate_e_invoice(self, invoice):
        if not self._auth_sek:
            raise GenerateTokenError()

        url = f"{self._base_url}/eicore/v1.03/Invoice"

        # convert payload to json string
        data = json.dumps(invoice)
        payload = data.encode()

        # encrypt payload
        encrypt_message = _encrypt_with_aes(payload, self._auth_sek)
        payload = {"Data": encrypt_message}
        headers = self._get_request_headers()
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            response = response.json()
            if response["Status"] == 1:
                encrypted_data = response["Data"]
                data = (
                    _decrypt_with_aes(encrypted_data, self._auth_sek)
                    .decode()
                    .strip()
                )
                # strip non-printable unicode bytes in the end
                data = "".join(d for d in data if d.isprintable())
                return json.loads(data)
            else:
                _raise_error(response)
        else:
            _raise_error(response)
