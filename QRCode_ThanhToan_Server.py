import subprocess
import os

# Đường dẫn đến file AHK
ahk_file = "CAGBank_NapTien_Gcafe.ahk"

# Dữ liệu mới để thay đổi
TaiKhoan = "tien"  # Giá trị mới cho TaiKhoan
SoTien = 100000  # Giá trị mới cho SoTien

# Mở file .ahk để đọc
with open(ahk_file, "r", encoding="utf-8") as file:
    lines = file.readlines()

# Duyệt qua từng dòng và thay đổi giá trị của TaiKhoan và SoTien
for i, line in enumerate(lines):
    if "TaiKhoan := " in line:  # Tìm dòng chứa TaiKhoan
        lines[i] = f'TaiKhoan := "{TaiKhoan}"\n'  # Thay thế giá trị mới
    if "SoTien := " in line:  # Tìm dòng chứa SoTien
        lines[i] = f"SoTien := {SoTien}\n"  # Thay thế giá trị mới

# Ghi lại các thay đổi vào file .ahk
with open(ahk_file, "w", encoding="utf-8") as file:
    file.writelines(lines)

print(f"Đã thay đổi TaiKhoan thành '{TaiKhoan}' và SoTien thành {SoTien} trong file {ahk_file}")

# Mở file .ahk sau khi thay đổi
# Sử dụng os.startfile() để mở file bằng chương trình mặc định liên kết với .ahk (AutoHotkey)
os.startfile(ahk_file)
