import socket
import ssl
import certifi

hostname = "example.com"
context = ssl.create_default_context(cafile=certifi.where())

with socket.create_connection((hostname, 443)) as sock:
    with context.wrap_socket(
        sock,
        server_hostname=hostname
    ) as secure_socket:

        print("TLS Connection Established")
        print("TLS Version:", secure_socket.version())
        print("Cipher:", secure_socket.cipher())

        print("Server Certificate:")
        print(secure_socket.getpeercert())