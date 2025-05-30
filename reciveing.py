import socket
import json
import time
import threading
import tkinter as tk
from tkinter import ttk

HOST = '127.0.0.1'
PORT = 5052

stop_flag = False
socket_thread = None

def send_data_loop():
    global stop_flag
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            status_var.set("🟢 Connected")
            while not stop_flag:
                # Get GUI inputs
                command = command_var.get()
                try:
                    value = float(value_var.get())
                except ValueError:
                    value = 0.0  # fallback

                # Build JSON
                payload = {
                    "command": command,
                    "value": value
                }
                json_bytes = json.dumps(payload).encode("utf-8")
                data_length = len(json_bytes)
                if data_length > 255:
                    status_var.set("❌ JSON too long!")
                    break

                # Send: 1-byte length + JSON string
                length_byte = data_length.to_bytes(1, byteorder='big')
                s.sendall(length_byte)
                s.sendall(json_bytes)

                last_sent_var.set(json.dumps(payload))
                print("Sent:", json.dumps(payload))

                # Receive 1-byte length + JSON reply
                try:
                    length_byte = s.recv(1)
                    if not length_byte:
                        break
                    recv_len = int.from_bytes(length_byte, byteorder='big')
                    recv_data = s.recv(recv_len)
                    if len(recv_data) == recv_len:
                        json_reply = json.loads(recv_data.decode("utf-8"))
                        last_received_var.set(json.dumps(json_reply))
                        print("Received:", json_reply)
                except Exception as recv_err:
                    print("Receive error:", recv_err)

                time.sleep(0.001)  # 1ms
    except Exception as e:
        status_var.set(f"❌ Error: {e}")
    finally:
        stop_flag = False
        status_var.set("🔴 Disconnected")

def start_sending():
    global stop_flag, socket_thread
    if not stop_flag:
        stop_flag = False
        socket_thread = threading.Thread(target=send_data_loop, daemon=True)
        socket_thread.start()

def stop_sending():
    global stop_flag
    stop_flag = True
    status_var.set("🟡 Stopping...")

# ----------------- GUI -------------------
root = tk.Tk()
root.title("LabVIEW TCP JSON GUI")

# Inputs
ttk.Label(root, text="Command:").grid(row=0, column=0, sticky='e')
command_var = tk.StringVar(value="start")
ttk.Entry(root, textvariable=command_var).grid(row=0, column=1)

ttk.Label(root, text="Value:").grid(row=1, column=0, sticky='e')
value_var = tk.StringVar(value="23.0")
ttk.Entry(root, textvariable=value_var).grid(row=1, column=1)

# Controls
ttk.Button(root, text="Start Sending", command=start_sending).grid(row=2, column=0, pady=5)
ttk.Button(root, text="Stop", command=stop_sending).grid(row=2, column=1, pady=5)

# Status Display
status_var = tk.StringVar(value="🔴 Disconnected")
ttk.Label(root, text="Status:").grid(row=3, column=0, sticky='e')
ttk.Label(root, textvariable=status_var).grid(row=3, column=1, sticky='w')

# Last Sent
last_sent_var = tk.StringVar()
ttk.Label(root, text="Last Sent:").grid(row=4, column=0, sticky='ne')
ttk.Label(root, textvariable=last_sent_var, wraplength=300).grid(row=4, column=1, sticky='w')

# Last Received
last_received_var = tk.StringVar()
ttk.Label(root, text="Last Received:").grid(row=5, column=0, sticky='ne')
ttk.Label(root, textvariable=last_received_var, wraplength=300).grid(row=5, column=1, sticky='w')

root.mainloop()
