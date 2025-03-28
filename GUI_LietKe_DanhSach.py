import tkinter as tk
from tkinter import ttk
import json


# Hàm để đọc dữ liệu từ file JSON
def read_transactions(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Lỗi khi đọc file JSON: {e}")
        return []


# Hàm tạo giao diện
def create_gui(transactions):
    root = tk.Tk()
    root.title("Danh Sách Giao Dịch")

    # Tạo Treeview để hiển thị danh sách giao dịch
    tree = ttk.Treeview(root, columns=("STT", "Tên", "Số Tiền", "Trạng Thái"), show="headings")
    tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Cấu hình các cột
    tree.heading("STT", text="STT")
    tree.heading("Tên", text="Tên")
    tree.heading("Số Tiền", text="Số Tiền")
    tree.heading("Trạng Thái", text="Trạng Thái")

    # Chỉnh độ rộng các cột
    tree.column("STT", width=25, anchor="center")
    tree.column("Tên", width=250, anchor="w")
    tree.column("Số Tiền", width=100, anchor="e")
    tree.column("Trạng Thái", width=150, anchor="e")

    # Thêm các dòng dữ liệu vào Treeview
    for idx, transaction in enumerate(transactions, 1):
        # Kiểm tra nếu có đủ các trường (Tên, Số Tiền, Trạng Thái) trong từng giao dịch
        name = transaction.get("content", "N/A")
        amount = transaction.get("amount", "0")
        status = transaction.get("status", "N/A")
        tree.insert("", "end", values=(idx, name, amount, status))

    style = ttk.Style()
    style.configure("Treeview",
                    highlightthickness=0,  # Tắt đường viền khi chọn
                    bd=0,
                    font=("Arial", 10),
                    rowheight=25)  # Tăng chiều cao hàng

    # Thêm đường kẻ giữa các hàng
    style.configure("Treeview.Heading",
                    font=("Arial", 10, "bold"),
                    relief="solid")  # Đặt đường kẻ cho tiêu đề cột
    style.configure("Treeview", relief="solid")  # Đặt đường kẻ cho các dòng dữ liệu

    # Chạy giao diện
    root.mainloop()


if __name__ == "__main__":
    # Đọc dữ liệu từ file processed_transactions.json
    file_path = "processed_transactions.json"
    transactions = read_transactions(file_path)

    # Tạo giao diện và hiển thị danh sách giao dịch
    create_gui(transactions)
