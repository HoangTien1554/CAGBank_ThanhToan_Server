import requests
import re
import time
import json
import os

def load_config():
    with open("config.json", "r", encoding="utf-8") as file:
        return json.load(file)

config = load_config()

ahk_file = config["ahk_file"]
API_KEY = config["api_key"]
URL = config["api_url"]

# Headers (sử dụng API Key)
headers = {
    "Authorization": f"Apikey {API_KEY}"
}

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
        json.dump(processed_transactions, file, indent=4, ensure_ascii=False)

# Gửi yêu cầu GET và lấy danh sách giao dịch
def get_transactions():
    response = requests.get(URL, headers=headers)

    if response.status_code == 200:
        data = response.json()
        transactions = data.get("data", {}).get("records", [])

        # Chỉ lấy giao dịch tiền vào (amount > 0)
        incoming_transactions = [t for t in transactions if t["amount"] > 0]

        return incoming_transactions
    else:
        print(f"Lỗi API: {response.status_code} - {response.text}")
        return []

# Chỉnh sửa file AHK và chạy AutoHotkey
def execute_transaction(content, amount):
    with open(ahk_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Duyệt qua từng dòng và thay đổi giá trị của TaiKhoan và SoTien
    for i, line in enumerate(lines):
        if "TaiKhoan := " in line:
            lines[i] = f'TaiKhoan := "{content}"\n'
        if "SoTien := " in line:
            lines[i] = f"SoTien := {amount}\n"

    # Ghi lại các thay đổi vào file .ahk
    with open(ahk_file, "w", encoding="utf-8") as file:
        file.writelines(lines)

    # Mở file .ahk để thực hiện giao dịch
    os.startfile(ahk_file)

# Danh sách các giao dịch đã xử lý
processed_transactions = load_processed_transactions()

# Lặp vô hạn để kiểm tra API mỗi 31 giây
while True:
    records = get_transactions()
    new_transactions = []

    if records:
        for transaction in records:
            transaction_id = transaction.get("id")
            description = transaction.get("description", "")
            amount = transaction.get("amount", "N/A")
            date = transaction.get("when", "").replace("T", " - ")



            # Kiểm tra xem giao dịch đã có trong danh sách chưa
            existing_transaction = next((t for t in processed_transactions if t["id"] == transaction_id), None)

            if not existing_transaction:
                match = re.search(r'([a-z0-9\s]+)(?=\s*\d{6,}|\s*QR\s*|\s*GD|\s*$)', description)
                if match:
                    content = match.group().strip()

                    new_transaction = {
                        "id": transaction_id,
                        "content": content,
                        "datetime": date,
                        "amount": amount,
                        "status": "Chưa nạp tiền"  # Chưa thực hiện
                    }
                    new_transactions.append(new_transaction)
                    processed_transactions.append(new_transaction)

        # Lưu lại danh sách giao dịch đã cập nhật
        save_processed_transactions(processed_transactions)

    # Thực hiện giao dịch có status rỗng, mỗi 3 giây
    pending_transactions = [t for t in processed_transactions if t["status"] == "Chưa nạp tiền"]

    for transaction in pending_transactions:
        execute_transaction(transaction["content"], transaction["amount"])
        print(f"Thực hiện giao dịch: {transaction['content']} - {transaction['amount']} VND")

        # Cập nhật trạng thái thành "Đã nạp tiền"
        transaction["status"] = "Đã nạp tiền"
        save_processed_transactions(processed_transactions)

        time.sleep(3.5)  # Chờ 3 giây trước khi thực hiện giao dịch tiếp theo

    # Đợi 31 giây trước khi kiểm tra API tiếp
    time.sleep(31)
