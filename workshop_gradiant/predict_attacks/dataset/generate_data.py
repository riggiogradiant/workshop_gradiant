import csv
import random
import datetime
import sys

# List of simulated IP addresses
ips = [
    "192.168.1.1", "10.0.0.2", "172.16.5.3", "203.0.113.4", "8.8.8.8",
    "192.168.100.10", "10.10.10.10", "172.20.30.40", "198.51.100.5", "192.0.2.6"
]

# Dictionary of protocols and their corresponding attacks
attacks_per_protocol = {
    "TCP": ["DDoS", "Brute Force", "Port Scanning"],
    "UDP": ["DDoS", "Malware"],
    "ICMP": ["DDoS", "Ping Flood"],
    "HTTP": ["SQL Injection", "Cross-Site Scripting"],
    "HTTPS": ["Man-in-the-Middle", "Zero-Day"],
    "FTP": ["Brute Force", "Malware"],
    "SSH": ["Brute Force", "Unauthorized Access"],
    "DNS": ["DNS Spoofing", "DNS Amplification"]
}

# Range of interactions per attack type
interactions_range = {
    "DDoS": (100, 500),
    "Brute Force": (50, 300),
    "Port Scanning": (10, 100),
    "Malware": (30, 200),
    "Ping Flood": (80, 400),
    "SQL Injection": (20, 150),
    "Cross-Site Scripting": (10, 120),
    "Man-in-the-Middle": (40, 250),
    "Zero-Day": (5, 50),
    "Unauthorized Access": (25, 180),
    "DNS Spoofing": (15, 100),
    "DNS Amplification": (90, 450)
}

# Ports associated with each protocol
ports_per_protocol = {
    "TCP": [80, 443, 22, 25, 21],
    "UDP": [53, 67, 68, 123],
    "ICMP": [0],
    "HTTP": [80],
    "HTTPS": [443],
    "FTP": [21],
    "SSH": [22],
    "DNS": [53]
}

# Attack severity levels associated with attack types
severity_per_attack = {
    "DDoS": "Critical",
    "Brute Force": "High",
    "Port Scanning": "Medium",
    "Malware": "High",
    "Ping Flood": "Medium",
    "SQL Injection": "High",
    "Cross-Site Scripting": "Medium",
    "Man-in-the-Middle": "Critical",
    "Zero-Day": "Critical",
    "Unauthorized Access": "High",
    "DNS Spoofing": "Medium",
    "DNS Amplification": "High"
}

# Detection systems associated with attack types
detection_per_attack = {
    "DDoS": "IPS",
    "Brute Force": "Firewall",
    "Port Scanning": "IDS",
    "Malware": "Antivirus",
    "Ping Flood": "IPS",
    "SQL Injection": "SIEM",
    "Cross-Site Scripting": "SIEM",
    "Man-in-the-Middle": "Firewall",
    "Zero-Day": "SIEM",
    "Unauthorized Access": "Firewall",
    "DNS Spoofing": "IDS",
    "DNS Amplification": "IPS"
}

# Response time and packet size adjustments based on attack type
response_time_adjustments = {
    "DDoS": (500, 2000),
    "Brute Force": (10, 100),
    "Port Scanning": (20, 150),
    "Malware": (50, 400),
    "Ping Flood": (100, 800),
    "SQL Injection": (50, 300),
    "Cross-Site Scripting": (20, 200),
    "Man-in-the-Middle": (200, 1000),
    "Zero-Day": (100, 800),
    "Unauthorized Access": (30, 250),
    "DNS Spoofing": (30, 200),
    "DNS Amplification": (300, 1500)
}

packet_size_adjustments = {
    "DDoS": (1200, 1500),
    "Brute Force": (200, 500),
    "Port Scanning": (200, 700),
    "Malware": (500, 1200),
    "Ping Flood": (1000, 1500),
    "SQL Injection": (300, 1000),
    "Cross-Site Scripting": (200, 600),
    "Man-in-the-Middle": (500, 1500),
    "Zero-Day": (400, 1200),
    "Unauthorized Access": (200, 700),
    "DNS Spoofing": (200, 600),
    "DNS Amplification": (1000, 1500)
}

# Possible countries of origin
origin_countries = ["USA", "China", "Russia", "Germany", "India", "Brazil", "UK", "France", "Canada", "Japan"]

# Get the number of records from the command line
num_records = 100  # Default value
if len(sys.argv) > 1:
    try:
        num_records = int(sys.argv[1])
    except ValueError:
        print("Error: Argument must be an integer.")
        sys.exit(1)

# Output file name
output_file = "attacks.csv"

# Generate data and write to CSV file
with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["IP", "Protocol", "Attack Type", "DateTime", "Interactions", "Port", "Severity", "Response Time", "Packet Size", "Origin Country", "Detected By"])
    
    for _ in range(num_records):  # Generate specified number of records
        ip = random.choice(ips)
        protocol = random.choice(list(attacks_per_protocol.keys()))
        attack = random.choice(attacks_per_protocol[protocol])
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        interactions = random.randint(*interactions_range[attack])  # Specific range per attack type
        port = random.choice(ports_per_protocol[protocol])  # Specific port per protocol
        severity = severity_per_attack[attack]
        
        # Adjust response time and packet size based on attack type
        response_time = random.randint(*response_time_adjustments[attack])
        packet_size = random.randint(*packet_size_adjustments[attack])
        
        origin_country = random.choice(origin_countries)
        detected_by = detection_per_attack[attack]
        
        writer.writerow([ip, protocol, attack, date_time, interactions, port, severity, response_time, packet_size, origin_country, detected_by])

print(f"File '{output_file}' successfully generated with {num_records} records.")
