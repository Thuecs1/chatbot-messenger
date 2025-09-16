from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Lấy token từ biến môi trường (Render -> Environment Variables)
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "EAARKuY5YAOsBPTEGYsAQjWG7yAvSbQZAkNw3AaZAVSLbvEZAAyGDQTSQocOzd9TZAZBTh3qUODQnRMbxzkQEO0zxEnZAQeq86fLJZArGDkljCz6N2qKcWBSjjMQdzM9ZBPZB6mMGDK6HKWrqafZAP0VU75QViF8y4RnQwj3IsoKHhQymRDwZA1rUELhP6hHT2WUzZBE9ZAvO68ZBsZD")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "my_secret_token")


@app.route("/", methods=['GET'])
def home():
    return "Chatbot is running!", 200


@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Xử lý xác minh webhook từ Facebook
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            return "Verification token mismatch", 403

    elif request.method == 'POST':
        # Nhận dữ liệu từ Messenger
        data = request.get_json()
        print(data)

        if data['object'] == 'page':
            for entry in data['entry']:
                for messaging_event in entry['messaging']:
                    if 'message' in messaging_event:
                        sender_id = messaging_event['sender']['id']
                        message_text = messaging_event['message'].get('text', '')

                        if message_text:
                            reply(sender_id, f"Bạn vừa nói: {message_text}")

        return "EVENT_RECEIVED", 200


def reply(recipient_id, message_text):
    """Gửi tin nhắn trả lời về Messenger"""
    url = "https://graph.facebook.com/v17.0/me/messages"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
        "messaging_type": "RESPONSE"
    }
    params = {"access_token": PAGE_ACCESS_TOKEN}
    response = requests.post(url, headers=headers, params=params, json=payload)
    print("Message sent:", response.text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
