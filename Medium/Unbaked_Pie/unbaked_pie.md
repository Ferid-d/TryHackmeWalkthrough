# Unbaked Pie TryHackMe WriteUp
### Machine IP: 10.112.184.156

----
First of all, as usual I made a port scan:
```bash
rustscan -a 10.112.184.156
```
I saw that only the port (5003) is open. Let's look at the web-site. I saw "search", "login", "signup" pages and some posts.  
I also got three usernames, maybe they can be useful for us: [ramsey], [wan], [oliver]. I decided to do directory scan:
```bash
ffuf -u http://10.112.184.156:5003/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -mc 200,301,302
```
Actually, I didn't get any important info from there. I thought that there isn't anything I can try so lets explore the sign in page.  
When I write default credentials on there, like (admin:admin) I saw an error message:
|  
<img width="1929" height="418" alt="Screenshot From 2026-02-23 20-12-49" src="https://github.com/user-attachments/assets/64b0b2ea-09d8-4b21-8518-bd02ff160b1b" />
|  
Hmm, This is a significant Information Leakage vulnerability. The verbosity of the error confirms two things:

    Backend Technology: The syntax %(username)s is a classic Python string formatting style, confirming the backend is likely running Django or a similar Python framework.

    Username Enumeration: The system explicitly distinguishes between an "invalid login" and an "inactive account." This allows an attacker to brute-force usernames to identify which accounts actually exist on the system.  

----
### Information Gathering via Debug Mode
The detailed JSON error messages I received suggested that the application was running in Debug Mode. In a live environment, these technical details should be hidden to prevent leaking the app's internal logic.

To test this, I tried to access a non-existent page (like /random_123). Instead of a standard "Not Found" error, the server returned a 404 Debug Page. This page is a goldmine for an attacker because it reveals:

    File Paths: Exactly where the application files are stored on the server.

    URL Patterns: A complete list of all available pages and hidden API endpoints.

    System Info: The specific Python modules and versions being used.

    










