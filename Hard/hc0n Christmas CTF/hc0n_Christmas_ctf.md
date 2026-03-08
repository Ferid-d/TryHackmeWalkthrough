# hc0n Christmas CTF TryHackMe WriteUp
### Machine IP = 10.112.181.140
Start with port scan:
```bash
rustscan -a 10.112.181.140
```
Open Ports: 22, 80, 8080  
When I opened the web-site, I saw a login and register page in there. Lets discover the directories and meanwhile I checked the 8080 port on the url:  
<img width="1048" height="214" alt="image" src="https://github.com/user-attachments/assets/9a5a13af-1755-4a2d-857a-0b643491e846" />  
I tried to decrypt it on CyberChef but got noting as a result. So let's look founded directories.  
```bash
ffuf -u http://10.112.181.140/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt -e .php,.txt,.bak,.zip -fs 0,44 -t 250

/admin
/hide-folders
/robots.txt
```
Let's check them.   
In "**/admin**" page, I saw an .apk file (app-release.apk	2019-12-10 08:06 	1.4M). Lets download it for future discovery.   
In **"/hide-folders"** there was two folder:
```bash
|--hide-folders  
  |--1  
     | Method not allowed  
  |--2  
     |hola	2019-12-10 07:38 	8.6K  
```
Firstly, I decided to look at the request on burp-suite when I try to open folder number '1'. Because maybe if we change the method, we can get a hint or something important:    
<img width="801" height="306" alt="image" src="https://github.com/user-attachments/assets/477975c4-be68-4c81-850e-f27683f83826" />  
I changed the "GET" method to "OPTIONS" method and got the hint in response section:  
```bash
hax0r :3 you win firts part of the ssh password Gf7MRr55
```
Hmm, it means that the ssh password is divided into parts. We have already found the first part lets try to complete it.  

----
As you remember there was a file named **"hola"** in the folder number two. Lets open it on terminal.  
```bash
┌──(faridd㉿Ferid)-[~/Downloads/christmas]
└─$ strings hola
      
/lib64/ld-linux-x86-64.so.2
libc.so.6
__isoc99_scanf
puts
__stack_chk_fail
printf
strcmp
__libc_start_main
__gmon_start__
GLIBC_2.7
GLIBC_2.4
GLIBC_2.2.5
UH-X
AWAVA
AUATL
[]A\A]A^A_
Enter your username:
Enter your password:
stuxnet
n$@#PDuliL
Welcome, Login Success! this is a second part of ssh password 
Wrong password
```
Woww, we found another part of the password: n$@#PDuliL. I combined this two parts:  Gf7MRr55n$@#PDuliL. I tried them on the ssh connection for the "stuxnet" user, but it didn't work. Let's look at one of the most important folder "robots.txt" that I left for the end.   
<img width="1103" height="298" alt="image" src="https://github.com/user-attachments/assets/945fa055-e374-4332-b8ef-156a579a45bb" />   
administratorhc0nwithyhackme -- kept it in my mindt
famous group 3301 and secret IV is a hint. I searched about it and learned that "famous group 3301" is cicada 3301. It was one of the most popular cryptograpy puzzle. secret IV means "Initialization Vector". This is a block that is used to make the encryption process random in block cypher algorithm, for (example AES, DES). In this way, when we encrypt the same string multiple it will be different in each time. 

Okay, we learned that we should decrypt the string in the "iv.png" photo that was obtained from robots.txt file. Lets do it. I used this photo from reddit:
![cicada](https://github.com/user-attachments/assets/bb181c18-ebc1-44e7-ae7b-36c6a2cd2f71)  
























