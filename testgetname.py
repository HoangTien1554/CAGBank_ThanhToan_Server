import psutil

search_keyword = "GCafe+ server".lower()

matching_processes = [
    p.info["name"]
    for p in psutil.process_iter(attrs=["name"])
    if p.info["name"] and search_keyword in p.info["name"].lower()
]

if matching_processes:
    print("Ứng dụng đang chạy:")
    for process in matching_processes:
        print(process)
else:
    print("Không tìm thấy ứng dụng nào chứa 'GCafe+ server'")