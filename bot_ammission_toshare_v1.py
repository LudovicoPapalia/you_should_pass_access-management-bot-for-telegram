# WORKING this bot handles access requests and, if there are any requests, writes the message to the admin group
# This bot should be an admin and able to read all messages to work (enable it in botfather)

import requests
import json
import re
import time

TOKEN = '12345fjernv:eofn0000fakebottoken0000rjvnjerfre4098t4r'  # Replace with your actual bot token
GROUP_A_ID = '123456789'  # Insert here your group A id - remember that usually the id starts with a "-". This is the id of your MAIN group you can find it using @chatIDrobot
GROUP_B_ID = '987654321'  # Insert here your group B id - remember that usually the id starts with a "-". This is the id of your ADMIN group you can find it using @chatIDrobot
API_URL = f"https://api.telegram.org/bot{TOKEN}/"

# Mapping between message_id of messages forwarded to the admin group and user_id of the users
forwarded_messages = {}

def send_message(chat_id, text):
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    response = requests.post(f"{API_URL}sendMessage", json=payload)
    response_data = response.json()  # Convert the response to JSON
    print(response_data)  # Print for debugging
    return response_data  # Return the response data

def forward_message_to_admin(from_user_id, text):
    forward_text = f"Message from {from_user_id}: {text}"
    response_data = send_message(GROUP_B_ID, forward_text)
    if response_data and 'result' in response_data:
        admin_message_id = response_data['result']['message_id']
        forwarded_messages[admin_message_id] = from_user_id  # Save the association

def handle_updates():
    last_update_id = None
    while True:
        response = requests.get(f"{API_URL}getUpdates?offset={last_update_id}&timeout=100")
        if response.status_code == 200:
            updates = response.json()
            for update in updates.get("result", []):
                last_update_id = update["update_id"] + 1

                if "chat_join_request" in update:
                    chat_join_request = update["chat_join_request"]
                    chat_id = chat_join_request["chat"]["id"]
                    user_id = chat_join_request["from"]["id"]

                    if str(chat_id) == GROUP_A_ID:
                        send_message(user_id, "Your join request is under review.")
                        send_message(GROUP_B_ID, f"New join request from user ID {user_id}.")

                elif "message" in update:
                    message = update["message"]
                    chat_id = str(message["chat"]["id"])
                    from_user_id = str(message["from"]["id"])
                    text = message.get("text", "")

                    if chat_id != GROUP_A_ID and chat_id != GROUP_B_ID:
                        forward_message_to_admin(from_user_id, text)
                    elif chat_id == GROUP_B_ID and "reply_to_message" in message:
                        reply_to_message_id = message["reply_to_message"]["message_id"]
                        if reply_to_message_id in forwarded_messages:
                            original_user_id = forwarded_messages[reply_to_message_id]
                            send_message(original_user_id, text)  # Send the reply to the original user
                        else:
                            send_message(GROUP_B_ID, "Unable to send reply: the original user is not tracked.")

        time.sleep(1)

if __name__ == "__main__":
    handle_updates()
