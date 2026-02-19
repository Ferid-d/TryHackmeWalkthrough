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
<img width="891" height="909" alt="Screenshot From 2026-02-19 19-49-21" src="https://github.com/user-attachments/assets/f030b593-086f-45be-9ffd-93827d36420d" />  
|  
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










