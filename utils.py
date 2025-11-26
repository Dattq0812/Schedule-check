import re # Thư viện xử lý biểu thức chính quy để xóa thẻ HTML
from datetime import datetime as dt
from datetime import timedelta
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
def format_upcoming_schedule(schedule_list):
    # 1. Kiểm tra danh sách rỗng
    if not schedule_list:
        return "😴 Không tìm thấy dữ liệu lịch học."

    # 2. Lấy ngày hiện tại
    now = dt.now()
    #now = dt.strptime("2025-11-29", "%Y-%m-%d")  # Dùng ngày cố định để test
    today_date = now.date()
    
    # Tính ngày giới hạn (2 ngày sau) để hiển thị trong tiêu đề
    end_date = today_date + timedelta(days=2)
    
    message = f"📅 **LỊCH HỌC 2 NGÀY TỚI**\n"
    message += f"*(Ngày {today_date + timedelta(days=1):%d/%m} Và {end_date:%d/%m})*\n"
    message += "========================\n\n"
    
    count = 0
    
    # Mẹo: Sắp xếp danh sách theo ngày tăng dần trước khi duyệt
    # Để đảm bảo lịch Ngày mai hiện trước, Ngày kia hiện sau
    schedule_list.sort(key=lambda x: dt.strptime(x['date'], "%d/%m/%Y"))

    for item in schedule_list:
        date_str = item.get('date', '')
        try:
            # Chuyển chuỗi ngày học thành object date
            item_date = dt.strptime(date_str, "%d/%m/%Y").date()
            
            # 3. Tính khoảng cách ngày (Delta)
            delta = (item_date - today_date).days
            
            # Kiểm tra: Chỉ lấy Ngày mai (1) và Ngày kia (2)
            if 1 <= delta <= 2:
                # Xác định nhãn ngày cho thân thiện
                day_label = "NGÀY MAI" if delta == 1 else "NGÀY KIA"
                
                message += f"🔔 **{day_label} ({item['day']} - {date_str})**\n"
                message += f"📖 Môn: **{item['subject']}**\n"
                message += f"⏰ Thời gian: {item['time']}\n"
                message += f"🏫 Phòng: {item['room']}\n"
                message += "------------------------\n"
                count += 1
                
        except ValueError:
            continue
    # 4. Xử lý trường hợp không có môn nào
    if count == 0:
        message += "🎉 Tuyệt vời! 2 ngày tới bạn không có lịch học nào.\n"
        
    return message

def clean_exam_data(raw_exam_list):
    """Làm sạch dữ liệu lịch thi từ JSON thô"""
    cleaned_list = []
    for item in raw_exam_list:
        cleaned_item = {
            'CurriculumName': item.get('CurriculumName', 'Không rõ tên môn'),
            'NgayThi': item.get('NgayThi', ''),
            'GioThi': item.get('GioThi', ''),
            'PhongThi': item.get('PhongThi', ''),
            'DiaDiem': item.get('DiaDiem', ''),
            'HinhThucThi': item.get('HinhThucThi', ''),
            'SBD': item.get('SBD', None)  # Số báo danh có thể là None
        }
        cleaned_list.append(cleaned_item)
    return cleaned_list
def format_exam_schedule(exam_list):
    # 1. Kiểm tra danh sách rỗng
    if not exam_list:
        return "🎉 Bạn chưa có lịch thi nào. Ăn ngon ngủ yên nhé!"

    now = dt.now()
    today_date = now.date()

    message = "🏆 **DANH SÁCH CÁC MÔN SẮP THI**\n"
    message += "========================\n\n"
    
    count = 0
    
    # Sắp xếp lịch thi theo ngày tăng dần để môn nào thi trước hiện lên đầu
    # Lưu ý: Cần đảm bảo 'NgayThi' đúng định dạng dd/mm/yyyy
    exam_list.sort(key=lambda x: dt.strptime(x['NgayThi'], "%d/%m/%Y"))

    for item in exam_list:
        date_str = item.get('NgayThi', '')
        
        try:
            # Chuyển chuỗi ngày thi thành object date
            exam_date = dt.strptime(date_str, "%d/%m/%Y").date()
            
            # Tính khoảng cách ngày
            delta = (exam_date - today_date).days
            
            # Chỉ hiện các môn thi từ hôm nay trở đi (Không hiện môn đã thi qua rồi)
            if delta >= 0:
                # --- LOGIC CẢNH BÁO ---
                icon = "📅"
                warning = ""
                
                if delta == 0:
                    icon = "🚨"
                    warning = " (HÔM NAY THI!)"
                elif delta == 1:
                    icon = "⚡"
                    warning = " (NGÀY MAI!)"
                elif delta <= 2:
                    icon = "⚠️"
                    warning = " (Sắp thi!)"

                # Tạo nội dung tin nhắn
                message += f"{icon} **{item['CurriculumName']}** {warning}\n"
                message += f"⏰ **{item['GioThi']}** - Ngày **{date_str}**\n"
                message += f"🏫 Phòng: **{item['PhongThi']}** ({item['DiaDiem']})\n"
                message += f"📝 Hình thức: {item['HinhThucThi']}\n"
                
                # Kiểm tra xem có Số báo danh chưa (vì dữ liệu mẫu của bạn SBD là None)
                sbd = item.get('SBD')
                if sbd:
                    message += f"🔢 SBD: **{sbd}**\n"
                
                message += "------------------------\n"
                count += 1
                
        except ValueError:
            continue

    if count == 0:
        message += "🎉 Bạn đã hoàn thành tất cả các môn thi (hoặc chưa có lịch mới).\n"
        
    return message

def get_notification_message(schedule_list, exam_list):
    """
    Kiểm tra xem có môn nào học/thi sau đúng 2 ngày nữa không.
    Trả về nội dung thông báo hoặc None.
    """
    now = dt.now().date()
    target_date = now + timedelta(days=2) # Ngày mục tiêu (Ngày kia)
    
    msg_list = []
    
    # 1. KIỂM TRA LỊCH HỌC
    if schedule_list:
        for item in schedule_list:
            try:
                # Giả sử format ngày là dd/mm/yyyy
                item_date = dt.strptime(item.get('date', ''), "%d/%m/%Y").date()
                if item_date == target_date:
                    msg_list.append(f"📚 **Học:** {item['subject']} ({item['time']}) tại {item['room']}")
            except:
                continue

    # 2. KIỂM TRA LỊCH THI (Quan trọng hơn)
    if exam_list:
        for item in exam_list:
            try:
                item_date = dt.strptime(item.get('NgayThi', ''), "%d/%m/%Y").date()
                if item_date == target_date:
                    msg_list.append(f"🚨 **THI:** {item['CurriculumName']} ({item['GioThi']}) tại {item['PhongThi']}")
            except:
                continue

    # 3. TỔNG HỢP TIN NHẮN
    if msg_list:
        text = f"🔔 **NHẮC NHỞ LỊCH TRÌNH NGÀY {target_date.strftime('%d/%m')}**\n"
        text += "(Còn 2 ngày nữa để chuẩn bị nha!)\n"
        text += "--------------------------------\n"
        text += "\n".join(msg_list)
        return text
    
    return None # Không có gì thì trả về None