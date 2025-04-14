import tkinter as tk
from tkinter import ttk
import json

# ------------------ Config ------------------
valve_names = [
    "A_Seg 1.1", "A_Seg 1.2", "A_Seg 2.1", "A_Seg 2.2",
    "A_Seg 3.1", "A_Seg 3.2", "A_Seg 4.1", "A_Seg 4.2",
    "A_Seg 5.1", "A_Seg 5.2", "A_Seg 6.1", "A_Seg 6.2"
]
valve_states = {}
command = "stop"
spuelen_cmd = "stop"
wasser_cmd = "stop"
# --------------------------------------------

def set_command(cmd):
    global command
    command = cmd
    status_var.set(f"System command set to '{cmd}'")

def toggle_spuelen():
    global spuelen_cmd
    spuelen_cmd = "start" if spuelen_cmd == "stop" else "stop"
    spuelen_btn.config(text=f"Spülen: {spuelen_cmd}")

def toggle_wasser():
    global wasser_cmd
    wasser_cmd = "start" if wasser_cmd == "stop" else "stop"
    wasser_btn.config(text=f"K_Wasser: {wasser_cmd}")

def send_data():
    payload = {
        "command": command,
        "spuelen": spuelen_cmd,
        "wasser": wasser_cmd,
        "intensity": intensity_var.get()
    }
    for name, var in valve_states.items():
        payload[name] = "on" if var.get() else "off"

    json_str = json.dumps(payload, indent=2)
    print("Sending to", ip_var.get(), "port", port_var.get())
    print(json_str)
    last_json_var.set(json_str)

def update_display(val):
    lcd_var.set(f"{int(float(val))}")

# ------------------ GUI ------------------
root = tk.Tk()
root.title("Valve Control Panel (Tkinter)")
root.geometry("950x700")

main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill="both", expand=True)

# ========== IP / Port ==========
ip_port_frame = ttk.LabelFrame(main_frame, text="TCP Settings", padding=10)
ip_port_frame.grid(row=0, column=0, columnspan=4, pady=5, sticky="ew")

ttk.Label(ip_port_frame, text="IP Address:").grid(row=0, column=0)
ip_var = tk.StringVar(value="127.0.0.1")
ttk.Entry(ip_port_frame, textvariable=ip_var, width=15).grid(row=0, column=1, padx=5)

ttk.Label(ip_port_frame, text="Port:").grid(row=0, column=2)
port_var = tk.StringVar(value="5052")
ttk.Entry(ip_port_frame, textvariable=port_var, width=8).grid(row=0, column=3)

# ========== Valve Toggles ==========
valves_frame = ttk.LabelFrame(main_frame, text="Valves", padding=10)
valves_frame.grid(row=1, column=0, columnspan=4, pady=10, sticky="ew")

for idx, name in enumerate(valve_names):
    var = tk.BooleanVar(value=False)
    valve_states[name] = var
    chk = ttk.Checkbutton(valves_frame, text=name, variable=var)
    chk.grid(row=idx // 6, column=idx % 6, padx=5, pady=3, sticky="w")

# ========== System Commands ==========
cmd_frame = ttk.LabelFrame(main_frame, text="System Commands", padding=10)
cmd_frame.grid(row=2, column=0, columnspan=4, pady=10, sticky="ew")

ttk.Button(cmd_frame, text="ON", width=10, command=lambda: set_command("start")).grid(row=0, column=0, padx=5)
ttk.Button(cmd_frame, text="OFF", width=10, command=lambda: set_command("stop")).grid(row=0, column=1, padx=5)

spuelen_btn = ttk.Button(cmd_frame, text="Spülen: stop", command=toggle_spuelen)
spuelen_btn.grid(row=0, column=2, padx=10)

wasser_btn = ttk.Button(cmd_frame, text="K_Wasser: stop", command=toggle_wasser)
wasser_btn.grid(row=0, column=3, padx=10)

# ========== Intensity ==========
intensity_frame = ttk.LabelFrame(main_frame, text="Intensität in mm/h (18–110)", padding=10)
intensity_frame.grid(row=3, column=0, columnspan=4, pady=10, sticky="ew")

intensity_var = tk.IntVar(value=40)
lcd_var = tk.StringVar(value="40")

lcd = tk.Label(intensity_frame, textvariable=lcd_var, font=("Helvetica", 28), bg="white", width=6)
lcd.grid(row=0, column=0, padx=10)

slider = ttk.Scale(intensity_frame, from_=18, to=110, orient="horizontal", variable=intensity_var, command=update_display)
slider.grid(row=0, column=1, padx=10, sticky="ew")
intensity_frame.columnconfigure(1, weight=1)

# ========== Send + Status ==========
ttk.Button(main_frame, text="Send", command=send_data).grid(row=4, column=0, pady=10, sticky="w")

status_var = tk.StringVar(value="System idle.")
ttk.Label(main_frame, textvariable=status_var).grid(row=4, column=1, columnspan=3, sticky="w")

# ========== Last Sent JSON ==========
ttk.Label(main_frame, text="Last Sent JSON:").grid(row=5, column=0, sticky="nw")
last_json_var = tk.StringVar()
ttk.Label(main_frame, textvariable=last_json_var, wraplength=800, justify="left").grid(row=5, column=1, columnspan=3, sticky="w")

root.mainloop()
