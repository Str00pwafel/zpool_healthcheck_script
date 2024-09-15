import re
import requests
import subprocess

from datetime import datetime

# Telegram bot token and chat ID
telegram_token = "5467355025:AAGwc7kbR7xD6Y4oOLlssvuGhoY4sDOE4qs"
chat_id = "5520672024"

# Shell command to check zpool status
command = ["/sbin/zpool", "status"]

# Define the regex pattern for the conditions you're interested in
pattern = r'(DEGRADED|FAULTED|OFFLINE|UNAVAIL|REMOVED|FAIL|DESTROYED|corrupt|cannot|unrecover)'

# Log file path
log_file_path = "/var/log/zpool_health_script.log"

# Get the current date and time for logging purposes
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Execute the command
result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


# Function to log the output to the log file
def log_to_file(message):
    # Open the file in append mode, which will create the file if it doesn't exist
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"{current_time} - {message}\n")


# Function to send a message via Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            log_to_file(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        log_to_file(f"Error sending Telegram message: {str(e)}")

# Check if the command was successful
if result.returncode == 0:
    # Search for the pattern in the command output
    condition = re.search(pattern, result.stdout, re.IGNORECASE)

    if condition:
        log_message = f"Warning: Condition matched - {condition.group()}"
        log_to_file(log_message)
        send_telegram_message(f"Zpool Alert: {log_message}")
    else:
        log_message = "No issues found in zpool status."
        log_to_file(log_message)
else:
    log_message = f"Error executing command:\n{result.stderr}"
    log_to_file(log_message)
    send_telegram_message(f"Zpool Error: {log_message}")
