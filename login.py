import requests
import urllib3
import os
from dotenv import load_dotenv


# Tắt cảnh báo SSL (nếu có)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# 1. Cấu hình thông tin mục tiêu
LOGIN_URL = 'https://portal_api.vhu.edu.vn/api/authenticate/authpsc' # URL trang xử lý đăng nhập

# Giả lập trình duyệt thật để tránh bị chặn
HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7,fr-FR;q=0.6,fr;q=0.5',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://portal.vhu.edu.vn',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
    'apiKey': 'pscRBF0zT2Mqo6vMw69YMOH43IrB2RtXBS0EHit2kzvL2auxaFJBvw==',
    'clientId': 'vhu',
    'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

# 2. Thông tin đăng nhập (Thay bằng của bạn để test)
#file .env chứa tài khoản và mật khẩu
# username=your_username
# password=your_password
load_dotenv()
username = os.getenv('username')
password = os.getenv('password')
if username is None or password is None:
    print("Vui lòng thiết lập biến môi trường 'username' và 'password' trong file .env")
    exit(1)
data = {
    'username' : username,
    'password' : password,
    'type': 0
}
# 3. Khởi tạo Session
session = requests.Session()

def loging():
    count = 0
    response = None
    while count < 3:
        print(f"Đang gửi yêu cầu đăng nhập đến: {LOGIN_URL}")

        # Gửi yêu cầu đăng nhập (POST)
        response = session.post(LOGIN_URL, json=data, headers=HEADERS, verify= False)
        print(f"Đã gửi yêu cầu đăng nhập.")
        print(f"Status Code: {response.status_code}")

        # Kiểm tra xem login thành công không (thường check status code 200 hoặc check url chuyển hướng)
        if response.status_code != 200:
            print("Login failed!")
            count += 1
            continue
        break
    
    # print("Login request sent. Checking data...")
    # print(f"Response Text: {response.text}")
    if response is None or response.status_code != 200:
        print("Login failed after 3 attempts.")
        return None
    login_data = response.json()
    token = login_data.get("Token")
    if not token:
        print("Login failed! No token found.")
        return None
    print("Login successful!")
    return token

