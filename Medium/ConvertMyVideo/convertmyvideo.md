# ConvertMyVideo TryHackMe WriteUp
## Machine IP = 10.112.149.155

----
First of all, let's made a port scan:
```bash
rustscan -a 10.112.149.155
```
Two ports are open:
-- *22* ssh
-- *80* http

----
### Discover web-site  
<img width="1594" height="698" alt="image" src="https://github.com/user-attachments/assets/b94b459f-08d5-46c6-aabb-931a2023cb0e" />  
There is a input form which requires ID to convert it into mp3 file. Let's look at the source code. I wanted to meaning of the JavaScript codes that are used in this web-site to understant every thing better. 
The script identifies exactly where the data is going and what format it expects:  

    Target URL: / (The root of the web server).

    Method: POST.

    Parameter: yt_url.

    Input logic: It takes whatever you put in #ytid and prepends https://www.youtube.com/watch?v=.  

----
I decided to check it on burpsuite:  
When I wrote "hello" in that form it looked like this.  
 
