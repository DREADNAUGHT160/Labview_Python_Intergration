import tkinter as tk
from tkinter import ttk
import socket
import json
import threading
import time

class ValveControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Valve Control Panel")
        self.root.geometry("800x500")

        self.valve_names = [
            "A_Seg 1.1", "A_Seg 1.2", "A_Seg 2.1", "A_Seg 2.2",
            "A_Seg 3.1", "A_Seg 3.2", "A_Seg 4.1", "A_Seg 4.2",
            "A_Seg 5.1", "A_Seg 5.2", "A_Seg 6.1", "A_Seg 6.2"
        ]
        self.valve_vars = {}
        self.command = "stop"
        self.intensity = tk.IntVar(value=40)

        self.connected = False
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_to_labview()

        self.build_ui()

        self.running = True
        self.sender_thread = threading.Thread(target=self.auto_send_json, daemon=True)
        self.sender_thread.start()

    def connect_to_labview(self):
        try:
            self.client_socket.connect(('172.22.11.2', 5052))  # Updated IP and Port
            self.connected = True
            print("Connected to LabVIEW!")
        except Exception as e:
            print("Connection failed:", e)

    def build_ui(self):
        valve_frame = ttk.LabelFrame(self.root, text="Valves")
        valve_frame.pack(fill='x', padx=10, pady=5)

        for i, name in enumerate(self.valve_names):
            var = tk.BooleanVar()
            self.valve_vars[name] = var
            chk = ttk.Checkbutton(valve_frame, text=name, variable=var)
            chk.grid(row=i//6, column=i%6, sticky='w', padx=5, pady=2)

        cmd_frame = ttk.LabelFrame(self.root, text="System Commands")
        cmd_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(cmd_frame, text="ON", command=lambda: self.set_command("start")).pack(side='left', padx=5)
        ttk.Button(cmd_frame, text="OFF", command=lambda: self.set_command("stop")).pack(side='left', padx=5)
        ttk.Button(cmd_frame, text="Spülen", command=lambda: self.set_command("spuelen")).pack(side='left', padx=5)
        ttk.Button(cmd_frame, text="K_Wasser an/aus", command=lambda: self.set_command("wasser_toggle")).pack(side='left', padx=5)

        intensity_frame = ttk.LabelFrame(self.root, text="Intensität (mm/h 18–110)")
        intensity_frame.pack(fill='x', padx=10, pady=5)

        slider = ttk.Scale(intensity_frame, from_=18, to=110, variable=self.intensity, orient='horizontal')
        slider.pack(side='left', fill='x', expand=True, padx=5)

        self.intensity_label = ttk.Label(intensity_frame, text="40")
        self.intensity_label.pack(side='left', padx=10)
        self.intensity.trace_add('write', self.update_intensity_label)

        ttk.Button(self.root, text="Send Once", command=self.send_json_once).pack(pady=10)

    def update_intensity_label(self, *args):
        self.intensity_label.config(text=str(int(self.intensity.get())))

    def set_command(self, cmd):
        self.command = cmd
        print("Command set to:", cmd)

    def build_data_packet(self):
        data = {
            "command": self.command,
            "intensity": int(self.intensity.get())
        }
        for name, var in self.valve_vars.items():
            data[name] = "on" if var.get() else "off"
        return json.dumps(data)

    def send_json_once(self):
        if self.connected:
            try:
                message = self.build_data_packet()
                self.client_socket.sendall((message + '\n').encode('utf-8'))
                print("Sent:", message)
            except Exception as e:
                print("Send error:", e)

    def auto_send_json(self):
        while self.running:
            try:
                if self.connected:
                    self.send_json_once()
                time.sleep(0.5)  # Adjusted sleep time for background send
            except Exception as e:
                print("Background send error:", e)

    def on_close(self):
        self.running = False
        if self.sender_thread.is_alive():
            self.sender_thread.join()  # Ensure that the thread finishes its work
        if self.connected:
            self.client_socket.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ValveControlApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
