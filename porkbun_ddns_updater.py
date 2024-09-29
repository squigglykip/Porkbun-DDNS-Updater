import requests
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# API details
api_key = "pk1_7e56b78f832a77d905da75e09e22487c9cfb5fe026cdb4c84900cc5e14449a3f"
secret_key = "sk1_230eba20f12cb654eff73f2b15199d494a2ce5a74ff5a0613fc1f8b29e707952"

# Domain and DNS settings
domain = "urmeetingcost.lol"
dns_type = "A"
ttl = 600  # Time to live (600 seconds = 10 minutes)

# Email configuration
SMTP_SERVER = "smtp.gmail.com"  # Change this to your SMTP server
SMTP_PORT = 587  # Change if your SMTP server uses a different port
SMTP_USERNAME = "kipjordan@gmail.com"
SMTP_PASSWORD = "Kv0the!@#"  # Use an app password for Gmail
RECIPIENT_EMAIL = "hello@kipjordan.com"

# Function to get the current public IP address
def get_public_ip():
    return requests.get("https://ifconfig.me").text.strip()

# Function to retrieve current DNS records
def get_current_dns_records():
    url = f"https://api.porkbun.com/api/json/v3/dns/retrieve/{domain}"
    data = {
        "apikey": api_key,
        "secretapikey": secret_key
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        if result["status"] == "SUCCESS":
            return result["records"]    
        else:
            print(f"Failed to retrieve DNS records: {result.get('message', 'Unknown error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while retrieving DNS records: {str(e)}")
        return None
    except json.JSONDecodeError:
        print("Failed to decode JSON response from API when retrieving DNS records.")
        return None

# Function to update the DNS record on Porkbun
def update_dns_record(record_name, ip, current_content):
    if ip == current_content:
        print(f"DNS record for {record_name or '@'} is already up to date.")
        return {"status": "SUCCESS", "message": "No update needed"}

    url = f"https://api.porkbun.com/api/json/v3/dns/editByNameType/{domain}/A/{record_name}"
    data = {
        "secretapikey": secret_key,
        "apikey": api_key,
        "content": ip,
        "ttl": ttl
    }

    print(f"Sending request to URL: {url}")
    print(f"Request data: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        print(f"API Response: {json.dumps(result, indent=2)}")
        
        if result["status"] != "SUCCESS":
            error_message = f"Failed to update DNS record for {record_name or '@'}: {result.get('message', 'Unknown error')}"
            print(error_message)
            send_error_email("DNS Update Error", error_message)
        return result
    except requests.exceptions.RequestException as e:
        error_message = f"Error occurred while updating DNS record for {record_name or '@'}: {str(e)}"
        print(error_message)
        send_error_email("DNS Update Error", error_message)
        return {"status": "ERROR", "message": str(e)}
    except json.JSONDecodeError:
        error_message = f"Failed to decode JSON response from API for {record_name or '@'}."
        print(error_message)
        send_error_email("DNS Update Error", error_message)
        return {"status": "ERROR", "message": "Failed to decode JSON response from API."}

# Function to send error email
def send_error_email(subject, message):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    
    msg.attach(MIMEText(message, 'plain'))
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        print("Error email sent successfully")
    except Exception as e:
        print(f"Failed to send error email: {str(e)}")

# Main script
if __name__ == "__main__":
    try:
        current_ip = get_public_ip()
        print(f"Current public IP: {current_ip}")

        print("Current DNS records:")
        current_records = get_current_dns_records()
        if current_records:
            a_records = [record for record in current_records if record["type"] == "A"]
            for record in a_records:
                print(f"Host: {record['name']}, Content: {record['content']}, Type: {record['type']}")
            
            updates_needed = False
            for record in a_records:
                if record['name'] == domain:
                    record_name = ''  # Root domain
                elif record['name'].endswith('.' + domain):
                    record_name = record['name'][:-len('.' + domain)]
                else:
                    record_name = record['name']

                if record['content'] != current_ip:
                    updates_needed = True
                    print(f"\nUpdating DNS record for {record['name']}...")
                    result = update_dns_record(record_name, current_ip, record['content'])
                    if result.get("status") != "SUCCESS":
                        print(f"Error updating {record['name']}: {result.get('message', 'Unknown error')}")
                    time.sleep(5)  # Wait for 5 seconds between updates
                else:
                    print(f"\nDNS record for {record['name']} is already up to date.")

            if updates_needed:
                print("\nUpdated DNS records:")
                updated_records = get_current_dns_records()
                if updated_records:
                    for record in updated_records:
                        if record["type"] == "A":
                            print(f"Host: {record['name']}, Content: {record['content']}, Type: {record['type']}")
                else:
                    print("Failed to retrieve updated DNS records.")
            else:
                print("\nAll DNS records are already up to date.")
        else:
            error_message = "Failed to retrieve current DNS records."
            print(error_message)
            send_error_email("DNS Update Error", error_message)
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        print(error_message)
        send_error_email("DNS Update Script Error", error_message)
