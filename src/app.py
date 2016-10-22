''' ### Acknowledgment
This webhook template is derived from
[here](https://github.com/hartleybrody/fb-messenger-bot/blob/master/app.py)
'''
import os
import sys
import json
import requests
from flask import Flask, request
import nltk
import time
import threading

from chat_bot.chat_bot import ChatBot

def create_flask_app():
    def sync_memory_and_recycle_inactive_chat_bots():
        '''
        Sync brain memory of local chat bots with remote and recycle inactive chat bots periodically
        '''
        global active_chat_bot_pool
        global lock
        while True:
            with lock:
                for sender_id, chat_bot_info in active_chat_bot_pool.items():
                    chat_bot = chat_bot_info[0]
                    last_active_time = chat_bot_info[1]
                    if time.time() - last_active_time > 300:
                        # Make sure memory sync succeed, as the chat bot will be recycled
                        while not chat_bot.sync_memory():
                            pass
                        send_message(sender_id, "I went to sleep as you have not been talking to me for a while.")
                        send_message(sender_id, "As always, you can talk to me to wake me up!")
                        del active_chat_bot_pool[sender_id]
                    else:
                        # Memory sync failure is acceptable, as an active chat bot syncs memory periodically
                        chat_bot.sync_memory()
            time.sleep(300)

    app = Flask(__name__)
    thread = threading.Thread(target=sync_memory_and_recycle_inactive_chat_bots, args=())
    thread.start()

    return app

nltk.download('punkt')
active_chat_bot_pool = {} # Dev only, use memcache instead for scalability
lock = threading.Lock()
app = create_flask_app()

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello world", 200

@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events
    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  # someone sent us a message
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    global active_chat_bot_pool
                    global lock
                    with lock:
                        if sender_id in active_chat_bot_pool:
                            chat_bot = active_chat_bot_pool[sender_id][0]
                        else:
                            chat_bot = ChatBot()
                        now = time.time()
                        active_chat_bot_pool[sender_id] = (chat_bot, now)
                    response = chat_bot.respond(message_text)
                    if isinstance(response, tuple):
                        for r in response:
                            send_message(sender_id, r)
                    else:
                        send_message(sender_id, response)
                if messaging_event.get("delivery"):  # delivery confirmation
                    pass
                if messaging_event.get("optin"):  # optin confirmation
                    pass
                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass
    return "ok", 200

def send_message(recipient_id, message_text):
    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
