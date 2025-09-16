from flask import Flask, request
import requests
import pandas as pd
import os

app = Flask(__name__)

# Load FAQ từ file Excel
faq_df = pd.read_excel("faq.xlsx")

# Token từ Facebook Developer (config trong Render)
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "my_secret_token")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")

@app.route("/", methods=["GET"])
def home():
    return "Chatbot Messenger đang chạy!"

# Webhook để Facebook gọi
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Verify token khi Facebook setup webhook
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Sai verify token", 403
    
    elif request.method == "POST":
        data = request.get_json()
        if "entry" in data:
            for entry in data["entry"]:
                if "messaging" in entry:
                    for message_event in entry["messaging"]:
                        if "message" in message_event:
                            sender_id = message_event["sender"]["id"]
                            message_text = message_event["message"].get("text", "")
                            reply = get_answer(message_text)
                            send_message(sender_id, reply)
        return "ok", 200

# Hàm tìm câu trả lời từ FAQ
def get_answer(user_message):
    for i, row in faq_df.iterrows():
        if row["keyword"].lower() in user_message.lower():
            return row["answer"]
    return "Xin lỗi, mình chưa có câu trả lời cho câu hỏi này."

# Hàm gửi tin nhắn lại Messenger
def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post(url, headers=headers, json=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
