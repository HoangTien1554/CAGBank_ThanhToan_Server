import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import json
from pystray import MenuItem as item, Icon
from PIL import Image, ImageDraw
import threading
import os
import datetime
import subprocess

# Đường dẫn file JSON
config_path = "data/config.json"
file_path = "data/processed_transactions.json"
txt_file = "data/daily_summary.txt"

# server_script = os.path.join(os.path.dirname(__file__), "QRCode_ThanhToan_Server.py")

# Hàm đọc file JSON
def read_json(file):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Lỗi khi đọc file JSON {file}: {e}")
        return {}

# Đọc cấu hình
config = read_json(config_path)

# Lấy giá trị mặc định nếu không có trong file JSON
ahk_file = config.get("ahk_file", "CAGBank_NapTien_Gcafe.ahk")
api_key = config.get("api_key", "your_api_key")
api_url = config.get("api_url", "https://your_api_url")
last_id = config.get("last_id", 0)

# Hàm ghi file JSON
def write_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)  # Ghi file với định dạng đẹp

def clear_transactions():
    """Xóa toàn bộ dữ liệu trong bảng giao diện."""
    for item in tree.get_children():
        tree.delete(item)

    # Cập nhật nhãn tổng tiền về 0
    total_label.config(text="Tổng Kết: 0 VND")

# Hàm cập nhật dữ liệu
def update_transactions():
    global last_id
    config = read_json(config_path)
    last_id = config.get("last_id", 0)  # Cập nhật last_id mới nhất từ config

    transactions = read_json(file_path)

    # Xóa dữ liệu cũ
    clear_transactions()

    total_amount = 0  # Tổng tiền

    # Lọc ra những giao dịch mới (ID > last_id)
    new_transactions = [t for t in transactions if t.get("id", 0) > last_id]

    # Sắp xếp danh sách theo ID tăng dần
    new_transactions.sort(key=lambda x: x.get("id", 0))

    # Thêm dữ liệu mới vào đầu bảng
    for idx, transaction in enumerate(new_transactions, 1):
        name = transaction.get("content", "N/A")
        amount = transaction.get("amount", "0")
        date = transaction.get("datetime", "N/A")  # Đổi T thành khoảng trắng
        status = transaction.get("status", "N/A")

        try:
            total_amount += int(amount)
        except ValueError:
            pass

        # Chèn vào đầu danh sách thay vì cuối
        tree.insert("", 0, values=(idx, name, f"{int(amount):,} VND", date, status))

    # Cập nhật tổng tiền
    total_label.config(text=f"Tổng Kết: {total_amount:,} VND")

    # Lên lịch cập nhật sau 2 giây
    root.after(2000, update_transactions)

def get_last_id():
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            transactions = json.load(f)
        if not transactions:
            return 0  # Trả về 0 nếu file rỗng
        return transactions[-1].get("id", 0)  # Lấy ID của dòng cuối cùng
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

def write_to_txt():
    # Đọc dữ liệu từ file JSON
    transactions = read_json(file_path)

    # Đọc last_id từ config.json
    config = read_json(config_path)
    last_id = config.get("last_id", 0)

    # Lọc ra các giao dịch có ID lớn hơn last_id
    new_transactions = [t for t in transactions if t.get("id", 0) > last_id]

    # Tính tổng số lượt giao dịch
    total_transactions = len(new_transactions)

    # Tính tổng số tiền (chỉ lấy số hợp lệ)
    total_amount = sum(int(t.get("amount", 0)) for t in new_transactions if str(t.get("amount", "0")).isdigit())

    # Lấy ngày và thời gian hiện tại
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")

    # Ghi dữ liệu vào file TXT
    with open(txt_file, "a", encoding="utf-8") as f:
        f.write(f"{today} {current_time} - {total_transactions} giao dịch - {total_amount:,} VND\n")

    print(f"Đã ghi {total_transactions} giao dịch, tổng tiền {total_amount:,} VND vào {txt_file}")


