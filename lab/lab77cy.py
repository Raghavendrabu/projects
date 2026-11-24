import socket
target = "127.0.0.1"
print("Scanning localhost:", target)
for port in range(1, 1025):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.1)
    result = sock.connect_ex((target, port))
    if result == 0:
        try:
            service = socket.getservbyport(port)
        except OSError:
            service = "Unknown"
        print(f"Port {port} OPEN - {service}")
    sock.close()