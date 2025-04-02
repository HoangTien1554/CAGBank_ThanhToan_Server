import base64

# Chuỗi cần mã hóa
text = "76030f80652559028160acbcae6fb0039585d4ed3604faec742731478a4d7526"

# Mã hóa sang Base64
encoded_text = base64.b64encode(text.encode()).decode()

print("Chuỗi đã mã hóa:", encoded_text)
