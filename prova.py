import requests

# Define your bot token
TOKEN = "7039441013:AAFLoD1pmkhos_6vLobX7fzeebPd-jBBEd4"

# Define the base URL for the Telegram Bot API
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

def get_updates():
    url = BASE_URL + "getUpdates"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        updates = data.get("result")
        return updates
    else:
        print("Failed to fetch updates.")
        return None

def main():
    updates = get_updates()
    if updates:
        for update in updates:
            message = update.get("message")
            if message:
                print("New message:", message.get("text"))

if __name__ == "__main__":
    main()