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
ffuf -u http://10.112.181.140/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt -fs 0,44 -t 250

/admin
/hide-folders
```
Let's check them.   
In "**/admin**" page, I saw an .apk file (app-release.apk	2019-12-10 08:06 	1.4M). Lets download it for future discovery.   
In **"/hide-folders"** there was two folder:
'''
|--hide-folders
  |--1
     | Method not allowed
  |--2
     |hola	2019-12-10 07:38 	8.6K
'''
