import json
import os
import time

# Tên file để lưu dữ liệu
CACHE_FILE = "student_data_cache.json"

# Thời gian hết hạn của Cache (Tính bằng giây)
# Ví dụ: 3600s = 1 tiếng. Nghĩa là sau 1 tiếng mới cần crawl lại.
CACHE_DURATION = 3600 * 12 # 12 tiếng 

def save_to_cache(schedule_data, exam_data):
    """Lưu dữ liệu mới vào file JSON"""
    data = {
        "timestamp": time.time(), # Lưu thời điểm crawl
        "schedule": schedule_data,
        "exam": exam_data
    }
    
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("✅ Đã lưu dữ liệu vào Cache thành công!")
    except Exception as e:
        print(f"❌ Lỗi khi lưu Cache: {e}")

def get_from_cache():
    """Đọc dữ liệu từ file JSON nếu còn hạn sử dụng"""
    if not os.path.exists(CACHE_FILE):
        print("⚠️ Chưa có file Cache.")
        return None, None

    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        saved_time = data.get("timestamp", 0)
        current_time = time.time()
        
        # Kiểm tra xem dữ liệu có quá cũ không
        age = current_time - saved_time
        if age > CACHE_DURATION:
            print(f"⚠️ Cache đã hết hạn (Cũ hơn {int(age/60)} phút).")
            return None, None # Trả về None để code chính biết mà đi crawl mới
            
        print(f"✅ Đã lấy dữ liệu từ Cache (Cũ {int(age/60)} phút).")
        return data.get("schedule"), data.get("exam")
        
    except Exception as e:
        print(f"❌ File Cache bị lỗi: {e}")
        return None, None