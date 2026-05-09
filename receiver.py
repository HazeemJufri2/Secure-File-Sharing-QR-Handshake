import os
import tkinter as tk
from tkinter import filedialog, messagebox
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import cv2
import numpy as np
import firebase_admin
from firebase_admin import credentials, db
import time

class ReceiverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FYP Receiver - Scan & Decrypt")
        self.root.geometry("400x350")
        
        # --- Firebase Initialization ---
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate('serviceAccountKey.json')
                firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://file-sharing-1128f-default-rtdb.asia-southeast1.firebasedatabase.app/' 
                })
            
            # Pointing to the specific folder
            self.db_ref = db.reference('handshake_status')
            
            # We DON'T reset to 'waiting' here anymore to avoid race conditions
            print(">>> Firebase: Connection Established.")
            
        except Exception as e:
            print(f"!!! Firebase Init Error: {e}")
            self.db_ref = None 

        self.setup_ui()

    def setup_ui(self):
        self.label = tk.Label(self.root, text="Select the .enc file to restore", pady=10)
        self.label.pack()

        self.btn_select = tk.Button(self.root, text="Select Encrypted File", command=self.select_file, bg="#f0f0f0")
        self.btn_select.pack(pady=5)

        self.btn_scan = tk.Button(self.root, text="Scan QR & Decrypt", command=self.scan_and_decrypt, state=tk.DISABLED, bg="#90ee90")
        self.btn_scan.pack(pady=10)
        self.file_path = ""

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Encrypted files", "*.enc")])
        if self.file_path:
            self.label.config(text=f"Selected: {os.path.basename(self.file_path)}")
            self.btn_scan.config(state=tk.NORMAL)

    def scan_and_decrypt(self):
        cap = cv2.VideoCapture(0)
        detector = cv2.QRCodeDetector()
        scanned_data = ""
        
        messagebox.showinfo("Scanner", "Camera opening... Point it at the Sender's QR.")
        
        while True:
            ret, img = cap.read()
            if not ret: continue

            data, bbox, _ = detector.detectAndDecode(img)
            
            if data:
                scanned_data = data
                # --- THE MOMENT OF SUCCESS ---
                if self.db_ref:
                    try:
                        # Use .set() to overwrite EVERYTHING in that node
                        self.db_ref.set({
                            'status': 'verified',
                            'last_scan': time.time()
                        })
                        print(">>> FIREBASE: DATA PUSHED TO SERVER")
                        # Force the GUI to process the network event before closing
                        self.root.update()
                        time.sleep(1) # CRITICAL: Gives the network 1 second to finish
                    except Exception as e:
                        print(f"!!! Firebase Error: {e}")
                break

            cv2.imshow("Scanning... (Focus on QR)", img)
            self.root.update() 
            if cv2.waitKey(1) & 0xFF == ord('q'): break
        
        cap.release()
        cv2.destroyAllWindows()

        if scanned_data:
            self.decrypt_process(scanned_data)

    def decrypt_process(self, scanned_data):
        try:
            # Parse key and nonce from the QR hex
            key_hex, nonce_hex = scanned_data.split(":")
            key, nonce = bytes.fromhex(key_hex), bytes.fromhex(nonce_hex)

            aesgcm = AESGCM(key)
            with open(self.file_path, 'rb') as f:
                ciphertext = f.read()
            
            # AES-GCM performs the integrity check automatically
            decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)

            # Restoring the original file extension
            original_full_path, _ = os.path.splitext(self.file_path)
            directory = os.path.dirname(self.file_path)
            base_name = os.path.basename(original_full_path)
            final_path = os.path.join(directory, f"restored_{base_name}")

            with open(final_path, 'wb') as f:
                f.write(decrypted_data)

            messagebox.showinfo("Success", f"Integrity Verified!\nRestored as: {os.path.basename(final_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Decryption Failed: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReceiverApp(root)
    root.mainloop()