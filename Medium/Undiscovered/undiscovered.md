# "Undiscovered" WriteUp
## The Machines Ip = 10.80.171.179
### Reconniance
At first, I made a port scan to see open ports:
```bash
rustscan -a 10.80.171.179
```
The open ports: 22,80,111,2049,34926. Then, I decided to look at their versions:
```bash
nmap -sCV -p22,80,111,2049,34926 10.80.171.179 -A
```
Let's look at the web site. But before it, we need to add undiscovered.thm domain into the /etc/hosts file. There was not anthing so, I decided to do a directory scan:
```bash
ffuf -u http://undiscovered.thm/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -fs 0
```
Even in there I cannot find anything important. The best choice is to do subdirectory scan.
```bash
ffuf -H "Host: FUZZ.undiscovered.thm" -u http://undiscovered.thm -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-110000.txt -mc 200
```
<img width="1436" height="556" alt="Screenshot From 2026-02-19 12-15-08" src="https://github.com/user-attachments/assets/b908ce44-4bd8-4b24-912e-ac4da9abcc24" />  

Yeah, as you can see we found several domains but it would take so much time to check all of them one-by-one. That's why I decided to keep only one among same sized subdomains. I used AI to eliminate repeated subdomains:  

<img width="399" height="491" alt="Screenshot From 2026-02-19 12-19-49" src="https://github.com/user-attachments/assets/d3afbb1c-160c-453a-8851-8443b9e11a99" />

----

I checked the first one "manager.undiscovered.thm". There was a version number "Powered by RiteCMS Version:2.2.1" I looked at it on searchsploit and saw that there are some vulnerabilities about it. Most of them requires us to be aunthenticated, so maybe there can be a login page.  
I also made a directory scan for this subdomain but there wasn't anything important else. So let's discover others. I specificly targeted the unique sized subdomains at first. Because in CTF's they gives us more important things than others. So, let's check "deliver.undiscovered.thm". It looks same so, I made directory scan again for this subdomain. Yeahh, we found so much directories in there.  
```bash
ffuf -u http://deliver.undiscovered.thm/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -fs 0
```

<img width="1249" height="418" alt="image" src="https://github.com/user-attachments/assets/d65bc269-f042-4ac8-9f0d-f4f98bb0d859" />  

The "http://deliver.undiscovered.thm/cms/" url shows us a login page.  

<img width="1241" height="528" alt="Screenshot From 2026-02-19 12-30-52" src="https://github.com/user-attachments/assets/528f06e9-a543-423c-b325-c4f0d5fcad3d" />

But we dont have credentials, so lets look at other folders like "data". After checking the files in there, I found a user "admin". So let's make a hydra bruteforce to get the password.

<img width="1146" height="578" alt="Screenshot From 2026-02-19 12-33-19" src="https://github.com/user-attachments/assets/ebadf64e-772b-41a0-86d7-be4f324c512c" />

----

After looking the POST request on burpsuite, I write a command like this:
```bash
hydra -l admin -P /usr/share/wordlists/rockyou.txt deliver.undiscovered.thm http-post-form "/cms/index.php:username=^USER^&userpw=^PASS^:F=login_failed" -t 64 -V
```
Yeah we got the password "liverpool" for "admin" user. Lets check them on the website. I looked for a section to upload files. Let's check "Administration" section on navbar. Then, I accessed file manager and saw a file upload form in there. It is as a gold for me because I can upload reverse shell php file on there.  

<img width="861" height="428" alt="Screenshot From 2026-02-19 12-41-48" src="https://github.com/user-attachments/assets/bae988d2-cd6f-4ff4-99b8-40e642642ebf" />  

Just click on the file-name and get a shell on terminal. I accessed as "www-data" user but I don't have permission to read user's files. I checked also SUID files but got nothing useful in there. Then, I remembered that we had open NFS port. But what is it?  
NFS is a protocol that allows files to be shared across a network as if they were stored on the local machine. It enables remote clients to mount directories from a server and interact with them based on the permissions defined in the /etc/exports file.  
So, as you understood, the first thing that we need to do is read the /etc/export file if there is open NFS port.  

