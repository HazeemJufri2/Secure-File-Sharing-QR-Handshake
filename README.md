# Secure File Sharing System (QR-Based Handshake)

## 🛡️ Project Overview
This is a **Computer System Security** Final Year Project (FYP2). It implements a localized secure file transfer protocol that mitigates **Man-in-the-Middle (MitM)** attacks by performing a physical "Out-of-Band" key exchange.

## 🚀 Key Features
* **AES-256-GCM Encryption:** Provides both confidentiality and built-in integrity verification (AEAD).
* **QR-Based Handshake:** Keys and nonces are exchanged via dynamic QR codes, keeping credentials off the network.
* **Firebase Integration:** Real-time handshake status monitoring.
* **Computer Vision:** Automated QR detection using OpenCV.

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Security:** Cryptography.io, AES-GCM
* **Vision:** OpenCV (CV2)
* **Backend:** Firebase Admin SDK
* **UI:** Tkinter
