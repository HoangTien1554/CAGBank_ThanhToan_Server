import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import json
from pystray import MenuItem as item, Icon
from PIL import Image, ImageDraw
import threading
import datetime


# Đường dẫn file JSON
config_path = "config.json"
file_path = "processed_transactions.json"
txt_file = "daily_summary.txt"

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


# Hàm ghi file JSON
def write_json(file, data):
    try:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Lỗi khi ghi file JSON {file}: {e}")


# Đọc cấu hình
config = read_json(config_path)

# Lấy giá trị mặc định nếu không có trong file JSON
ahk_file = config.get("ahk_file", "CAGBank_NapTien_Gcafe.ahk")
api_key = config.get("api_key", "your_api_key")
api_url = config.get("api_url", "https://your_api_url")


# Hàm cập nhật dữ liệu
def update_transactions():
    transactions = read_json(file_path)

    # Xóa dữ liệu cũ
    for item in tree.get_children():
        tree.delete(item)

    total_amount = 0  # Tổng tiền

    # Thêm dữ liệu mới
    for idx, transaction in enumerate(transactions, 1):
        name = transaction.get("content", "N/A")
        amount = transaction.get("amount", "0")
        date = transaction.get("datetime", "N/A").replace("T", " ")  # Đổi T thành khoảng trắng
        status = transaction.get("status", "N/A")

        try:
            total_amount += int(amount)
        except ValueError:
            pass

        tree.insert("", "end", values=(idx, name, f"{int(amount):,} VND", date, status))

    # Cập nhật tổng tiền
    total_label.config(text=f"Tổng Tiền: {total_amount:,} VND")

    # Lên lịch cập nhật sau 2 giây
    root.after(2000, update_transactions)


import datetime
import json

json_file = "processed_transactions.json"
txt_file = "daily_summary.txt"

def write_to_txt():
    """Ghi tổng hợp dữ liệu vào file TXT và xóa dữ liệu JSON mỗi ngày lúc 23:59:59"""

    # Đọc dữ liệu từ file JSON
    transactions = read_json(json_file)

    # Tính tổng số lượt giao dịch
    total_transactions = len(transactions)

    # Tính tổng số tiền (Đảm bảo chuyển về chuỗi trước khi kiểm tra)
    total_amount = sum(int(t.get("amount", 0)) for t in transactions if str(t.get("amount", "0")).isdigit())

    # Lấy ngày và thời gian hiện tại
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")

    # Ghi dữ liệu vào file TXT
    with open(txt_file, "a", encoding="utf-8") as f:
        f.write(f"{today} {current_time} - {total_transactions} giao dịch - {total_amount:,} VND\n")

    print(f"Đã ghi {total_transactions} giao dịch, tổng tiền {total_amount:,} VND vào {txt_file}")

    # Xóa toàn bộ dữ liệu trong file JSON
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump([], f)

    print(f"Đã xóa dữ liệu trong {json_file}")



# Hàm chỉnh sửa cấu hình
def open_config_window():
    global ahk_file, api_key, api_url

    def change_CSM():
        config_data = {"ahk_file": "CAGBank_NapTien_CSM.ahk", "api_key": api_key, "api_url": api_url}
        write_json(config_path, config_data)
        messagebox.showinfo("Thành công", f"Đã đổi sang CSM Billing")
        config_window.deiconify()


    def change_FNet():
        config_data = {"ahk_file": "CAGBank_NapTien_FNet.ahk", "api_key": api_key, "api_url": api_url}
        write_json(config_path, config_data)
        messagebox.showinfo("Thành công", "Đã đổi sang CSM Billing")
        config_window.deiconify()


    def change_Gcafe():
        config_data = {"ahk_file": "CAGBank_NapTien_Gcafe.ahk", "api_key": api_key, "api_url": api_url}
        write_json(config_path, config_data)
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

    def exit_app(icon, item):
        """Thoát hoàn toàn ứng dụng"""
        icon.stop()  # Dừng System Tray
        root.quit()

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
    tk.Button(button_frame, text="Gcafe Billing", command=change_Gcafe).pack(side="left", expand=False, padx=5, pady=5)

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
    root.deiconify()


# Hàm thoát ứng dụng
def exit_app(icon, item):
    icon.stop()  # Dừng System Tray
    root.quit()


# Tạo biểu tượng trong System Tray
def create_tray_icon():
    image = Image.new("RGB", (64, 64), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 64, 64), fill="blue")

    menu = (item("Hiện cửa sổ", show_window), item("Thoát", exit_app))

    icon = Icon("app_icon", image, menu=menu)
    root.iconify()
    icon.run()


# Giao diện chính
root = tk.Tk()
root.title("Danh Sách Giao Dịch")
root.geometry("600x400")

main_button_frame = tk.Frame(root)
main_button_frame.pack(pady=5)

# Nút mở cấu hình
settings_button = tk.Button(main_button_frame, text="⚙ Cấu Hình", command=open_config_window)
summary_button = tk.Button(main_button_frame, text="Tổng kết doanh thu", command=write_to_txt)
settings_button.pack(side="left", expand=True, padx=5)
summary_button.pack(side="left", expand=True, padx=5)

# Treeview
tree = ttk.Treeview(root, columns=("STT", "Tài khoản", "Số Tiền", "Ngày", "Trạng Thái"), show="headings")
tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

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

# Chạy System Tray trong luồng khác để không chặn giao diện
threading.Thread(target=create_tray_icon, daemon=True).start()

# Ẩn cửa sổ khi chạy
root.withdraw()

# Chạy ứng dụng
root.mainloop()
