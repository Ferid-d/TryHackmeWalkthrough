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
Yeah, I get 4 subdomains: [api], [shop], [blog], [admin1].
