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

















