import tkinter as tk
from pynput import keyboard
from screeninfo import get_monitors
import os

SAVE_FILE = "counter.txt"

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
pressed_keys = set()
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

# Increase counter on key press
def on_press(key):
    global counter, combo_used
    try:
        pressed_keys.add(key.char)
    except AttributeError:
        pressed_keys.add(key)

    if ('z' in pressed_keys and
        'x' in pressed_keys and
        'c' in pressed_keys and
        'v' in pressed_keys and
        not combo_used):
            combo_used = True
            counter += 2 # Increment Number
            root.after(0, update_label)

# Does not allow for hold
def on_release(key):
    global combo_used
    try:
        pressed_keys.discard(key.char)
    except AttributeError:
        pressed_keys.discard(key)

    if ('z' not in pressed_keys or
        'x' not in pressed_keys or
        'c' not in pressed_keys or
        'v' not in pressed_keys):
            combo_used = False

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

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