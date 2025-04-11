import socket
import json
import time

HOST = '127.0.0.1'
PORT = 5052

# Message to send
payload = {
    "command": "start",
    "flowrate": 22.5
}

try:
    print(f"[INFO] Connecting to LabVIEW at {HOST}:{PORT}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(200)  # Timeout after 5 seconds
        s.connect((HOST, PORT))
        print("[✓] Connected to LabVIEW!")

        # Convert to JSON
        msg = json.dumps(payload).encode("utf-8")
        print(f"[INFO] Sending JSON: {msg}")
        s.sendall(msg)

        # Wait and receive response
        try:
            response = s.recv(1024)
            decoded = response.decode("utf-8")
            print(f"[✓] Response from LabVIEW: {decoded}")

            try:
                reply = json.loads(decoded)
                print(f"[✓] Parsed JSON: {reply}")
            except json.JSONDecodeError:
                print("[✗] Received response is not valid JSON")

        except socket.timeout:
            print("[✗] Timeout while waiting for LabVIEW response")

except ConnectionRefusedError:
    print("[✗] Connection refused. Is LabVIEW running and listening on port 5052?")
except socket.timeout:
    print("[✗] Connection timed out.")
except Exception as e:
    print(f"[✗] Unexpected error: {e}")

