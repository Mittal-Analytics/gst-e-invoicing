import base64
import json
import re

import requests
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


# snake case to camel case
def snake_to_camel(name):
    return "".join(word.title() for word in name.split("_"))


def _get_dict(**kwargs):
    # Returns a dictionary of kwargs with camel case keys
    return {snake_to_camel(k): v for k, v in kwargs.items()}


def tran_dtls(*, tax_sch, sup_typ="B2B", **kwargs):
    return _get_dict(tax_sch=tax_sch, sup_typ=sup_typ, **kwargs)


def doc_dtls(*, typ, no, dt, **kwargs):
    return _get_dict(typ=typ, no=no, dt=dt, **kwargs)


def item_dtls(
    *,
    sl_no,
    is_servc,
    hsn_cd,
    unit_price,
    igst_amt,
    tot_amt,
    ass_amt,
    gst_rt,
    tot_item_val,
    **kwargs,
):
    return _get_dict(
        sl_no=sl_no,
        is_servc=is_servc,
        hsn_cd=hsn_cd,
        unit_price=unit_price,
        igst_amt=igst_amt,
        tot_amt=tot_amt,
        ass_amt=ass_amt,
        gst_rt=gst_rt,
        tot_item_val=tot_item_val,
        **kwargs,
    )


def _get_seller_dtls(*, gstin, lgl_nm, addr1, loc, pin, stcd, **kwargs):
    return _get_dict(
        gstin=gstin,
        lgl_nm=lgl_nm,
        addr1=addr1,
        loc=loc,
        pin=pin,
        stcd=stcd,
        **kwargs,
    )


def _get_buyer_dtls(*, gstin, lgl_nm, pos, addr1, loc, pin, stcd, **kwargs):
    return _get_dict(
        gstin=gstin,
        lgl_nm=lgl_nm,
        pos=pos,
        addr1=addr1,
        loc=loc,
        pin=pin,
        stcd=stcd,
        **kwargs,
    )


def dispatch_dtls(*, nm, addr1, loc, pin, stcd, **kwargs):
    return _get_dict(nm=nm, addr1=addr1, loc=loc, pin=pin, stcd=stcd, **kwargs)


def ship_dtls(*, lgl_nm, addr1, loc, pin, stcd, **kwargs):
    return _get_dict(
        lgl_nm=lgl_nm, addr1=addr1, loc=loc, pin=pin, stcd=stcd, **kwargs
    )


def val_dtls(*, tot_inv_val, **kwargs):
    return _get_dict(tot_inv_val=tot_inv_val, **kwargs)


def ewb_dtls(*, distance, **kwargs):
    return _get_dict(distance=distance, **kwargs)


def get_buyer_dtls(buyer_gstin):
    return _get_buyer_dtls(
        gstin=buyer_gstin.get("Gstin"),
        lgl_nm=buyer_gstin.get("LegalName"),
        pos=f"{buyer_gstin.get('StateCode')}",
        addr1=buyer_gstin.get("AddrBnm"),
        loc=buyer_gstin.get("AddrLoc"),
        pin=buyer_gstin.get("AddrPncd"),
        stcd=f"{buyer_gstin.get('StateCode')}",
    )


def get_seller_dtls(seller_gstin):
    return _get_seller_dtls(
        gstin=seller_gstin.get("Gstin"),
        lgl_nm=seller_gstin.get("LegalName"),
        addr1=seller_gstin.get("AddrBnm"),
        loc=seller_gstin.get("AddrLoc"),
        pin=seller_gstin.get("AddrPncd"),
        stcd=f"{seller_gstin.get('StateCode')}",
    )


def get_payload(
    *,
    version,
    tran_dtls,
    doc_dtls,
    seller_dtls,
    buyer_dtls,
    item_list,
    val_dtls,
    ewb_dtls,
    **kwargs,
):
    return _get_dict(
        version=version,
        tran_dtls=tran_dtls,
        doc_dtls=doc_dtls,
        seller_dtls=seller_dtls,
        buyer_dtls=buyer_dtls,
        item_list=item_list,
        val_dtls=val_dtls,
        ewb_dtls=ewb_dtls,
        **kwargs,
    )


def get(func, **kwargs):
    return func(**kwargs)


# function encrypt message with RSA by given public key
# return message with is already decoded
def encrypt_with_rsa_pub_key(message, public_key_str):
    public_key = RSA.import_key(public_key_str)
    cipher = PKCS1_v1_5.new(public_key)
    encrypted_msg = cipher.encrypt(message)
    encoded_encrypted_msg = base64.b64encode(encrypted_msg).decode()
    return encoded_encrypted_msg


