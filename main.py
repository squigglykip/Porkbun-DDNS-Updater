from porkbun_ddns.porkbun_ddns_updater import PorkbunDDNSUpdater

if __name__ == "__main__":
    updater = PorkbunDDNSUpdater()
    current_ip = updater.get_public_ip()
    print(f"Current public IP: {current_ip}")

    domains = updater.domains

    for domain in domains:
        print(f"\nProcessing domain: {domain}")
        current_records = updater.get_current_dns_records(domain)
        if current_records:
            a_records = [record for record in current_records if record["type"] == "A"]
            for record in a_records:
                if record['name'] == domain:
                    record_name = ''  # Root domain
                elif record['name'].endswith('.' + domain):
                    record_name = record['name'][:-len('.' + domain)]
                else:
                    record_name = record['name']

                if record['content'] != current_ip:
                    print(f"\nUpdating DNS record for {record['name']}...")
                    result = updater.update_dns_record(domain, record_name, current_ip, record['content'])
                    if result.get("status") != "SUCCESS":
                        print(f"Error updating {record['name']}: {result.get('message', 'Unknown error')}")
                    time.sleep(5)  # Wait for 5 seconds between updates
                else:
                    print(f"\nDNS record for {record['name']} is already up to date.")
        else:
            error_message = f"Failed to retrieve current DNS records for {domain}."
            print(error_message)
            updater.send_error_email("DNS Update Error", error_message)
