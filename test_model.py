import google.generativeai as genai

# Dán API Key của bạn vào đây
API_KEY = '#API KEY VO DAY'
genai.configure(api_key=API_KEY)

print("Đang kiểm tra danh sách model khả dụng trên API Key của bạn...\n")

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            # Cắt bỏ chữ 'models/' để lấy tên gốc cần dùng
            model_name = m.name.replace('models/', '')
            print(f"Tên model hợp lệ: {model_name}")
    print("\n=> Hãy copy một trong các tên trên để điền vào file bot.py")
except Exception as e:
    print(f"Lỗi kiểm tra: {e}")
