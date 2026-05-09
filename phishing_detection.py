import re
import tkinter as tk
from tkinter import messagebox

class PhishingDetectorModule:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Phishing Detection - Malaysia")
        self.root.geometry("500x500")
        self.root.configure(bg="#f8f9fa")

        # Dictionary of local Malaysian lures (based on FYP requirements)
        self.local_keywords = {
            "institutions": ["lhdn", "kwsp", "pdrm", "maybank", "cimb", "tng", "bantuan kerajaan", "epf", "sspn"],
            "urgency": ["akaun dibekukan", "verify now", "segera", "tunggakan", "tuntut segera", "sekatan", "sahkan"]
        }
        
        self.create_widgets()

    def preprocess_manglish(self, text):
        """Standardizes Manglish/Malay text for analysis"""
        text = text.lower()
        # Normalize local slang to English/Standard Malay equivalents
        text = text.replace("u punya", "your").replace("acc", "account").replace("kene", "kena")
        # Identify and mask URLs for pattern analysis
        text = re.sub(r'http\S+|www\S+', '[URL]', text)
        return text

    def create_widgets(self):
        # Header Styling
        tk.Label(self.root, text="Phishing Detection Analysis", font=("Arial", 14, "bold"), bg="#f8f9fa", fg="#333").pack(pady=15)
        
        # Instruction Label
        tk.Label(self.root, text="Paste suspicious SMS or Email content below:", bg="#f8f9fa", font=("Arial", 10)).pack()
        
        # Input Text Area
        self.input_text = tk.Text(self.root, height=12, width=55, font=("Arial", 10), relief="flat", highlightthickness=1)
        self.input_text.pack(padx=20, pady=10)

        # Analysis Button
        self.btn_analyze = tk.Button(self.root, text="Analyze Localized Lures", 
                                     command=self.run_analysis, bg="#add8e6", font=("Arial", 10, "bold"), 
                                     width=25, cursor="hand2")
        self.btn_analyze.pack(pady=20)

        # Status Footer
        self.status = tk.Label(self.root, text="Module: Localized Heuristic Engine v1.0", font=("Arial", 8), bg="#f8f9fa", fg="#888")
        self.status.pack(side="bottom", pady=5)

    def run_analysis(self):
        """Core logic to identify Malaysian social engineering cues"""
        content = self.input_text.get("1.0", "end-1c")
        
        if not content.strip():
            messagebox.showwarning("Input Required", "Please enter text to analyze.")
            return

        cleaned = self.preprocess_manglish(content)
        risk_score = 0
        findings = []

        # 1. Check for Malaysian Institutional Impersonation
        for inst in self.local_keywords["institutions"]:
            if inst in cleaned:
                risk_score += 35
                findings.append(f"Institutional Lure: {inst.upper()}")

        # 2. Check for Social Engineering Urgency/Fear Cues
        for term in self.local_keywords["urgency"]:
            if term in cleaned:
                risk_score += 25
                findings.append(f"Urgency/Threat: {term.title()}")

        # 3. Check for Suspicious Links
        if "[URL]" in cleaned:
            risk_score += 20
            findings.append("Suspicious Hyperlink")

        # Result Logic
        if risk_score >= 45:
            result = f"RISK LEVEL: HIGH ({risk_score}%)\n\n"
            result += "AI ANALYSIS DETECTED:\n"
            for item in findings:
                result += f"• {item}\n"
            result += "\n[!] This message mimics common Malaysian scams (e.g., LHDN/KWSP lures). Do not click any links."
            messagebox.showwarning("High Risk Detected", result)
        elif risk_score > 0:
            result = f"RISK LEVEL: MEDIUM ({risk_score}%)\n\nCues found:\n" + "\n".join(findings)
            messagebox.showinfo("Moderate Risk", result)
        else:
            messagebox.showinfo("Analysis Result", "RISK LEVEL: LOW (0%)\n\nNo significant localized phishing patterns found.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhishingDetectorModule(root)
    root.mainloop()