# UltraTech TryHackMe WriteUp  
### Machine's IP = 10.112.149.213  
Start with rustscan:  
```bash
rustscan -a 10.112.149.213
```
| Open 10.112.149.213:21  
| Open 10.112.149.213:22  
| Open 10.112.149.213:8081  
| Open 10.112.149.213:31331  

Let's look at their services and versions:  
```bash
nmap -sV -sT -Pn -T4 -p21,8081,31331 10.112.149.213

PORT      STATE SERVICE VERSION
21/tcp    open  ftp     vsftpd 3.0.5
8081/tcp  open  http    Node.js Express framework
31331/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
Service Info: OS: Unix
```
First 4 questions' answers are ready from this reconniance.  

----
## Discoveying the web-site:  
Actually I checked both 8081 and 31331 ports on the website but got nothing special. There were some rabbit hole hints. Let's do directory enumeration for them:  
```bash
ffuf -u http://10.112.149.213:8081/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/big.txt - .php,.txt,.bak,.zip -fs 0
  - auth
  - ping
```
And,  

```bash
ffuf -u http://10.112.149.213:31331/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/big.txt - .php,.txt,.bak,.zip -fs 0
  - .htaccess
  - .htpasswd
  - css
  - favicon.ico
  - images
  - javascript
  - js
  - robots.txt
  - server-status
```

----
The answer of 5th question is "2" --> auth and ping. The software which is used at 8081 port is REST api. It has only routes that are used by web application. Theauth and ping routes are used for different purposes they arent normal directories.  
Lets check them:    
<img width="1131" height="174" alt="image" src="https://github.com/user-attachments/assets/e0faec31-a448-4740-9942-bd06b6125464" />    
Unfortunately we need credentials. Lets check ping route:    
<img width="1283" height="411" alt="image" src="https://github.com/user-attachments/assets/31d88a04-4f61-4e78-bae2-d316995ded01" />     

Here is the explanation in simple English, broken down just like before:  
1. Analyzing the Error: Cannot read property 'replace' of undefined  
This error means that on line 45 of the server's code (index.js), the program is trying to use a function called .replace().  
In programming, you use .replace() on a piece of text (a string) to change one part of it to something else. For example: text.replace("apple", "orange").  
The problem: The "text" variable the server is looking for is undefined (it doesn't exist or is empty). Because you didn't provide the input it was expecting, the code "broke" while trying to process nothing.  
  
2. Where is the input missing? (The Entry Point)  
The error log mentions app.get. This tells us the server is waiting for a GET request (a standard web URL request). Usually, the missing information is hidden in the URL in one of two ways:  

    URL Query: The parameter comes after a question mark.  

        Example: ?ping=8.8.8.8 or ?ip=127.0.0.1

    URL Path: The parameter is part of the link itself.   

        Example: /api/ping/8.8.8.8

We can check which parameter works on there by using, **"arjun"** tool.  
```bash
arjun -u http://10.112.149.213:8081/ping -m GET
```
Yeah we get the answer "ip". Let's check it:    
<img width="3091" height="363" alt="image" src="https://github.com/user-attachments/assets/033074f4-830a-455a-ab60-f1156da9e5e3" />    
I wanted to try the vulnerability which is called **" OS Command Injection. "** There are several ways of it but only **%0A** worked. It simply add new line and in this way when api sends request for ping command, it also executes out commands. I can explore so much in this way.     
<img width="1454" height="539" alt="image" src="https://github.com/user-attachments/assets/c5546e9e-008e-4243-864b-b471a740caf7" />    
<img width="1666" height="539" alt="image" src="https://github.com/user-attachments/assets/01e5760a-5738-4909-b60e-ff6e8e6bbf69" />    
BINGOOOOO!!! We got two user names and theis corresponding hash passwords. Lets decrypt them:  
| r00t = n100906  
| admin = mrsheafy  
Hmmm, I remembered that auth route needed authentication. So lets try it maybe we will find another important thing on there.  
```bash
http://10.112.149.213:8081/auth?login=admin&password=mrsheafy
``` 
<img width="1666" height="433" alt="image" src="https://github.com/user-attachments/assets/6af3c02f-f8c8-4cf3-a727-6701831c30df" />     
Hmm, there is another user which is called lp1 i think.   

----
I think we already checked the main things, I checked also the robots.txt file on 31331 port but got nothing so special from there. There was a login page which redirect us to the /auth page and we have already did it so, there is nothing we can do else. Let's became r00t user via ssh.    
We are in!!!    
First thing I did was sudo -l but it didn't worked so I checked id of this user. And THE GOLDMINEEE!!!!  
```bash
r00t@ip-10-112-149-213:~$ id
uid=1001(r00t) gid=1001(r00t) groups=1001(r00t),116(docker)
```
THe docker group will make us root easily. The first thing was to check docker image.    
<img width="873" height="106" alt="image" src="https://github.com/user-attachments/assets/2942620f-1ec5-40a8-9e33-f2799a65c604" />    
As we can see the Docker image is "bash". In GTFObins we can get this command:  
```bash
docker run -v /:/mnt --rm -it alpine chroot /mnt /bin/sh
```
We only need to change its image from "alpine" to "bash".   
```bash
docker run -v /:/mnt --rm -it bash chroot /mnt /bin/sh
```
WE ARE ROOT !!!! Next step is go to .ssh/id_rsa file and take first 9 strings from there for the last answer.   




Docker Image is a lightweight, standalone, and read-only "snapshot" or "blueprint" of an operating system or application. It contains all the necessary files, libraries, and system tools required to run a container.
In this specific scenario:  

    The Blueprint: Before launching a container, I needed a template to build it from. I ran docker images to identify which templates were already stored on the server's local disk.

    The Environment: I discovered a bash image. This image provides a minimal Linux environment with a functional terminal, which is exactly what I needed to execute system commands.

    The Bypass: Checking for local images is critical in restricted environments. Since I couldn't download new images (like alpine) from the internet, I had to use the existing bash image as the "vehicle" to mount the host's file system and escalate my privileges to root.

Docker is a platform that uses OS-level virtualization to deliver software in packages called containers. These containers are usually isolated from the host system.  
This user is in the docker group, so it can create its own container and interact directly with the Docker daemon. Since the Docker daemon runs with root privileges, any user in the docker group can execute commands as root through a container.   
By using this command, it can get the root files and mount them to its own container:  
Bash  
 
docker run -v /:/mnt -it bash chroot /mnt sh  

Technical Breakdown:  

    docker run: Starts a new container.

    -v /:/mnt: This is the Volume Mount. It maps the entire host file system (/) to a folder inside the container (/mnt).

    -it bash: Specifies the container should use the locally available bash image (verified earlier via docker images) and provides an interactive terminal.

    chroot /mnt sh: This "changes root" to the /mnt directory. Because the host's real root is mounted there, the container's shell session escapes its isolation and gains full root access to the host machine's files.






















