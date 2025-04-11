import socket
import json

def send_json_to_labview(data_dict, host='127.0.0.1', port=5052):
    try:
        # 1. Create TCP socket
        print("[INFO] Connecting to LabVIEW at {}:{}...".format(host, port))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            print("[✓] Connected to LabVIEW")

            # 2. Convert dict to JSON and encode to UTF-8
            json_str = json.dumps(data_dict, ensure_ascii=False)
            json_bytes = json_str.encode('utf-8')
            print("[✓] Sending JSON:", json_bytes)

            # 3. Send data
            s.sendall(json_bytes)

            # 4. Receive response (up to 1024 bytes)
            response = s.recv(1024)
            print("[✓] Response from LabVIEW:", response)

            # 5. Try decode response
            try:
                response_dict = json.loads(response.decode('utf-8'))
                print("[✓] Decoded JSON:", response_dict)
            except json.JSONDecodeError:
                print("[X] Received response is not valid JSON")

    except ConnectionRefusedError:
        print("[X] LabVIEW TCP server not running or wrong port")
    except Exception as e:
        print("[X] General error:", e)

# Example payload
data_to_send = {
    "command": "start",
    "flowrate": 22.5
}

# Run it
if __name__ == "__main__":
    send_json_to_labview(data_to_send)
