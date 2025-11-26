import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re
from datetime import datetime
load_dotenv()

# Cấu hình AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('models/gemini-2.0-flash')

def ask_gemini_about_schedule(user_question, schedule_list, exam):
    """
    user_question: Câu hỏi của sinh viên (VD: "Mai học gì")
    Trả lời bình thường khi sinh viên nhắn tin bình thường.
    Trả về câu trả lời từ AI dựa trên dữ liệu lịch học và lịch thi.
    Chỉ trả lời về lich học và lịch thi dựa trên dữ liệu đã cho khi sinh viên hỏi.
    """
    
    # 1. Tạo Prompt (Kịch bản cho AI)
    current_time = datetime.now().strftime("%H:%M ngày %d/%m/%Y")
    
    # Chuyển data sang string gọn nhẹ để tiết kiệm token
    
    schedule_data_str = json.dumps(schedule_list, ensure_ascii=False)
    exam_data_str = json.dumps(exam, ensure_ascii=False)
    prompt = f"""
    Bạn là một trợ lý sinh viên tính cách mặc định có phần nghiêm túc và chuẩn mực.
    Nhiệm vụ của bạn là giúp sinh viên trả lời các câu hỏi liên quan đến lịch học và lịch thi dựa trên dữ liệu bạn có.
    Có thể thay đổi cách xưng hô cho phù hợp với từng ngữ cảnh.
    Có thể thay đoiên ngôn ngữ teen code nhẹ nhàng, dùng icon vui vẻ khi trả lời.
    
    Bây giờ là: {current_time}.
    
    Dưới đây là dữ liệu lịch học và lịch thi của sinh viên (dạng JSON):

    Thông tin lịch học {schedule_data_str}
    Thông tin lịch thi {exam_data_str}
    
    Người dùng hỏi: "{user_question}"
    
    Yêu cầu trả lời:
    1. Trả lời chính xác dựa trên dữ liệu JSON trên.
    2. Nếu không có lịch trong dữ liệu thì nói rõ.
    3. Dùng ngôn ngữ teen code nhẹ nhàng, dùng icon vui vẻ.
    4. KHÔNG hiển thị dữ liệu thô (JSON).
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ LỖI CHI TIẾT GEMINI: {str(e)}")
        return "Ui chà, não bộ AI đang bị quá tải xíu. Hỏi lại sau nha! 😵‍💫"
    

def analyze_user_intent(user_text, schedule_data, exam_data):
    """
    Hàm 2 trong 1: Vừa trả lời câu hỏi, vừa phát hiện đặt lịch.
    Output: Dictionary chứa action, time, và câu trả lời.
    """
    current_time = datetime.now().strftime("%H:%M ngày %d/%m/%Y")
    
    # Chuyển data sang string
    schedule_str = json.dumps(schedule_data, ensure_ascii=False, default=str)
    exam_str = json.dumps(exam_data, ensure_ascii=False, default=str)

    prompt = f"""
    Bạn là trợ lý ảo VHU. Hiện tại là: {current_time}.
    
    Dữ liệu lịch: {schedule_str}
    Dữ liệu thi: {exam_str}
    
    User chat: "{user_text}"
    
    Nhiệm vụ: Phân tích ý định của user và trả về JSON duy nhất (không markdown).
    
    Trường hợp 1: User muốn đặt lịch nhắc nhở/báo thức/hẹn giờ hàng ngày.
    - action: "set_reminder"
    - time: {{"h": <giờ 24h>, "m": <phút>}} (Ví dụ "9h tối" -> h:21, m:0)
    - response: Câu xác nhận vui vẻ (Ví dụ: "Okela, đã chốt đơn lúc 21:00 nha").

    Trường hợp 2: User hỏi lịch học/thi hoặc giao tiếp bình thường.
    - action: "chat"
    - time: null
    - response: Câu trả lời dựa trên dữ liệu lịch (ngắn gọn, teen code).
    - Chỉ trả lời dựa trên dữ liệu lịch học/thi đã cho.
    - Nếu không có lịch thì nói rõ "2 ngày tới không có lịch học/thi nha!".
    - Chỉ hiển thị lịch thi từ hôm nay trở đi.

    Trường hợp 3: User muốn hủy/tắt báo thức.
    - action: "cancel_reminder"
    - time: null
    - response: Câu xác nhận hủy.

    Mẫu JSON output bắt buộc:
    {{
        "action": "set_reminder" | "chat" | "cancel_reminder",
        "time": {{"h": 21, "m": 30}} hoặc null,
        "response": "Nội dung trả lời user"
    }}
    """
    
    try:
        res = model.generate_content(prompt)
        text = res.text.strip().replace('```json', '').replace('```', '')
        return json.loads(text)
    except Exception as e:
        print(f"Lỗi AI: {e}")
        # Fallback an toàn nếu AI lỗi
        return {
            "action": "chat",
            "time": None,
            "response": "Bot đang lú cái đầu, bạn hỏi lại câu khác đi! 😵‍💫"
        }