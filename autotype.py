import pyautogui
import tkinter as tk
import threading
import keyboard
import random
import time
import os
import sys
import traceback
from datetime import datetime

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRANSCRIPT = os.path.join(BASE_DIR, "Typable.txt")

# if and when an error occurs[which it shouldn't my code is PERFECT] this generates a .log just identifying the issue
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    date_str = datetime.now().strftime("%d-%m-%y")
    counter = 0
    while True:
        log_name = f"error{counter}-{date_str}.log"
        log_path = os.path.join(BASE_DIR, log_name)
        if not os.path.exists(log_path):
            break
        counter += 1

    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(error_msg)
        f.write("\n---\n")
        f.write(
            "An unexpected error occurred. Please open an issue on our GitHub repository.\n"
            "If you are able to resolve this bug, feel free to clone the source code, fix the issue,\n"
            "and rebuild the executable using one of the following commands:\n\n"
            "python -m PyInstaller --noconsole --onefile autotype.py\n"
            "pyinstaller --noconsole --onefile autotype.py\n"
        )

sys.excepthook = handle_exception
threading.excepthook = lambda args: handle_exception(args.exc_type, args.exc_value, args.exc_traceback)



running = True
def ensure():
    if not os.path.exists(TRANSCRIPT):
        with open(TRANSCRIPT, "w", encoding="utf-8") as f:
            f.write("")
def saveText():
    text = textBox.get("1.0", tk.END).strip()

    if text:
        with open(TRANSCRIPT, "w", encoding="utf-8") as f:
            f.write(text)

def load():
    with open(TRANSCRIPT, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        statusText.set("no text found")
        return None

    return text

def jitter(offset, isSpace):
    cap = offset / 2 if isSpace else offset
    return random.randint(0, int(cap)) / 1000.0

def pauses():
    return random.uniform(0.2, 3.0)

def stop():
    global running

    while running:
        if keyboard.is_pressed("esc") and keyboard.is_pressed("backspace"):
            running = False
            os._exit(0)

        time.sleep(0.05)

def type(text, speed, offset):
    global running

    pyautogui.FAILSAFE = True
    delay = 1.0 / speed

    wordsSincePause = 0
    nextPauseAt = random.randint(4, 8) # adds a pause between the randomly selected word

    for ch in text:
        if not running:
            return

        pyautogui.write(ch, interval=0)
        time.sleep(delay + jitter(offset, ch == " "))

        if ch == " ":
            wordsSincePause += 1

            if wordsSincePause >= nextPauseAt:
                time.sleep(pauses())

                wordsSincePause = 0
                nextPauseAt = random.randint(4, 8)

    statusText.set("finished")
    startButton.config(state="normal")

def countdown(speed, offset):
    for n in (3, 2, 1):
        statusText.set(str(n))
        time.sleep(1)

    statusSubText.set("typing...")
    text = load()

    if text:
        type(text, speed, offset)

def startcmd():
    try:
        speed = float(speedEntry.get())
        offset = float(offsetEntry.get())
    except:
        statusText.set("invalid values")
        return

    saveText()
    startButton.config(state="disabled")

    statusText.set("3")
    statusSubText.set(
        "click the writing field within 3 seconds after clicking start"
    )

    threading.Thread(
        target=countdown,
        args=(speed, offset),
        daemon=True
    ).start()

ensure()


# tk ui setup
threading.Thread(target=stop, daemon=True).start()
root = tk.Tk()
root.title("No AI Autotyper")
root.geometry("420x520")
root.resizable(False, False)

title = tk.Label(
    root,
    text="Autotyper",
    font=("Segoe UI", 20, "bold")
)
title.pack(pady=(15, 10))

speedLabel = tk.Label(root, text="Speed (chars/sec)")
speedLabel.pack()

speedEntry = tk.Entry(root)
speedEntry.insert(0, "12") # the initial type speed
speedEntry.pack(pady=(0, 10))

offsetLabel = tk.Label(root, text="Delay Offset (ms)")
offsetLabel.pack()

offsetEntry = tk.Entry(root)
offsetEntry.insert(0, "10") # initial offset in ms
offsetEntry.pack(pady=(0, 15))

textLabel = tk.Label(root, text="Text To Type")
textLabel.pack()

textBox = tk.Text(
    root,
    height=8,
    width=42,
    font=("Consolas", 9)
)
textBox.pack(pady=(5, 2))

textSubLabel = tk.Label(
    root,
    text="if left blank, existing contents in Typeable.txt will be used",
    font=("Segoe UI", 8)
)
textSubLabel.pack(pady=(0, 12))

startButton = tk.Button(
    root,
    text="Start Typing",
    command=startcmd,
    width=20,
    height=2
)
startButton.pack()

statusText = tk.StringVar()
statusText.set("ready")

statusLabel = tk.Label(
    root,
    textvariable=statusText,
    font=("Segoe UI", 16, "bold")
)
statusLabel.pack(pady=(15, 3))

statusSubText = tk.StringVar()
statusSubText.set("")

subLabel = tk.Label(
    root,
    textvariable=statusSubText,
    font=("Segoe UI", 8)
)
subLabel.pack()

killLabel = tk.Label(
    root,
    text="ESC + Backspace to shut program off",
    font=("Segoe UI", 9)
)
killLabel.pack(side="bottom", pady=10)

root.mainloop()
