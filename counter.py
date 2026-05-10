import tkinter as tk
from screeninfo import get_monitors
import os
import hid
import threading
import time

SAVE_FILE = "counter.txt"

# PS4/PS5 vendor and product IDs
PS4_VENDOR  = 0x054C
PS4_PRODUCT = 0x05C4  # DualShock 4 v1
PS4_PRODUCT2 = 0x09CC # DualShock 4 v2
PS5_PRODUCT = 0x0CE6  # DualSense

# Button byte/bit positions in the HID report
# Byte 5 contains the face buttons
SQUARE_BIT   = 4
CROSS_BIT    = 5
CIRCLE_BIT   = 6
TRIANGLE_BIT = 7

# Loads the counter.txt file
def load_counter():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            return int(f.read().strip())
    return 0

# Writes to the counter.txt file
def save_counter():
    with open(SAVE_FILE, 'w') as f:
        f.write(str(counter))

# Display overlay on the monitor that the mouse is on
def get_current_monitor():
    root.update_idletasks()
    mouse_x = root.winfo_pointerx()
    mouse_y = root.winfo_pointery()
    for monitor in get_monitors():
        if (monitor.x <= mouse_x < monitor.x + monitor.width and
            monitor.y <= mouse_y < monitor.y + monitor.height):
            return monitor
    return get_monitors()[0]

counter = load_counter()
combo_used = False

# Auto adjust size of window
def update_label():
    label.config(text=str(counter))
    save_counter()

    root.update_idletasks()
    win_width = root.winfo_reqwidth()
    win_height = root.winfo_reqheight()

    margin = 10
    x = monitor.x + monitor.width - win_width - margin
    y = monitor.y + margin
    root.geometry(f"{win_width}x{win_height}+{x}+{y}")

# Discovered controller and return type
def find_controller():
    for vendor, product in [
        (PS4_VENDOR, PS4_PRODUCT),
        (PS4_VENDOR, PS4_PRODUCT2),
        (PS4_VENDOR, PS5_PRODUCT),
    ]:
        try:
            d = hid.device()
            d.open(vendor, product)
            return d
        except:
            continue
    return None

# Thread that listens for controller inputs
def controller_listener():
    global counter, combo_used

    gamepad = None
    while gamepad is None:
        print("Waiting for controller...")
        gamepad = find_controller()
        if gamepad is None:
            time.sleep(1)

    gamepad.set_nonblocking(False)
    print("Controller found!")

    while True:
        try:
            report = gamepad.read(64)
            if report:
                buttons = report[5]
                cross    = bool(buttons & (1 << CROSS_BIT))
                circle   = bool(buttons & (1 << CIRCLE_BIT))
                square   = bool(buttons & (1 << SQUARE_BIT))
                triangle = bool(buttons & (1 << TRIANGLE_BIT))

                all_pressed = cross and circle and square and triangle

                if all_pressed and not combo_used:
                    combo_used = True
                    counter += 2
                    root.after(0, update_label)
                elif not all_pressed:
                    combo_used = False

        except Exception as e:
            print(f"Controller error: {e}")
            gamepad = None
            while gamepad is None:
                print("Reconnecting...")
                gamepad = find_controller()
                time.sleep(1)
            gamepad.set_nonblocking(False)

thread = threading.Thread(target=controller_listener, daemon=True)
thread.start()

# Formatting options
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", 0.7)
root.configure(bg="black")

label = tk.Label(root, text=str(counter), fg="white", bg="black", font=("Arial", 18)) # <---------- CHANGE THIS NUMBER TO INCREASE SIZE
label.pack(padx=0, pady=0)

# Detect monitor at startup based on cursor position
monitor = get_current_monitor()

root.update_idletasks()
win_width = root.winfo_reqwidth()
win_height = root.winfo_reqheight()

margin = 10
x = monitor.x + monitor.width - win_width - margin
y = monitor.y + margin
root.geometry(f"{win_width}x{win_height}+{x}+{y}")

root.mainloop()
