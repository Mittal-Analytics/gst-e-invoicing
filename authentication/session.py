import base64
import json

import requests
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import unpad


def encrypt_message(message, public_key_str):
    public_key = RSA.import_key(public_key_str)
    cipher = PKCS1_v1_5.new(public_key)
    encrypted_msg = cipher.encrypt(message)
    encoded_encrypted_msg = base64.b64encode(encrypted_msg).decode()
    return encoded_encrypted_msg


def decrypt_message(message, key):
    message = base64.b64decode(message)
    # convert to 32 bytes array
    key = base64.b64decode(key)

    cipher = AES.new(key, AES.MODE_ECB)
    # decrypt and decode
    decrypted = cipher.decrypt(message)
    return decrypted


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

        self._base_url = "https://einv-apisandbox.nic.in" if is_sandbox else ""
        self.token = None
        self.app_key = get_app_key()

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
            "AppKey": self.app_key,
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
        if response.status_code == 200 and response.json()["Status"] == 1:
            return response.json()

        raise ValueError(
            f"Error while getting token."
            f"Status Code: {response.status_code}. "
            f"\nResponse: {response.json()}"
        )

    def get_party_details(self, party_gstin):
        url = f"{self._base_url}/eivital/v1.04/Master/gstin/{party_gstin}"

        # request headers
        auth_response = self.get_token()
        auth_data = auth_response["Data"]
        token = auth_data["AuthToken"]
        headers = {
            "client-id": self.client_id,
            "client-secret": self.client_secret,
            "gstin": self.gstin,
            "user_name": self.username,
            "AuthToken": token,
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200 and response.json()["Status"] == 1:
            gstin_response = response.json()
            gstin_data = gstin_response["Data"]

            # decrypt session encryption key
            sek = auth_data["Sek"]
            decrypted_sek = decrypt_message(sek, self.app_key)

            # unpad - with pkcs7
            un_padded = unpad(decrypted_sek, AES.block_size)

            # base64 encoding
            decrypted_sek = base64.b64encode(un_padded).decode()

            # decrypted gstin data with decrypted sek
            decrypted_data = decrypt_message(gstin_data, decrypted_sek)
            decrypted_data = decrypted_data.decode()

            # getting 3 extra space to the end of the string
            # decryption of data on sandbox
            decrypted_data = decrypted_data.replace("\x03\x03\x03", "")
            return json.loads(decrypted_data)

        raise ValueError(
            f"Error while getting party details."
            f"Status Code: {response.status_code}. "
            f"\nResponse: {response}"
        )
