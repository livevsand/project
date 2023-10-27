# Passive Job Application System.  
Because when you come back from work the last thing you want to do is apply for work  
work in progress  

# Features
Applies to jobs found from provided job hosting site url.  
Desingned to be run tabed out or on other monitor.  
Can use chatgpt to write cover letters and answer more complicated questions ex. (Why do you want to work here?)  

# Start Up
1. Run GUI.exe and fill in requested information
2. Put your resume in user_info as Resume.pdf
3. you must provided job titles for the program to find
4. get a link for glassdoor like https://www.glassdoor.com/Job/software-engineering-jobs-SRCH_KO0,20.html
5. run main.exe with given link
6. wait 10 secounds then minimize let the code work

   
# Notes
Wait until the systems has logged in before you tab out
Chat Gpt disabled

# Job App Process
1. Access job hosting site and login
2. Check job posting to see if it matches keywords
3. If so click apply link and attempt to fill out apllication form
4. Attempt to answear each question using response.json
5. If we do not have a reponse and chatgpt enabled ask chat gpt else use defalut response
6. If an error is encoutered switch tabs back to job host site leave page for user to fill out later

# Chat gpt Process
1. Login to chat gpt useing front end not API
2. Give chat gpt your previous work experience taken from your resume and a brief description of user
3. Give chat gpt job description ask to parse into about the company, requirments and duties
4. Give chat gpt the question to be answered or just ask for a cover letter
5. Send reponse back to job application form

# Job Listing Site
1. LinkedIn
2. Glassdoor
3. Indeed

# Aplication Templates
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
python scripts provied in source code folder compile with psgcompiler

# issues
you will have to use command prompt to stop program

Has Chat GPT intergration for personalized responses and cover letter generation
