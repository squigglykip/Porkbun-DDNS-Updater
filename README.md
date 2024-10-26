# porkbun_ddns

## Overview

`porkbun_ddns` is a dynamic DNS updater that automatically updates the DNS records for specified domains using the Porkbun API. It checks your current public IP address and updates the DNS records if there are any changes.

## Setup Instructions

### Prerequisites

- Python 3.x
- Pip (Python package manager)
- Porkbun account with API access

### Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/porkbun_ddns.git
   cd porkbun_ddns
   ```

2. **Install Required Packages:**

   Use pip to install the necessary Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables:**

   Create a `.env` file in the `porkbun_ddns` directory with the following content:

   ```plaintext
   # API details
   API_KEY = "your_porkbun_api_key"
   SECRET_KEY = "your_porkbun_secret_key"

   # Email configuration
   SMTP_SERVER = "your_smtp_server"
   SMTP_PORT = 587  # or your SMTP server's port
   SMTP_USERNAME = "your_email@example.com"
   SMTP_PASSWORD = "your_email_password"
   RECIPIENT_EMAIL = "recipient_email@example.com"
   ```

   Replace the placeholder values with your actual API keys and email configuration.

### Usage

1. **Configure Domains:**

   Edit the `main.py` file to specify the domains you want to update. Modify the `domains` list:

   ```python
   domains = ["yourdomain1.com", "yourdomain2.com"]
   ```

2. **Run the Script:**

   Execute the script to update the DNS records:

   ```bash
   python main.py
   ```

   The script will check your current public IP address and update the DNS records for the specified domains if necessary.

### Error Handling

If there are any errors during the DNS update process, an email will be sent to the `RECIPIENT_EMAIL` specified in the `.env` file.

## Code Structure

- `porkbun_ddns_updater.py`: Contains the `PorkbunDDNSUpdater` class responsible for interacting with the Porkbun API and sending emails.
- `main.py`: The main script that initializes the updater and processes the domains.
- `.env`: Stores environment variables for API and email configuration.

## License

This project is licensed under the MIT License.
