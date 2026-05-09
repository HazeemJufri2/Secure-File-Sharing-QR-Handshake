import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import firebase_admin
from firebase_admin import credentials, db
import threading

# --- Firebase Configuration ---
def initialize_firebase():
    try:
        # Check if already initialized to avoid errors on hot-reload
        if not firebase_admin._apps:
            cred = credentials.Certificate('serviceAccountKey.json')
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://file-sharing-1128f-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
        return True
    except Exception as e:
        print(f"Firebase Init Error: {e}")
        return False

def listen_for_handshake():
    """Background listener for Firebase updates"""
    def callback(event):
        # If the receiver updates status to 'verified'
        if event.data == 'verified':
            # Use root.after to trigger UI changes from a background thread safely
            root.after(0, lambda: messagebox.showinfo("Handshake Verified", 
                "System Alert: Receiver has successfully scanned the QR and verified file integrity."))
            root.after(0, lambda: status.config(text="Status: Handshake Success | Connection Secure", fg="green"))
            
            # Reset status after 10 seconds so you can demo it again
            root.after(10000, lambda: status.config(text="Environment: Python 3.12 | AES-256 Enabled", fg="black"))
            
            # Reset Firebase status to 'waiting' so it's ready for the next test
            db.reference('handshake_status').update({'status': 'waiting'})

    # Start the listener on the specific database path
    db.reference('handshake_status/status').listen(callback)

# --- Module Launcher ---
def launch_module(file_name):
    """Launches the specified python script in a new process."""
    if os.path.exists(file_name):
        subprocess.Popen(['python', file_name])
    else:
        messagebox.showerror("Error", f"File '{file_name}' not found in folder.")

# --- Main Window Setup ---
root = tk.Tk()
root.title("FYP: Secure Malaysian File Exchange & Detection")
root.geometry("450x400")
root.configure(bg="#f0f0f0")

# Initialize Firebase and start background thread
if initialize_firebase():
    # Run the listener in a daemon thread so it closes when the app closes
    threading.Thread(target=listen_for_handshake, daemon=True).start()
else:
    messagebox.showwarning("Connection Warning", "Firebase not connected. Automation will be disabled.")

# Header
header = tk.Label(root, text="Security Suite Dashboard", font=("Arial", 16, "bold"), bg="#f0f0f0", pady=20)
header.pack()

# Description
desc = tk.Label(root, text="Select a module to demonstrate:", font=("Arial", 10), bg="#f0f0f0")
desc.pack(pady=5)

# Buttons
btn_phish = tk.Button(root, text="1. AI Phishing Detection", width=30, height=2, 
                      command=lambda: launch_module('phishing_detection.py'), bg="#add8e6")
btn_phish.pack(pady=10)

btn_sender = tk.Button(root, text="2. Sender (Encrypt & QR)", width=30, height=2, 
                       command=lambda: launch_module('sender.py'), bg="#90ee90")
btn_sender.pack(pady=10)

btn_receiver = tk.Button(root, text="3. Receiver (Scan & Decrypt)", width=30, height=2, 
                         command=lambda: launch_module('receiver.py'), bg="#ffffe0")
btn_receiver.pack(pady=10)

# Status Footer
status = tk.Label(root, text="Environment: Python 3.12 | AES-256 Enabled", font=("Arial", 8, "italic"), bg="#f0f0f0")
status.pack(side="bottom", pady=20)

root.mainloop()