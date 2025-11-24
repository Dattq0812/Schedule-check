import re # Thư viện xử lý biểu thức chính quy để xóa thẻ HTML

def clean_html(raw_html):
    """Xóa các thẻ HTML như <span>, <br> ra khỏi chuỗi"""
    if not raw_html:
        return ""
    # Thay thế <br> bằng xuống dòng hoặc dấu cách
    text = str(raw_html).replace('</br>', ' - ').replace('<br/>', ' - ')
    # Xóa tất cả các thẻ còn lại <...>
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', text)
    return cleantext.strip()

def parse_schedule_data(json_data):
    """Chuyển JSON thô của trường thành List đơn giản cho Bot"""
    raw_list = json_data.get('ResultDataSchedule', [])
    parsed_list = []

    for item in raw_list:
        # Xử lý tên phòng học (đang bị dính thẻ HTML)
        raw_room = item.get('RoomID', '')
        clean_room = clean_html(raw_room)

        # Tạo object gọn gàng
        schedule_item = {
            'subject': item.get('CurriculumName', 'Không rõ tên môn'),
            'date': item.get('Date', ''),      # Ví dụ: 24/11/2025
            'day': item.get('Thu', ''),        # Ví dụ: Thứ Hai
            'room': clean_room,                # Ví dụ: DMT012 - (Cơ sở 613 Âu Cơ)
            'time': f"{item.get('BeginTime', '')} - Tiết {item.get('EndTime', '')}", 
            'teacher': item.get('FullName', 'Giảng viên chưa cập nhật'),
            'week': item.get('Week', '')
        }
        parsed_list.append(schedule_item)
    
    return parsed_list

# Hàm định dạng lịch học thành chuỗi thông báo đẹp mắt
def format_schedule_message(schedule_list):
    if not schedule_list:
        return "😴 Tuần này bạn không có lịch học nào cả. Xõa thôi!"

    # Sắp xếp lịch theo ngày (nếu cần)
    # schedule_list.sort(key=lambda x: x['date'])

    # Lấy thông tin tuần từ item đầu tiên
    week_info = schedule_list[0].get('week', '')
    
    message = f"📅 **LỊCH HỌC TUẦN {week_info}**\n"
    message += "========================\n\n"

    for item in schedule_list:
        message += f"📖 **{item['subject']}**\n"
        message += f"⏰ {item['day']} ({item['date']}) | {item['time']}\n"
        message += f"🏫 **Phòng:** {item['room']}\n"
        message += f"👨‍🏫 **GV:** {item['teacher']}\n"
        message += "------------------------\n"
    
    return message


