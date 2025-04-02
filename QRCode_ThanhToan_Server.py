import requests
import re
import time
import json
import os
import base64

config_path = "data/config.json"
file_path = "data/processed_transactions.json"


def load_config(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

config = load_config(config_path)

last_id = config["last_id"]
bank_number = config["bank_number"]
ahk_file = config["ahk_file"]
token = config["token"]
URL = config["api_url"]

# Dữ liệu truy vấn
payload = {
    "bankAccounts": f"{bank_number}",  # Số tài khoản
    "begin": "20/3/2025",  # Ngày bắt đầu (DD/MM/YYYY)
    "end": "31/3/2050"  # Ngày kết thúc (DD/MM/YYYY)
}

encoded_text = base64.b64encode(token.encode()).decode()

# Headers yêu cầu
headers = {
    "pay2s-token": encoded_text,
    "Content-Type": "application/json"
}

# Lưu danh sách giao dịch vào file JSON
def save_transactions(transactions):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(transactions, file, indent=4, ensure_ascii=False)


# Đọc danh sách giao dịch từ file JSON
def load_transactions():
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Gửi yêu cầu GET và lấy danh sách giao dịch
def fetch_and_save_transactions():
    response = requests.post(URL, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        transactions = data.get("transactions", [])
        existing_transactions = load_transactions()
        existing_ids = {t["id"] for t in existing_transactions}


        # Chỉ lấy giao dịch tiền vào (type == "IN") và gán status "Chưa nạp tiền"
        new_transactions = [
            {
                "id": t["id"],
                "content": re.search(r'([a-z0-9\s]+)(?=\s*\d{6,}|\s*QR\s*|\s*GD|\s*$)',
                                     t["description"]).group().strip() if re.search(
                    r'([a-z0-9\s]+)(?=\s*\d{6,}|\s*QR\s*|\s*GD|\s*$)', t["description"]) else "",
                "datetime": t["transaction_date"],
                "amount": t["amount"],
                "status": "Chưa nạp tiền"
            }
            for t in transactions if t["type"] == "IN" and t["id"] not in existing_ids and t["id"] > last_id
        ]

        # Cập nhật last_id nếu cần
        max_new_id = max(t["id"] for t in transactions)
        if config["last_id"] == 0:
            update_config("last_id", max_new_id)



        if new_transactions:
            existing_transactions.extend(new_transactions)
            save_transactions(existing_transactions)


    else:
        print(f"Lỗi API: {response.status_code} - {response.text}")



# Chỉnh sửa file AHK và chạy AutoHotkey
def execute_transaction(content, amount):
    ahk_run = os.path.normpath(os.path.join("ahk", ahk_file))
    with open(ahk_run, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Duyệt qua từng dòng và thay đổi giá trị của TaiKhoan và SoTien
    for i, line in enumerate(lines):
        if "TaiKhoan := " in line:
            lines[i] = f'TaiKhoan := "{content}"\n'
        if "SoTien := " in line:
            lines[i] = f"SoTien := {amount}\n"
            break

    # Ghi lại các thay đổi vào file .ahk
    with open(ahk_run, "w", encoding="utf-8") as file:
        file.writelines(lines)

    # Mở file .ahk để thực hiện giao dịch
    os.startfile(ahk_run)

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def update_config(key, value):
    config = load_config("data/config.json")
    config[key] = value
    write_json("data/config.json", config)

# Lặp vô hạn để kiểm tra API mỗi 31 giây
while True:
    # Lấy dữ liệu từ API và lưu vào file JSON
    fetch_and_save_transactions()

    config = load_config(config_path)
    last_id = config["last_id"]

    # Đọc danh sách giao dịch từ file JSON
    transactions = load_transactions()

    # Lọc ra giao dịch có status "Chưa nạp tiền"
    pending_transactions = [t for t in transactions if t["status"] == "Chưa nạp tiền" and t["id"] > last_id]

    for transaction in pending_transactions:
        execute_transaction(transaction["content"], transaction["amount"])

        # Cập nhật trạng thái thành "Đã nạp tiền"
        transaction["status"] = "Đã nạp tiền"
        save_transactions(transactions)

        time.sleep(3)  # Chờ 3 giây trước khi thực hiện giao dịch tiếp theo

    # Đợi 2 giây trước khi kiểm tra API tiếp
    time.sleep(3.5)