# function to encrypt a message with AES by given
# return decrypted message is not decoded
def decrypt_with_aes(message, key):
    message = base64.b64decode(message)
    key = base64.b64decode(key)
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted = cipher.decrypt(message)
    return decrypted


# function to encrypt a message with AES by given key
# return decoded encrypted message
def encrypt_with_aes(message, key):
    key = base64.b64decode(key)
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted_msg = cipher.encrypt(pad(message, AES.block_size))
    encoded_encrypted_msg = base64.b64encode(encrypted_msg).decode()
    return encoded_encrypted_msg


# Function to create a random app_key of 32 byte
def get_app_key():
    aes_key = get_random_bytes(32)
    readable = base64.b64encode(aes_key).decode()
    return readable


# return headers with given args
def get_headers_with_token(auth_data, client_secret, gstin):
    headers = {
        "client-id": auth_data.get("ClientId"),
        "client-secret": client_secret,
        "gstin": gstin,
        "user_name": auth_data.get("UserName"),
        "AuthToken": auth_data.get("AuthToken"),
    }
    return headers


def get_decrypted_sek(sek, app_key):
    decrypted_sek = decrypt_with_aes(sek, app_key)
    # unpad - with pkcs7
    un_padded = unpad(decrypted_sek, AES.block_size)
    # base64 encoding
    decrypted_sek = base64.b64encode(un_padded).decode()
    return decrypted_sek


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

    def get_auth_data(self, force_regenerate_token=False):
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
        payload = encrypt_with_rsa_pub_key(payload, public_key_str)

        payload = {"Data": payload}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            response = response.json()
            return response["Data"]

        raise ValueError(
            f"Error while getting token."
            f"Status Code: {response.status_code}. "
            f"\nResponse: {response.json()}"
        )

    # function to fetch details of given gist number
    # return json response
    def get_party_details(self, party_gstin, auth_data=None):
        # api url
        url = f"{self._base_url}/eivital/v1.04/Master/gstin/{party_gstin}"
        if not auth_data:
            auth_data = self.get_auth_data()

        # request headers
        headers = get_headers_with_token(
            auth_data, self.client_secret, self.gstin
        )

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            gstin_response = response.json()
            gstin_data = gstin_response["Data"]

            decrypted_sek = get_decrypted_sek(
                auth_data.get("Sek"), self.app_key
            )

            # decrypted gstin data with decrypted sek
            decrypted_data = decrypt_with_aes(gstin_data, decrypted_sek)
            decrypted_data = decrypted_data.decode()

            # getting 3 extra space to the end of the string
            # on decryption of data on sandbox
            decrypted_data = re.sub(r"}.*", "", decrypted_data)
            decrypted_data = decrypted_data + "}"
            return json.loads(decrypted_data)

        raise ValueError(
            f"Error while getting party details."
            f"Status Code: {response.status_code}. "
            f"\nResponse: {response}"
        )

    # function to generate irn for given invoice details
    # return a json object
    def generate_e_invoice(
        self,
        *,
        party_gstin,
        tran_dtls,
        doc_dtls,
        item_list,
        val_dtls,
        ewb_dtls,
        version="1.1",
        disp_dtls=None,
        ship_tls=None,
        auth_data=None,
    ):
        if not auth_data:
            auth_data = self.get_auth_data()

        seller_gstin = self.get_party_details(self.gstin)
        buyer_gstin = self.get_party_details(party_gstin)

        # api url
        url = f"{self._base_url}/eicore/v1.03/Invoice"

        # request headers
        headers = get_headers_with_token(
            auth_data, self.client_secret, self.gstin
        )
        payload = get_payload(
            version=version,
            tran_dtls=tran_dtls,
            doc_dtls=doc_dtls,
            seller_dtls=get_seller_dtls(seller_gstin),
            buyer_dtls=get_buyer_dtls(buyer_gstin),
            item_list=[item_list],
            val_dtls=val_dtls,
            ewb_dtls=ewb_dtls,
            disp_dtls=disp_dtls,
            ship_tls=ship_tls,
        )

        # convert payload to json string
        data = json.dumps(payload)
        payload = data.encode()

        # decrypt session encryption key
        sek = auth_data["Sek"]
        decrypted_sek = get_decrypted_sek(sek, self.app_key)

        # encrypt payload
        encrypt_message = encrypt_with_aes(payload, decrypted_sek)
        payload = {"Data": encrypt_message}

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()

        raise ValueError(
            f"Error while generating invoice: "
            f"Status Code: {response.status_code}. "
            f"\nResponse: {response.json()}"
        )
