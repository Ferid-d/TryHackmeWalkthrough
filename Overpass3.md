# TryHackMe Overpass 3 hosting WriteUp
Machine IP = 10.82.158.10  

At first, I make a rust scan to find open ports:  

```bash  
rustscan -a 192.16.13.53
```  
Yeah, we defined that there are three ports:  
--> 21,22,80  
I searched the web-page and there were some usernames a hint on source code but nothing else. So I made a directory scanning by the help of **FFUF**.  
```bash
ffuf -u 'http://10.82.158.10/FUZZ' -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -ic
```
It found some directories but there is only one necessary file for us: ***backup***  
I contains a ".zip" file. I clicked on it and it automatically installed to my device. Let's look what is inside it.  
```bash
unzip backup.zip  
|CustomerDetails.xlsx.gpg  
|priv.key  
gpg --import priv.key  
gpg --decrypt CustomerDetails.xlsx.gpg > CustomerDetails.xlsx  
```  
I opened this ".xlsx" file on browser by the help of online excel. It gave me three users and their credentials like username and password. As you can remember, we have an open ftp port. I tried to access with these user's name and password. Only the user "paradox" became successful for ftp connection.  

----  
i decided

