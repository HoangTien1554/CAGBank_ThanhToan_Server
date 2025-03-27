import requests
import re
import time
import json
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import threading

ahk_file = "CAGBank_NapTien_Gcafe.ahk"
TaiKhoan = "tien"
SoTien = 100000

# Đọc tệp JSON để lấy các giao dịch đã xử lý trước đó
def load_processed_transactions():
    try:
        with open('processed_transactions.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Lưu các giao dịch đã xử lý vào tệp JSON
def save_processed_transactions(processed_transactions):
    with open('processed_transactions.json', 'w', encoding='utf-8') as file:
        json.dump(processed_transactions, file, indent=4)

# Lưu thông tin cấu hình vào file JSON (API Key và URL)
def save_config(api_key, url):
    config = {
        "api_key": api_key,
        "url": url
    }
    with open('config.json', 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=4)

# Đọc thông tin cấu hình từ file JSON (API Key và URL)
def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"api_key": "", "url": ""}

# Gửi yêu cầu GET và lấy danh sách giao dịch
def get_transactions(API_KEY, URL):
    headers = {
        "Authorization": f"Apikey {API_KEY}"
    }
    response = requests.get(URL, headers=headers)
    if response.status_code == 200:
        data = response.json()
        transactions_data = data.get("data", {})
        records = transactions_data.get("records", [])
        return records
    else:
        print(f"Lỗi API: {response.status_code} - {response.text}")
        return []

# Lập trình cho việc kiểm tra giao dịch
def check_transactions(API_KEY, URL):
    processed_transactions = load_processed_transactions()

    while True:
        records = get_transactions(API_KEY, URL)

        if records:
            for transaction in records:
                transaction_id = transaction.get("id")
                description = transaction.get("description", "")
                amount = transaction.get("amount", "N/A")

                if transaction_id not in [trans['id'] for trans in processed_transactions]:
                    match = re.search(r'IBFT(.*?)GD', description)
                    if match:
                        content_between_IBFT_and_GD = match.group(1).strip()

                        processed_transactions.append({
                            "id": transaction_id,
                            "content": content_between_IBFT_and_GD,
                            "amount": amount
                        })

                        with open(ahk_file, "r", encoding="utf-8") as file:
                            lines = file.readlines()

                        for i, line in enumerate(lines):
                            if "TaiKhoan := " in line:
                                lines[i] = f'TaiKhoan := "{content_between_IBFT_and_GD}"\n'
                            if "SoTien := " in line:
                                lines[i] = f"SoTien := {amount}\n"

                        with open(ahk_file, "w", encoding="utf-8") as file:
                            file.writelines(lines)

                        os.startfile(ahk_file)

            save_processed_transactions(processed_transactions)

        time.sleep(31)

# Tạo GUI để nhập API Key, URL API và thay đổi file AHK
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CAGBank")
        self.geometry("400x300")

        # Tải cấu hình từ file (API Key và URL)
        config = load_config()

        self.api_key_label = tk.Label(self, text="API Key:")
        self.api_key_label.pack()

        self.api_key_entry = tk.Entry(self, width=40)
        self.api_key_entry.insert(0, config.get("api_key", ""))
        self.api_key_entry.pack()

        self.api_key_edit_button = tk.Button(self, text="Edit", command=self.edit_api_key)
        self.api_key_edit_button.pack()

        self.url_label = tk.Label(self, text="API URL:")
        self.url_label.pack()

        self.url_entry = tk.Entry(self, width=40)
        self.url_entry.insert(0, config.get("url", ""))
        self.url_entry.pack()

        self.url_edit_button = tk.Button(self, text="Edit", command=self.edit_url)
        self.url_edit_button.pack()

        self.change_ahk_button = tk.Button(self, text="Change AHK File", command=self.change_ahk_file)
        self.change_ahk_button.pack(pady=10)

        self.start_button = tk.Button(self, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(pady=10)

    def start_monitoring(self):
        api_key = self.api_key_entry.get()
        url = self.url_entry.get()

        if not api_key or not url:
            messagebox.showerror("Input Error", "API Key and URL must be provided.")
            return

        # Lưu cấu hình vào file JSON
        save_config(api_key, url)

        # Start monitoring in a separate thread to avoid blocking the UI
        monitoring_thread = threading.Thread(target=check_transactions, args=(api_key, url))
        monitoring_thread.daemon = True
        monitoring_thread.start()

    def change_ahk_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("AHK Files", "*.ahk")])
        if file_path:
            global ahk_file
            ahk_file = file_path
            messagebox.showinfo("Success", f"AHK file changed to: {ahk_file}")

    def edit_api_key(self):
        new_api_key = self.api_key_entry.get()
        if new_api_key:
            self.api_key_entry.delete(0, tk.END)  # Xóa ô nhập hiện tại
            self.api_key_entry.insert(0, new_api_key)  # Cập nhật giá trị mới vào ô nhập

    def edit_url(self):
        new_url = self.url_entry.get()
        if new_url:
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, new_url)

# Chạy ứng dụng GUI
if __name__ == "__main__":
    app = Application()
    app.mainloop()
