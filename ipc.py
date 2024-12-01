import requests
from bs4 import BeautifulSoup
import sys
from ipaddress import ip_network
import time

def fetch_rapiddns_hosts(ip, output_file):
    page = 1
    max_pages = 3  # Set the maximum page limit
    
    while page <= max_pages:
        time.sleep(3)  # Introduce a delay before each request
        url = f"https://rapiddns.io/s/{ip}?page={page}&full=1"
        print(f"Fetching URL: {url}")
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Error fetching data for IP: {ip}. Status code: {response.status_code}")
            break
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')  # Look for the table in the page
        
        if not table:
            print(f"No table found on the page for IP {ip}, page {page}")
            break
        
        rows = table.find_all('tr')
        
        if len(rows) <= 1:
            # No more rows with data; only the header row exists
            break
        
        hosts_found = 0  # Counter for hostnames on this page
        
        for row in rows[1:]:  # Skip the header row
            cols = row.find_all('td')
            if len(cols) > 1:
                host = cols[0].get_text(strip=True)
                if host:
                    # Write host to the output file immediately
                    output_file.write(host + "\n")
                    print(f"Found host: {host}")
                    hosts_found += 1
        
        # If fewer than 100 hosts were found, stop fetching
        if hosts_found < 100:
            print(f"Fewer than 100 hosts found on page {page}. Stopping.")
            break
        
        page += 1

def main():
    ip_or_file = input("Enter IP or IP range in CIDR format or filename with IPs: ").strip()
    output_filename = input("Enter output file name: ").strip()
    
    # Check if input is a file or a single IP/CIDR range
    try:
        # Try to open as file
        with open(ip_or_file, 'r') as file:
            ips = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        # Handle as a single IP or CIDR range
        try:
            ips = [str(ip) for ip in ip_network(ip_or_file)]
        except ValueError:
            print("Invalid IP or CIDR range.")
            sys.exit(1)
    
    # Open the output file once and write results as they are fetched
    with open(output_filename, 'w', buffering=1) as output_file:
        for ip in ips:
            print(f"Fetching hosts for IP: {ip}")
            fetch_rapiddns_hosts(ip, output_file)
    
    print(f"Hosts saved to {output_filename}")

if __name__ == "__main__":
    main()

