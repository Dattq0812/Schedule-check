import crawler_Schedule as craw
import crawler_Exam as exam
import utils
import bot_personality
from dotenv import load_dotenv
import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram.ext import CallbackQueryHandler, MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import ai_engine
import cache_manager
# Load token từ .env
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") 


# Cấu hình logging để xem lỗi nếu có
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
# # --- 1. LỆNH /start ---
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text="👋 Chào bạn! Tôi là trợ lý sinh viên.\n\n"
#              "Gõ lệnh dưới đây để tra cứu:\n"
#              "📅 /lichhoc - Xem lịch học 2 ngày tới\n"
#              "🏆 /lichthi - Xem lịch thi sắp tới"
#     )

# --- 2. LỆNH /lichhoc ---
async def lich_hoc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    # 1. Báo cho user biết là đang xử lý (vì crawl hơi lâu)
    await context.bot.send_message(chat_id=chat_id, text=bot_personality.get_loading_text())

    try:
        # 2. Gọi hàm crawl dữ liệu (Code cũ của bạn)
        # Lưu ý: Hàm này phải return list data, không được print
        raw_data = craw.get_schedule() 
        
        if raw_data:
            # 3. Format tin nhắn (Code utils của bạn)
            message = utils.format_upcoming_schedule(raw_data)
            await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
        else:
            await context.bot.send_message(chat_id=chat_id, text="❌ Không lấy được dữ liệu (Lỗi Login hoặc Server trường).")
            
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"🔥 Có lỗi xảy ra: {str(e)}")

# --- 3. LỆNH /lichthi ---
async def lich_thi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text=bot_personality.get_loading_text())

    try:
        # Gọi hàm lấy lịch thi
        exam_data = exam.get_exam()
        
        if exam_data:
            msg = utils.format_exam_schedule(exam_data)
            await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')
        else:
            await context.bot.send_message(chat_id=chat_id, text="❌ Không lấy được lịch thi.")
            
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"🔥 Lỗi: {str(e)}")

# Hàm hiển thị Menu chính
async def send_main_menu(update, context):
    keyboard = [
        [
            InlineKeyboardButton("📅 Lịch học 2 ngày tới", callback_data='btn_lichhoc'),
            InlineKeyboardButton("🏆 Lịch thi sắp tới", callback_data='btn_lichthi')
        ],
        [
            InlineKeyboardButton("🌐 Vào Portal trường", url='https://portal.vhu.edu.vn')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Text chào hỏi
    welcome_text = bot_personality.get_random_greeting() + "\n\n" + \
                   "Chọn một trong các tùy chọn bên dưới để bắt đầu:"
    # Kiểm tra xem là lệnh chat hay bấm nút để dùng method phù hợp
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    elif update.callback_query:
        # Nếu đang ở menu cũ thì sửa lại thành menu mới (tránh spam tin nhắn)
        await update.callback_query.message.edit_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

# Hàm xử lý khi bấm nút
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # Báo cho Telegram biết đã nhận nút bấm (để tắt vòng xoay loading)
    
    # Kiểm tra nút nào được bấm
    if query.data == 'btn_lichhoc':
        # Gọi lại logic lấy lịch học (Tái sử dụng code cũ)
        await lich_hoc(update, context) 
        
    elif query.data == 'btn_lichthi':
        # Gọi lại logic lấy lịch thi
        await lich_thi(update, context)

# --- XỬ LÝ TIN NHẮN VĂN BẢN THÔNG THƯỜNG ---

async def handle_text_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    chat_id = update.effective_chat.id
    
    schedule_list, exam_list = cache_manager.get_from_cache()
    # Logic:
    # 1. Nếu user chào hỏi bình thường -> AI trả lời xã giao.
    # 2. Nếu user hỏi về lịch -> Bot tự động crawl ngầm -> Gửi cho AI phân tích.
    
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    if not schedule_list or not exam_list:
        print("🔄 Đang tiến hành lấy dữ liệu mới từ Portal...")
        # Gửi tin nhắn báo user đợi xíu nếu phải crawl
        temp_msg = await update.message.reply_text("⏳ Đợi tớ chạy lên trường xem bảng tin xíu nhé...")
        
        # Gọi hàm crawl (đảm bảo code crawler của bạn trả về list chuẩn)
        try:
            schedule_list = craw.get_schedule()
            exam_list = exam.get_exam()
            
            # Nếu crawl thành công thì Lưu ngay vào Cache
            if schedule_list and exam_list:
                cache_manager.save_to_cache(schedule_list, exam_list)
                # Xóa tin nhắn "Đợi xíu..." cho chuyên nghiệp
                await context.bot.delete_message(chat_id=chat_id, message_id=temp_msg.message_id)
            else:
                await update.message.reply_text("❌ Không lấy được dữ liệu từ trường. Thử lại sau nha.")
                return
                
        except Exception as e:
            print(f"Lỗi Crawl: {e}")
            await update.message.reply_text("❌ Lỗi hệ thống khi lấy dữ liệu.")
            return 
    # Hiện trạng thái "typing..."

    # Gửi cho Gemini xử lý
    ai_reply = ai_engine.ask_gemini_about_schedule(user_text, schedule_list, exam_list)
    
    await update.message.reply_text(ai_reply, parse_mode='Markdown')


# --- CHẠY BOT ---
if __name__ == '__main__':
    if not BOT_TOKEN:
        print("❌ Lỗi: Chưa có TELEGRAM_BOT_TOKEN trong file .env")
        exit()

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Đăng ký các lệnh
    #application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('start', send_main_menu)) # Thay hàm start cũ
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CommandHandler('lichhoc', lich_hoc))
    application.add_handler(CommandHandler('lichthi', lich_thi))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text_chat))
    print("🤖 Bot đang chạy... Nhấn Ctrl+C để dừng.")
    application.run_polling()


