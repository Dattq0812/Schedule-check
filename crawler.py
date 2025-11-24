from sqlite3 import Date
import requests
from bs4 import BeautifulSoup
import json
import urllib3
import login
from datetime import datetime
import utils
# Tắt cảnh báo SSL (nếu có)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# 1. Cấu hình thông tin mục tiêu
SCHEDULE_URL = 'https://portal_api.vhu.edu.vn/api/student/yearandterm' # URL trang lịch học
# Giả lập trình duyệt thật để tránh bị chặn
session = requests.Session()

token = login.loging()

schedule_headers = {
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
def get_schedule():
    print(f"Đang gửi yêu cầu lấy lịch học đến: {SCHEDULE_URL}")
    if not token:
        print("Không thể lấy lịch học vì đăng nhập thất bại.")
        return None
    print(f"Token nhận được: {token[:20]}...")

    #Lấy lịch học
   
    response_schedule = session.get(SCHEDULE_URL, headers=schedule_headers, verify=False)
    #print(f"Status Code lấy lịch học: {response_schedule.status_code}")

    if response_schedule.status_code != 200:
        print("Lấy lịch học thất bại!")
        return None
    
    print("Lấy lịch học thành công. Đang xử lý dữ liệu...")
   # print(f"Response Text Lịch học: {response_schedule.text}")
#
    schedule_data = response_schedule.json()
    #print(f"Dữ liệu lịch học: {schedule_data}")
    current_time = [schedule_data.get("CurrentYear"), schedule_data.get("CurrentTerm")]

    #print(f"Năm học hiện tại: {current_time[0]}, Học kỳ hiện tại: {current_time[1]}")

    params = {
        'namhoc': current_time[0],
        'hocky': current_time[1],
    }

    #Lấy ngày hiện tại để xác định tuần học
    date_now = datetime.now()

    #Xác định tuần học hiện tại
    response_week = session.get('https://portal_api.vhu.edu.vn/api/student/WeekSchedule', params=params, headers=schedule_headers, verify=False)
    #print(f"Status Code lấy lịch theo tuần: {response_week.status_code}")
    if response_week.status_code != 200:
        print("Lấy tuần học thất bại!")
        return None
    week_list = response_week.json()
    #print(f"Dữ liệu tuần học: {week_list}")
    cur_week = None
    for date in week_list:
        b_date = datetime.strptime(date["BeginDate"], "%d/%m/%Y")
        e_date = datetime.strptime(date["EndDate"], "%d/%m/%Y")
        if b_date <= date_now <= e_date:
            cur_week = date.get("Week")
            # print(f"Ngày hiện tại: {date_now}")
            # print(f"Tuần hiện tại: {cur_week}")
            break
    if cur_week is None:
        print("Không xác định được tuần học hiện tại.")
        return None
    params['tuan'] = cur_week
    response_schedule_info = session.get('https://portal_api.vhu.edu.vn/api/student/DrawingSchedules', params=params, headers=schedule_headers, verify=False)
    print(f"Status Code lấy thông tin lịch học: {response_schedule_info.status_code}")
    if response_schedule_info.status_code != 200:
        print("Lấy thông tin lịch học thất bại!")
        return None
    print("Lấy thông tin lịch học thành công.")
    schedule_info = response_schedule_info.text
    #Làm sạch thông tin lịch học
    cleaned_schedule = utils.parse_schedule_data(response_schedule_info.json())
    #Chuyển đổi lịch học thành tin nhắn đẹp mắt
    formatted_message = utils.format_schedule_message(cleaned_schedule)
    print(formatted_message)
    
    return cleaned_schedule

