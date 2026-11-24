import binascii
import hashlib
import os


def hash_password(password):
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt, 100000
    )
    return (
        binascii.hexlify(salt).decode(),
        binascii.hexlify(password_hash).decode(),
    )


def verify_password(password, stored_salt, stored_hash):
    salt = binascii.unhexlify(stored_salt)
    stored_hash = binascii.unhexlify(stored_hash)
    new_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt, 100000
    )
    return new_hash == stored_hash


if __name__ == "__main__":
    password = input("Enter password: ")
    salt, password_hash = hash_password(password)

    print("Stored Salt:", salt)
    print("Stored Password Hash:", password_hash)

    entered = input("Enter password again: ")
    if verify_password(entered, salt, password_hash):
        print("Authentication Successful")
    else:
        print("Authentication Failed")
