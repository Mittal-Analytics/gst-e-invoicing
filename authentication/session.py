import base64
import json

import requests
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from dotenv import dotenv_values

CONFIG = dotenv_values(".env")
import base64

import requests


def encrypt_with_public_key(message, public_key):
    encryptor = PKCS1_OAEP.new(public_key)
    encrypted_msg = encryptor.encrypt(message)
    encoded_encrypted_msg = base64.b64encode(encrypted_msg)
    return encoded_encrypted_msg


def _get_public_key():
    with open("public_keys/einv_sandbox.pem", "r") as key_file:
        return key_file.read()


class Session:
    gstin = CONFIG.get("GSTIN")
    client_id = CONFIG.get("CLIENT_ID")
    client_secret = CONFIG.get("CLIENT_SECRET")
    username = CONFIG.get("USERNAME")
    password = CONFIG.get("PASSWORD")
    is_sandbox = True
    force_generate = False

    # function to get authenticated token
    def get_token(self):
        url = "https://einv-apisandbox.nic.in/eivital/v1.04/auth"
        # request headers
        headers = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "Gstin": self.gstin,
        }

        # request payload
        data = {
            "UserName": self.username,
            "Password": self.password,
            "AppKey": base64.b64encode(get_random_bytes(32)).decode(),
            "ForceRefreshAccessToken": self.force_generate,
        }

        # Json containing the Credentials is encoded
        # using Base64 and then encrypted using e-Invoice public Key
        json_data = json.dumps(data)
        encoded_data = base64.b64encode(json_data.encode())

        public_key = RSA.importKey(_get_public_key())

        # encrypt using e-Invoice public Key
        encoded_encrypted_data = encrypt_with_public_key(
            encoded_data, public_key
        )

        payload = {"Data": encoded_encrypted_data.decode()}
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
