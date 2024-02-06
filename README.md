# Passive Job Application System.  
Because when you come back from work the last thing you want to do is apply for work   

# Features
Applies to jobs found from provided job hosting site URL.  not implemented
Designed to be run tabbed out or on another monitor.  
Can use ChatGPT to write cover letters and answer more complicated questions ex. (Why do you want to work here?)  

# Start Up
1. Run Startup.exe and fill in requested information
[//]: (#2. You must provide job titles for the program to find)
[//]: (#3. Get a link for Glassdoor like https://www.glassdoor.com/Job/software-engineering-jobs-SRCH_KO0,20.html)
[//]: (#4. Run Auto App.exe with given link)
[//]: (#5. Wait 10 seconds then minimize let the code work)

   
# Notes
I recommend making a dedicated Gmail account, Google Voice, and LinkedIn profile for this program

Wait until the systems has logged in before you tab out

# Job App Process
1. Access job hosting site and login
2. Check job posting to see if it matches keywords
3. If so, click apply link and attempt to fill out application form
4. Attempt to answer each question using response.json
5. If we do not have a response and ChatGPT enabled ask ChatGPT else use default response
6. If an error is encountered switch tabs back to job host site leave page for user to fill out later

# ChatGPT Process
1. Login into ChatGPT using front end not API
2. Give ChatGPT your previous work experience taken from your resume and a brief description of user
3. Give ChatGPT job description ask to parse into about the company, requirements and duties
4. Give ChatGPT the question to be answered or just ask for a cover letter
5. Send response back to job application form

[//]: # # Job Listing Site
[//]: # 1. LinkedIn
[//]: # 2. Glassdoor
[//]: # 3. Indeed

# Application Templates
1. LinkedIn Easy Apply
2. Indeed Easy Apply
3. Paylocity
4. Greenhouse
5. Jobvite
6. Lever
7. Jobjuncture
8. BambooHR
9. ICIMS*
10. Workday*
11. Ashby
12. SmartRecuiters*

*glitchy

# compiled with psgcompiler
python scripts provided in source code folder compile with psgcompiler

# issues
glassdoor not loading new page
