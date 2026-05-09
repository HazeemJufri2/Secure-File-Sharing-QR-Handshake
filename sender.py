import os
import tkinter as tk
from tkinter import filedialog, messagebox
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import qrcode
from PIL import ImageTk, Image

class SenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FYP Sender - AES-256 & QR")
        self.root.geometry("400x500")

        # UI Elements
        self.label = tk.Label(root, text="Step 1: Select a File to Encrypt", pady=10)
        self.label.pack()

        self.btn_select = tk.Button(root, text="Select File", command=self.select_file)
        self.btn_select.pack(pady=5)

        self.btn_encrypt = tk.Button(root, text="Encrypt & Generate QR", command=self.encrypt_file, state=tk.DISABLED)
        self.btn_encrypt.pack(pady=10)

        self.qr_label = tk.Label(root)
        self.qr_label.pack(pady=20)

        self.file_path = ""

    def select_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.label.config(text=f"Selected: {os.path.basename(self.file_path)}")
            self.btn_encrypt.config(state=tk.NORMAL)

    def encrypt_file(self):
        try:
            # 1. Generate AES-256 Key & Nonce (Following Flowchart)
            key = AESGCM.generate_key(bit_length=256)
            aesgcm = AESGCM(key)
            nonce = os.urandom(12) # GCM recommended nonce size

            # 2. Read and Encrypt the File
            with open(self.file_path, 'rb') as f:
                data = f.read()
            
            ciphertext = aesgcm.encrypt(nonce, data, None)

            # 3. Save the Encrypted File
            enc_file_path = self.file_path + ".enc"
            with open(enc_file_path, 'wb') as f:
                f.write(ciphertext)

            # 4. Generate QR Code (Key + Nonce) for Offline Exchange
            # Data format: key_hex:nonce_hex
            qr_data = f"{key.hex()}:{nonce.hex()}"
            qr_img = qrcode.make(qr_data)
            qr_img.save("exchange_qr.png")

            # 5. Display QR Code in UI
            display_img = Image.open("exchange_qr.png")
            display_img = display_img.resize((200, 200))
            self.photo = ImageTk.PhotoImage(display_img)
            self.qr_label.config(image=self.photo)

            messagebox.showinfo("Success", f"File Encrypted!\nSaved as: {os.path.basename(enc_file_path)}\nScan the QR code to exchange the key.")

        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = SenderApp(root)
    root.mainloop()
