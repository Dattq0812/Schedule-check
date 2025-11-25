import random

GREETINGS = [
    "Hế lô! Ngày mới tốt lành nha ☀️",
    "Chào đại ca! Cần em giúp gì không? 😎",
    "Bot đã sẵn sàng phục vụ! 🫡",
    "Lại là mình đây! Check lịch hay check thi nào? 🤔"
]

LOADING_MESSAGES = [
    "Đang chạy lên phòng đào tạo lấy lịch... 🏃‍♂️",
    "Đợi xíu nha, mạng trường hơi lag... 🐢",
    "Đang lục lọi dữ liệu... 🔍"
]

def get_random_greeting():
    return random.choice(GREETINGS)

def get_loading_text():
    return random.choice(LOADING_MESSAGES)