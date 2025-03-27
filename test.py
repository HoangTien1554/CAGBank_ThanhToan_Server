import requests
import re  # Thư viện regex để trích xuất thông tin
import time  # Để dừng chương trình một khoảng thời gian trước khi kiểm tra lại
import json  # Để làm việc với tệp JSON
import os
ahk_file = "CAGBank_NapTien_Gcafe.ahk"

TaiKhoan = "tien"  # Giá trị mới cho TaiKhoan
SoTien = 100000  # Giá trị mới cho SoTien

# Thay API Key của bạn vào đây
API_KEY = "AK_CS.6507d3700ab711f097089522635f3f80.1gLQbfnm3eO9TqwMfBVgGkUVeIwqKBqbroCyXAjoN53uuHZ6yQ6Ezfq7mf9AUnYDdZ2ASgxZ"

# URL API của Casso
URL = "https://oauth.casso.vn/v2/transactions?fromDate=2021-04-01&page=1&pageSize=10&sort=ASC"

# Headers (sử dụng API Key)
headers = {
    "Authorization": f"Apikey {API_KEY}"
}

# Đọc tệp JSON để lấy các giao dịch đã xử lý trước đó
def load_processed_transactions():
    try:
        with open('processed_transactions.json', 'r', encoding='utf-8') as file:
            return json.load(file)  # Trả về danh sách các giao dịch đã xử lý
    except FileNotFoundError:
        return []  # Nếu tệp không tồn tại, trả về danh sách rỗng

# Lưu các giao dịch đã xử lý vào tệp JSON
def save_processed_transactions(processed_transactions):
    with open('processed_transactions.json', 'w', encoding='utf-8') as file:
        json.dump(processed_transactions, file, indent=4)  # Ghi các giao dịch đã xử lý vào tệp JSON

# Gửi yêu cầu GET và lấy danh sách giao dịch
def get_transactions():
    # Gửi yêu cầu GET
    response = requests.get(URL, headers=headers)

    # Kiểm tra mã trạng thái HTTP
    if response.status_code == 200:
        data = response.json()  # Chuyển phản hồi thành JSON

        # Kiểm tra "data" có tồn tại không
        transactions_data = data.get("data", {})
        records = transactions_data.get("records", [])

        return records
    else:
        print(f"Lỗi API: {response.status_code} - {response.text}")
        return []

# Lấy danh sách các giao dịch đã xử lý
processed_transactions = load_processed_transactions()

# Chạy liên tục để kiểm tra giao dịch mới
while True:
    records = get_transactions()

    if records:
        for transaction in records:
            transaction_id = transaction.get("id")  # Lấy ID giao dịch
            description = transaction.get("description", "")  # Lấy nội dung giao dịch
            amount = transaction.get("amount", "N/A")  # Lấy số tiền giao dịch

            # Kiểm tra xem giao dịch đã được xử lý chưa
            if transaction_id not in [trans['id'] for trans in processed_transactions]:
                # Nếu giao dịch mới, tìm và lưu nội dung giữa 'IBFT' và 'GD'
                match = re.search(r'IBFT(.*?)GD', description)
                if match:
                    content_between_IBFT_and_GD = match.group(1).strip()  # Lấy nội dung giữa 'IBFT' và 'GD'

                    # Lưu thông tin giao dịch vào danh sách đã xử lý
                    processed_transactions.append({
                        "id": transaction_id,
                        "content": content_between_IBFT_and_GD,  # Lưu nội dung giữa 'IBFT' và 'GD'
                        "amount": amount
                    })

                    with open(ahk_file, "r", encoding="utf-8") as file:
                        lines = file.readlines()

                    # Duyệt qua từng dòng và thay đổi giá trị của TaiKhoan và SoTien
                    for i, line in enumerate(lines):
                        if "TaiKhoan := " in line:  # Tìm dòng chứa TaiKhoan
                            lines[i] = f'TaiKhoan := "{content_between_IBFT_and_GD}"\n'  # Thay thế giá trị mới
                        if "SoTien := " in line:  # Tìm dòng chứa SoTien
                            lines[i] = f"SoTien := {amount}\n"  # Thay thế giá trị mới

                    # Ghi lại các thay đổi vào file .ahk
                    with open(ahk_file, "w", encoding="utf-8") as file:
                        file.writelines(lines)

                    print(f"Đã thay đổi TaiKhoan thành '{TaiKhoan}' và SoTien thành {SoTien} trong file {ahk_file}")

                    # Mở file .ahk sau khi thay đổi
                    # Sử dụng os.startfile() để mở file bằng chương trình mặc định liên kết với .ahk (AutoHotkey)
                    os.startfile(ahk_file)

        # Lưu lại danh sách các giao dịch đã xử lý vào tệp JSON
        save_processed_transactions(processed_transactions)



    # Chờ 10 giây trước khi kiểm tra lại giao dịch mới
    time.sleep(31)