def tong_ket_doanh_thu():
    # Hiển thị hộp thoại xác nhận
    confirm = messagebox.askyesno("Xác nhận", "Sau khi tổng kết sẽ xoá hết lịch sử giao dịch!!!")

    if confirm:
        new_last_id = get_last_id()  # Lấy ID của giao dịch cuối cùng
        write_to_txt() # Lưu tổng kết vào file TXT
        update_config("last_id", new_last_id)  # Cập nhật last_id trong config
        clear_transactions()  # Xóa dữ liệu hiển thị trên giao diện
        messagebox.showinfo("Xác nhận", "Tổng kết doanh thu thành công!")

        # Đọc lại giá trị last_id mới để đảm bảo dữ liệu hiển thị đúng
        global last_id
        last_id = new_last_id

def update_config(key, value):
    config_data = read_json(config_path)  # Đọc dữ liệu hiện có
    config_data[key] = value  # Cập nhật giá trị mới
    write_json(config_path, config_data)  # Ghi lại file mà không mất dữ liệu cũ

# Hàm chỉnh sửa cấu hình
def open_config_window():
    global ahk_file, api_key, api_url

    def change_CSM():
        update_config("ahk_file", "CAGBank_NapTien_CSM.ahk")
        messagebox.showinfo("Thành công", f"Đã đổi sang CSM Billing")
        config_window.deiconify()

    def change_FNet():
        update_config("ahk_file", "CAGBank_NapTien_FNet.ahk")
        messagebox.showinfo("Thành công", "Đã đổi sang FNet Billing")
        config_window.deiconify()


    def change_Gcafe():
        update_config("ahk_file", "CAGBank_NapTien_Gcafe.ahk")
        messagebox.showinfo("Thành công", f"Đã đổi sang Gcafe Billing")
        config_window.deiconify()

    def close_config_window():
        config_window.destroy()
        root.attributes("-disabled", False)  # Bật lại cửa sổ chính
        root.deiconify()

    def save_config():
        global ahk_file, api_key, api_url
        api_key = api_entry.get()
        api_url = url_entry.get()
        close_config_window()
        config_data = {"ahk_file": ahk_file, "api_key": api_key, "api_url": api_url}
        write_json(config_path, config_data)
        close_config_window()

    def cancel_config():
        config_data = {"ahk_file": ahk_file, "api_key": api_key, "api_url": api_url}
        write_json(config_path, config_data)
        close_config_window()

    def on_closing():
        """Ẩn cửa sổ chính thay vì đóng hẳn ứng dụng"""
        root.withdraw()

    config_window = tk.Toplevel(root)
    config_window.title("Cấu hình")
    config_window.geometry("350x200")

    config_window.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() - config_window.winfo_width()) // 2
    y = root.winfo_y() + (root.winfo_height() - config_window.winfo_height()) // 2
    config_window.geometry(f"+{x}+{y}")

    root.attributes("-disabled", True)
    config_window.protocol("WM_DELETE_WINDOW", close_config_window)
    root.protocol("WM_DELETE_WINDOW", on_closing)

    tk.Label(config_window, text="AHK File:").pack()

    button_frame = tk.Frame(config_window)
    button_frame.pack(pady=5)

    tk.Button(button_frame, text="CSM Billing", command=change_CSM).pack(side="left", expand=True, padx=5, pady=5)
    tk.Button(button_frame, text="FNet Billing", command=change_FNet).pack(side="left", expand=True, padx=5, pady=5)
    tk.Button(button_frame, text="Gcafe Billing", command=change_Gcafe).pack(side="left", expand=True, padx=5, pady=5)

    tk.Label(config_window, text="API Key:").pack()
    api_entry = tk.Entry(config_window, width=40)
    api_entry.pack()
    api_entry.insert(0, api_key)

    tk.Label(config_window, text="API URL:").pack()
    url_entry = tk.Entry(config_window, width=40)
    url_entry.pack()
    url_entry.insert(0, api_url)

    apply_button_frame = tk.Frame(config_window)
    apply_button_frame.pack(pady=5)

    tk.Button(apply_button_frame, text="Hủy", command=cancel_config).pack(side="left", expand=True, padx=5)
    tk.Button(apply_button_frame, text="Lưu", command=save_config).pack(padx=5)

