import socket
import threading

# We use a Lock to prevent multiple threads from printing at the same time and mixing the output
print_lock = threading.Lock()

def check_port(ip, port):
    try:
        # Socket creation
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2) # Increased timeout slightly for SSH to respond

        # Connection
        s.connect((ip, port))

        # Reading the banner
        # Some fake ports close the connection immediately, so we keep recv inside try
        banner = s.recv(1024).decode(errors='ignore').strip()

        # Checking for real OpenSSH banner
        # Fake ports often just say "OpenSSH", 
        # but real SSH also shows the version number (e.g., SSH-2.0-OpenSSH_8.2...)
        if "OpenSSH" in banner:
            with print_lock:
                print(f"\n[+] FOUND! Port: {port}")
                print(f"Banner message: {banner}")

        s.close()
    except:
        pass

target_ip = "10.114.188.201"
print(f"Scan starting: {target_ip} (2500-4500)...")

threads = []
for p in range(2500, 4501):
    t = threading.Thread(target=check_port, args=(target_ip, p))
    t.start()
    threads.append(t)

# Wait for all threads to complete
for t in threads:
    t.join()

print("\nScan complete.")
