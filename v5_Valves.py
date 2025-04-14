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

# Flat JSON data structure
current_data = {
    "command": "stop",
    "intensity": 0.0,
    **{f"valve{i+1}": "off" for i in range(9)}
}

def send_data_loop():
    """Continuously sends current_data in JSON format until stopped."""
    global stop_flag
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            status_var.set("🟢 Connected")
            while not stop_flag:
                json_bytes = json.dumps(current_data).encode("utf-8")
                data_length = len(json_bytes)
                if data_length > 255:
                    status_var.set("❌ JSON too long!")
                    break

                length_byte = data_length.to_bytes(1, byteorder='big')
                s.sendall(length_byte)
                s.sendall(json_bytes)

                last_sent_var.set(json.dumps(current_data))
                print(json.dumps(current_data))
                time.sleep(0.005)  # ~200 Hz
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

def send_once():
    """Collect GUI input and update current_data with flat structure."""
    current_data["command"] = command_var.get()

    try:
        current_data["intensity"] = float(intensity_var.get())
    except ValueError:
        current_data["intensity"] = 0.0

    for i in range(9):
        state = "on" if valve_vars[i].get() else "off"
        current_data[f"valve{i+1}"] = state

    status_var.set("✅ Command updated")

# ---------------- GUI ------------------
root = tk.Tk()
root.title("Valve Control TCP Broadcaster")

# System command dropdown (start/stop)
ttk.Label(root, text="System Command:").grid(row=0, column=0, sticky='e')
command_var = tk.StringVar(value="stop")
ttk.Combobox(root, textvariable=command_var, values=["start", "stop"], width=8).grid(row=0, column=1)

# Intensity input
ttk.Label(root, text="Intensity:").grid(row=0, column=2, sticky='e')
intensity_var = tk.StringVar(value="100")
ttk.Entry(root, textvariable=intensity_var, width=10).grid(row=0, column=3)

# Valve checkboxes
valve_vars = [tk.BooleanVar(value=False) for _ in range(9)]
row_offset = 1
for i in range(9):
    r = row_offset + i // 3
    c = i % 3
    ttk.Checkbutton(root, text=f"Valve {i+1}", variable=valve_vars[i]).grid(row=r, column=c, padx=5, pady=2, sticky='w')

# Control buttons
ttk.Button(root, text="Send", command=send_once).grid(row=row_offset+3, column=0, pady=5)
ttk.Button(root, text="Start Sending", command=start_sending).grid(row=row_offset+3, column=1, pady=5)
ttk.Button(root, text="Stop", command=stop_sending).grid(row=row_offset+3, column=2, pady=5)

# Status and last JSON sent
status_var = tk.StringVar(value="🔴 Disconnected")
ttk.Label(root, text="Status:").grid(row=row_offset+4, column=0, sticky='e')
ttk.Label(root, textvariable=status_var).grid(row=row_offset+4, column=1, columnspan=3, sticky='w')

last_sent_var = tk.StringVar()
ttk.Label(root, text="Last Sent:").grid(row=row_offset+5, column=0, sticky='ne')
ttk.Label(root, textvariable=last_sent_var, wraplength=400).grid(row=row_offset+5, column=1, columnspan=3, sticky='w')

root.mainloop()
