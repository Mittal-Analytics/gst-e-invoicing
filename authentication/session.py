import base64
import json

import requests
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes


def encrypt_message(message, public_key_str):
    public_key = RSA.import_key(public_key_str)
    cipher = PKCS1_v1_5.new(public_key)
    encrypted_msg = cipher.encrypt(message)
    encoded_encrypted_msg = base64.b64encode(encrypted_msg).decode()
    return encoded_encrypted_msg


def get_app_key():
    aes_key = get_random_bytes(32)
    readable = base64.b64encode(aes_key).decode()
    return readable


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

        self._base_url = (
            "https://einv-apisandbox.nic.in/" if is_sandbox else ""
        )
        self.token = None

    def get_token(self, force_regenerate_token=False):
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
            "AppKey": get_app_key(),
            "ForceRefreshAccessToken": force_regenerate_token,
        }

        # convert payload to json string
        payload = json.dumps(payload)

        # base64 encoding of payload
        payload = base64.b64encode(payload.encode())

        # encrypt using e-Invoice public Key
        public_key_str = self.public_key
        payload = encrypt_message(payload, public_key_str)

        payload = {"Data": payload}
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
