import secrets
import os
import hashlib
import config

class Auth():
    def gen_key():
        return secrets.token_urlsafe(config.API_KEY_LEN)

    def hash_key(key):
        salt = os.urandom(config.SALT_LEN)
        hash_key = hashlib.pbkdf2_hmac(config.HASH_ALGO, key.encode('utf-8'), salt, config.HASH_ITER)
        return salt.hex() + hash_key.hex()
