import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Generate a 256-bit key
key = AESGCM.generate_key(bit_length=256)
aes = AESGCM(key)

# Input plaintext message
message = input("Enter message: ").encode()

# Generate a recommended 96-bit (12-byte) nonce
nonce = os.urandom(12)

# Encrypt the message (associated_data is None)
ciphertext = aes.encrypt(nonce, message, None)

print("Original Message:", message.decode())
print("Encrypted Data:", ciphertext.hex())

# Decrypt the ciphertext
decrypted = aes.decrypt(nonce, ciphertext, None)
print("Decrypted Message:", decrypted.decode())
