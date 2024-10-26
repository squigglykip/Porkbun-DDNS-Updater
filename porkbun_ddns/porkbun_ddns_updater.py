import requests
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

class PorkbunDDNSUpdater:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.secret_key = os.getenv("SECRET_KEY")
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.recipient_email = os.getenv("RECIPIENT_EMAIL")
        self.ttl = 600
        self.domains = os.getenv("DOMAINS").split(",")

    def get_public_ip(self):
        return requests.get("https://ifconfig.me").text.strip()

    def get_current_dns_records(self, domain):
        url = f"https://api.porkbun.com/api/json/v3/dns/retrieve/{domain}"
        data = {
            "apikey": self.api_key,
            "secretapikey": self.secret_key
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

    def update_dns_record(self, domain, record_name, ip, current_content):
        if ip == current_content:
            print(f"DNS record for {record_name or '@'} is already up to date.")
            return {"status": "SUCCESS", "message": "No update needed"}

        url = f"https://api.porkbun.com/api/json/v3/dns/editByNameType/{domain}/A/{record_name}"
        data = {
            "secretapikey": self.secret_key,
            "apikey": self.api_key,
            "content": ip,
            "ttl": self.ttl
        }

        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            if result["status"] != "SUCCESS":
                error_message = f"Failed to update DNS record for {record_name or '@'}: {result.get('message', 'Unknown error')}"
                print(error_message)
                self.send_error_email("DNS Update Error", error_message)
            return result
        except requests.exceptions.RequestException as e:
            error_message = f"Error occurred while updating DNS record for {record_name or '@'}: {str(e)}"
            print(error_message)
            self.send_error_email("DNS Update Error", error_message)
            return {"status": "ERROR", "message": str(e)}
        except json.JSONDecodeError:
            error_message = f"Failed to decode JSON response from API for {record_name or '@'}."
            print(error_message)
            self.send_error_email("DNS Update Error", error_message)
            return {"status": "ERROR", "message": "Failed to decode JSON response from API."}

    def send_error_email(self, subject, message):
        msg = MIMEMultipart()
        msg['From'] = self.smtp_username
        msg['To'] = self.recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            print("Error email sent successfully")
        except Exception as e:
            print(f"Failed to send error email: {str(e)}")

# List of domains
domains = ["urmeetingcost.lol", "anotherdomain.com", "yetanotherdomain.com"]

# Main script
if __name__ == "__main__":
    updater = PorkbunDDNSUpdater()
    try:
        current_ip = updater.get_public_ip()
        print(f"Current public IP: {current_ip}")

        for domain in domains:
            print(f"\nProcessing domain: {domain}")

            print("Current DNS records:")
            current_records = updater.get_current_dns_records(domain)
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
                        result = updater.update_dns_record(domain, record_name, current_ip, record['content'])
                        if result.get("status") != "SUCCESS":
                            print(f"Error updating {record['name']}: {result.get('message', 'Unknown error')}")
                        time.sleep(5)  # Wait for 5 seconds between updates
                    else:
                        print(f"\nDNS record for {record['name']} is already up to date.")

                if updates_needed:
                    print("\nUpdated DNS records:")
                    updated_records = updater.get_current_dns_records(domain)
                    if updated_records:
                        for record in updated_records:
                            if record["type"] == "A":
                                print(f"Host: {record['name']}, Content: {record['content']}, Type: {record['type']}")
                    else:
                        print("Failed to retrieve updated DNS records.")
                else:
                    print("\nAll DNS records are already up to date.")
            else:
                error_message = f"Failed to retrieve current DNS records for {domain}."
                print(error_message)
                updater.send_error_email("DNS Update Error", error_message)
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        print(error_message)
        updater.send_error_email("DNS Update Script Error", error_message)
