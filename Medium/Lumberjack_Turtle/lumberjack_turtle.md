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








