import requests
import urllib3
import login
from datetime import datetime
import utils
import crawler_Schedule

# Tắt cảnh báo SSL (nếu có)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Giả lập trình duyệt thật để tránh bị chặn
session = requests.Session()

token = login.loging()

exam_headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7,fr-FR;q=0.6,fr;q=0.5',
    'Connection': 'keep-alive',
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
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
    }

def get_exam() :
    params = crawler_Schedule.get_schedule_date()
    if not token:
        print("Không thể lấy lịch thi vì đăng nhập thất bại.")
        return None
    response_exam = session.get('https://portal_api.vhu.edu.vn/api/student/exam', params=params, headers=exam_headers, verify=False)
    print(f"Status Code lấy thông tin lịch thi: {response_exam.status_code}")
    if response_exam.status_code != 200:
        print("Lấy thông tin lịch thi thất bại!")
        return None 
    print("Lấy thông tin lịch thi thành công.")
    date_exam = response_exam.json()
    print(f"Dữ liệu lịch thi: {date_exam}")
    cleaned_exam_list = utils.clean_exam_data(date_exam)
    #formatted_message = utils.format_exam_schedule(cleaned_exam_list)
    #print(formatted_message)
    return cleaned_exam_list