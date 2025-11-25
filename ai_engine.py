import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
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