<img width="1239" height="458" alt="Screenshot From 2026-02-19 12-51-28" src="https://github.com/user-attachments/assets/f0ad6fe2-8bf4-400e-a4fb-d02b23e5afb0" />

Yeah, the important part is located at the end of the result. Let's explain it one-by-one:
1. /home/william --> It means that the main folder of william user in the target machine was shared over the network and we can connect it from our own machine.
2. * (symbol) --> It means that everyone can mount this folder into their devices. There isn't any IP limitation.
3. (rw, root_squash) --> rw means that we can both read and write something on william's folders. But root_squash isn't so good for us. Because it prevent us to act as root on william files even if we are root on our device. So, It will make our work a little bit harder.
4. The weakest and most interesting part of NFS is that it doesn't look at your passwords or user name. It only look at UID(user_id). So, when you mount "/home/william" folder to your device, the target doesn't know who you are. It only checks that who want to change the files. If you create a user as named "william" with the same UID of it on the target, the system will think that you are the same user who it knows as william.

----

Lets check the william's ip:
```bash
www-data@undiscovered:/home$ id william
id william
uid=3003(william) gid=3003(william) groups=3003(william)
```
Let's run this command on our own terminal to mount william's files.
```bash
sudo userdel -r william
sudo useradd william -u 3003
sudo mkdir -p /mnt/william
sudo chown william:william /mnt/william
sudo mount -t nfs 10.80.171.179:/home/william /mnt/william
sudo su william
cd /mnt/william
ls -la
```
Yeah we got the **"USER FLAG"** from there. I want to work easier so, decided to create ssh key for this william user.
In my own terminal:
```bash
ssh-keygen -f william_ssh_key
```
It created two files "william_ssh_key" --> private, "william_ssh_key.pub" --> public. I copied the content of public key and add into the target user's aouthorized key files in the ssh folder because as you remember we had (rw) permission in there. Let's do it.  
```bash
william@Ferid:/mnt/william$ mkdir .ssh
william@Ferid:/mnt/william$ cd .ssh
william@Ferid:/mnt/william$ echo "THE_CONTENT_OF_PUBLIC_KEY_FILE" > authorized_keys
```
Then, I go back to my oown terminal and access this user's accound by ssh with private key:
```bash
ssh -i william_ssh_key william@10.80.171.179
```
----
We are in !!!!
<img width="1239" height="488" alt="Screenshot From 2026-02-19 13-30-01" src="https://github.com/user-attachments/assets/66f24284-4b9d-4391-adb5-61f84c4d0039" />
There is a suspicious file named "script" which is leonard's. I decided to read its content by this command:
```bash
strings script
```
I saw "/bin/cat" in there which means I can read some files by using this script. It has also suid permission which means I can run it as root. The first thing that I wanted to try was leonard's ssh key. In this way, if I could get it, I can be closer to be root.
<img width="906" height="826" alt="Screenshot From 2026-02-19 13-33-41" src="https://github.com/user-attachments/assets/6485236e-b5c9-4d88-adee-8e7c4810766c" />
Yeahhh we got it. Lets copy and use it to be leonard user. It worked !!!!. 

----
# Privilege Escalation
I looked at the SUID permission files and check the intersting ones on GTFObins. I didn't get anything from there. But there is another way:
```bash
getcap / -r 2>/dev/null
```
It is the best alternative of SUID file discovery. SUID permission means to give root permission to the program that can be used with root privileges by everyone even if they are normal user. But getcap check "Capabilities". In modern linux systems, they give special permissions to the program that they need instead of full root privileges. With getcap, we find this programs and if they are misconfigured, we can use it to be root.  
<img width="906" height="164" alt="Screenshot From 2026-02-19 13-43-19" src="https://github.com/user-attachments/assets/2248aeaf-6cfd-4d75-a04c-a39baa1a72ec" />
I checked them and found a payload for "vim.basic" which make us root.
```bash
/usr/bin/vim.basic -c ':py3 import os; os.setuid(0); os.execl("/bin/sh", "sh", "-c", "reset; exec /bin/sh")'
```
Bingoooo!! I am root right now. I need root's hash password for this CTF and can easily get it by reading /etc/shadow file.






