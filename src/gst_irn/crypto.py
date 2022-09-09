import base64

from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_pem_public_key

# specs for algorithms are available at:
# https://einv-apisandbox.nic.in/FaqsonAPI.html


def encrypt_with_rsa_pub_key(message, public_key_str) -> str:
    """
    encrypt message with RSA by given public key
    """
    public_key = load_pem_public_key(public_key_str.encode())
    encrypted_msg = public_key.encrypt(
        plaintext=message, padding=asym_padding.PKCS1v15()
    )
    encoded_encrypted_msg = base64.b64encode(encrypted_msg).decode()
    return encoded_encrypted_msg


def decrypt_with_aes(message, key, raw=False):
    """
    decrypts the message using the given secret key (SEK)
    """
    message = base64.b64decode(message)
    key = base64.b64decode(key)
    decryptor = Cipher(
        algorithm=algorithms.AES(key=key), mode=modes.ECB()
    ).decryptor()
    decrypted = decryptor.update(message) + decryptor.finalize()

    # remove padding with pkcs7
    unpadder = sym_padding.PKCS7(128).unpadder()
    decrypted = unpadder.update(decrypted) + unpadder.finalize()

    # convert to string if not raw
    if not raw:
        decrypted = decrypted.decode()
    return decrypted


def encrypt_with_aes(message, key) -> str:
    """
    encrypts the message with the given secret key (SEK)
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