# Hàm ẩn cửa sổ chính
def hide_window():
    root.withdraw()

# Hàm hiện lại cửa sổ chính
def show_window(icon, item):
    root.deiconify()  # Hiện cửa sổ chính
    root.lift()  # Đưa cửa sổ lên trên
    root.attributes("-topmost", True)  # Đảm bảo cửa sổ trên cùng

# Hàm thoát ứng dụng
def exit_app(icon, item):
    icon.stop()  # Dừng System Tray
    root.quit()

# Tạo biểu tượng trong System Tray
def create_tray_icon():
    image = Image.open("data/CAGPRO.ico")

    menu = (item("Hiện cửa sổ", show_window), item("Thoát", exit_app))

    icon = Icon("app_icon", image, menu=menu)
    icon.run()

def insert_transaction_ui(name, amount, date, status):
    tree.insert("", "end", values=("*", name, f"{int(amount):,} VND", date, status))

def on_closing():
    """Ẩn cửa sổ chính thay vì đóng hẳn ứng dụng"""
    root.withdraw()

def run_qrcode_server():
    exe_path = os.path.join(os.getcwd(), "dist/QRCode_ThanhToan_Server.exe")  # Đường dẫn file exe
    try:
        subprocess.Popen(exe_path, creationflags=subprocess.CREATE_NO_WINDOW)  # Chạy ẩn cửa sổ
    except FileNotFoundError:
        print("Lỗi: Không tìm thấy file QRCode_ThanhToan_Server.exe!")

# Giao diện chính
root = tk.Tk()
root.title("Danh Sách Giao Dịch")
root.geometry("600x400")
root.iconbitmap("data/CAGPRO.ico")

main_button_frame = tk.Frame(root)
main_button_frame.pack(anchor="nw", padx=5, pady=5)

# Nút mở cấu hình
settings_button = tk.Button(main_button_frame, text="⚙ Cấu Hình", command=open_config_window)
summary_button = tk.Button(main_button_frame, text="Tổng kết doanh thu", command=tong_ket_doanh_thu)
settings_button.pack(side="left", expand=True, padx=5)
summary_button.pack(side="left", expand=True, padx=5)

# Treeview
tree = ttk.Treeview(root, columns=("STT", "Tài khoản", "Số Tiền", "Ngày", "Trạng Thái"), show="headings")
tree.pack(padx=10, pady=2, fill=tk.BOTH, expand=True)

# Cấu hình cột
tree.heading("STT", text="STT")
tree.heading("Tài khoản", text="Tài khoản")
tree.heading("Số Tiền", text="Số Tiền")
tree.heading("Ngày", text="Ngày")
tree.heading("Trạng Thái", text="Trạng Thái")

tree.column("STT", width=35, anchor="center")
tree.column("Tài khoản", width=150, anchor="w")
tree.column("Số Tiền", width=100, anchor="e")
tree.column("Ngày", width=175, anchor="center")
tree.column("Trạng Thái", width=100, anchor="center")

# Nhãn hiển thị tổng tiền
total_label = tk.Label(root, text="Tổng Tiền: 0 VND", font=("Arial", 12, "bold"), fg="red")
total_label.pack(pady=5, side="right", padx=5)

# Gọi hàm cập nhật dữ liệu
update_transactions()

# # Chạy file QRCode_ThanhToan_Server.py trong nền
# subprocess.Popen(["python", server_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

run_qrcode_server()

# Chạy System Tray trong luồng khác để không chặn giao diện
threading.Thread(target=create_tray_icon, daemon=True).start()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Chạy ứng dụng
root.mainloop()
