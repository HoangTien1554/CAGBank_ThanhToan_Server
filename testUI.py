import sys
import json
import subprocess
import psutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QLabel, QVBoxLayout, QWidget, QTableWidget, \
    QSystemTrayIcon, QMenu, QDialog, QLineEdit, QHBoxLayout, QPushButton, QHeaderView, QTableWidgetItem, QMessageBox
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QSharedMemory, QTimer
import datetime
import pyautogui

width, height = pyautogui.size()

qr_process = None

shared_memory = QSharedMemory("TestUI_Unique_Instance")

if not shared_memory.create(1):  # Nếu ứng dụng đã chạy
    sys.exit()

def update_config(key, value):
    config = load_config("data/config.json")
    config[key] = value
    write_json("data/config.json", config)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def load_config(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def load_transactions(file_path, last_id):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            transactions = json.load(file)
            return [t for t in transactions if t["transactionID"] > last_id][::-1]  # Lọc và đảo ngược danh sách
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def start_qr_code_server():
    global qr_process
    if not is_qr_code_running():
        qr_process = subprocess.Popen(["QRCode_ThanhToan_Server.exe"], creationflags=subprocess.CREATE_NO_WINDOW)

def is_qr_code_running():
    for proc in psutil.process_iter(attrs=['name']):
        if proc.info['name'] == "QRCode_ThanhToan_Server.exe":
            return True
    return False

def stop_qr_code_server():
    for proc in psutil.process_iter(attrs=['name', 'pid']):
        if proc.info['name'] == "QRCode_ThanhToan_Server.exe":
            proc.terminate()


class ConfigWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cấu hình")
        self.setGeometry(200, 200, 350, 320)
        self.setWindowModality(Qt.ApplicationModal)

        config = load_config("data/config.json")
        self.ahk_file = config.get("ahk_file", "")
        self.token = config.get("token", "")
        self.api_url = config.get("api_url", "")
        self.bank_number = config.get("bank_number", "")
        self.password = config.get("password", "")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("AHK File:"))

        button_layout = QHBoxLayout()
        self.csm_button = QPushButton("CSM Billing")
        self.csm_button.clicked.connect(lambda: self.change_ahk("CAGBank_NapTien_CSM.ahk"))
        button_layout.addWidget(self.csm_button)

        self.fnet_button = QPushButton("FNet Billing")
        self.fnet_button.clicked.connect(lambda: self.change_ahk("CAGBank_NapTien_FNet.ahk"))
        button_layout.addWidget(self.fnet_button)

        self.gcafe_button = QPushButton("Gcafe Billing")
        self.gcafe_button.clicked.connect(lambda: self.change_ahk("CAGBank_NapTien_Gcafe.ahk"))
        button_layout.addWidget(self.gcafe_button)

        layout.addLayout(button_layout)

        layout.addWidget(QLabel("API URL:"))
        self.url_entry = QLineEdit(self.api_url)
        layout.addWidget(self.url_entry)

        layout.addWidget(QLabel("Số tài khoản:"))
        self.bank_entry = QLineEdit(str(self.bank_number))
        layout.addWidget(self.bank_entry)

        layout.addWidget(QLabel("Mật khẩu:"))
        self.password_entry = QLineEdit(self.password)
        layout.addWidget(self.password_entry)

        layout.addWidget(QLabel("TOKEN:"))
        self.token_entry = QLineEdit(self.token)
        layout.addWidget(self.token_entry)

        # Tạo nút Hủy và Lưu
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Huỷ")
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("Lưu")
        self.save_button.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def change_ahk(self, file_name):
        update_config("ahk_file", file_name)
        print(f"Đã đổi sang {file_name}")

    def save_config(self):
        """Lưu cấu hình vào file config.json"""
        reply = QMessageBox.question(
            self, "Xác nhận", "Bạn có chắc chắn đã nhập đúng dữ liệu?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            update_config("api_url", self.url_entry.text())
            update_config("bank_number", self.bank_entry.text())
            update_config("password", self.password_entry.text())
            update_config("token", self.token_entry.text())
            QMessageBox.information(self, "Thành công", "Đã lưu cấu hình!")
            self.close()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Danh Sách Giao Dịch")
        self.setGeometry(100, 100, 800, 400)
        self.setWindowIcon(QIcon("data/CAGPRO.ico"))

        menubar = self.menuBar()
        settings_menu = menubar.addMenu("Tuỳ chọn")

        self.settings_action = QAction("Cấu Hình", self)
        self.settings_action.triggered.connect(self.open_config_window)
        settings_menu.addAction(self.settings_action)

        self.summary_action = QAction("Tổng kết doanh thu", self)
        self.summary_action.triggered.connect(self.tong_ket_doanh_thu)
        settings_menu.addAction(self.summary_action)

        layout = QVBoxLayout()

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Tài khoản", "Số Tiền", "Ngày", "Trạng Thái"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.total_label = QLabel("Tổng Tiền: 0 VND")
        self.total_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.total_label.setStyleSheet("color: red;")
        layout.addWidget(self.total_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("data/CAGPRO.ico"))
        self.tray_menu = QMenu()

        show_action = QAction("Mở lại", self)
        show_action.triggered.connect(self.show_main_window)
        self.tray_menu.addAction(show_action)

        exit_action = QAction("Thoát", self)
        exit_action.triggered.connect(self.close_application)
        self.tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Khởi tạo QTimer để tự động cập nhật dữ liệu mỗi 5 giây
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_data)
        self.timer.start(1000)  # Cập nhật mỗi 5000ms (5 giây)

        self.load_data()  # Load dữ liệu ngay khi khởi động
        start_qr_code_server()

    def load_data(self):
        config = load_config("data/config.json")
        last_id = config.get("last_id", 0)
        transactions = load_transactions("data/processed_transactions.json", last_id)
        self.table.setRowCount(len(transactions))
        total_amount = 0

        for row, transaction in enumerate(transactions):
            self.table.setItem(row, 0, QTableWidgetItem(transaction.get("content", "")))

            amount = transaction.get("amount", 0)
            formatted_amount = f"{amount:,} VND"
            amount_item = QTableWidgetItem(formatted_amount)
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 1, amount_item)

            date_item = QTableWidgetItem(transaction.get("datetime", ""))
            date_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, date_item)

            status_item = QTableWidgetItem(transaction.get("status", ""))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, status_item)

            total_amount += amount

        self.total_label.setText(f"Tổng Tiền: {total_amount:,} VND")

    def open_config_window(self):
        config_dialog = ConfigWindow(self)
        config_dialog.exec_()

    def tong_ket_doanh_thu(self):
        # 🔹 Hiển thị hộp thoại xác nhận
        confirm = QMessageBox.question(self, "Xác nhận",
                                       "Sau khi tổng kết sẽ xoá hết lịch sử giao dịch!!!\nBạn có chắc chắn không?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.No:
            return

        # 🔹 Đọc dữ liệu giao dịch
        config = load_config("data/config.json")
        last_id = config.get("last_id", 0)
        transactions = load_transactions("data/processed_transactions.json", last_id)

        # 🔹 Lọc ra các giao dịch mới
        new_transactions = [t for t in transactions if t.get("transactionID", 0) > last_id]
        total_transactions = len(new_transactions)
        total_amount = sum(int(t.get("amount", 0)) for t in new_transactions if str(t.get("amount", "0")).isdigit())

        # 🔹 Ghi tổng kết vào file TXT
        now = datetime.datetime.now()
        today = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")

        summary_file = "data/daily_summary.txt"
        with open(summary_file, "a", encoding="utf-8") as f:
            f.write(f"{today} {current_time} - {total_transactions} giao dịch - {total_amount:,} VND\n")

        # 🔹 Cập nhật last_id trong config
        if new_transactions:
            new_last_id = max(t["transactionID"] for t in new_transactions)
            update_config("last_id", new_last_id)

        # 🔹 Xoá dữ liệu hiển thị trên giao diện
        self.table.setRowCount(0)
        self.total_label.setText("Tổng Tiền: 0 VND")

        QMessageBox.information(self, "Thành công", "Tổng kết doanh thu thành công!")

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage("Ứng dụng", "Ứng dụng đang chạy dưới system tray", QSystemTrayIcon.Information, 2000)

    def show_main_window(self):
        self.showNormal()
        self.activateWindow()

    def close_application(self):
        self.tray_icon.hide()
        stop_qr_code_server()
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    shared_memory = QSharedMemory("TestUI_Unique_Instance")
    if not shared_memory.create(1):  # Kiểm tra nếu ứng dụng đã chạy
        print("Ứng dụng đã chạy, không thể mở thêm!")
        sys.exit()

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
