from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import time
import json
import undetected_chromedriver as uc
from datetime import date

URL = 'https://chat.openai.com/'
TASK = "Split the job description into Responsibilities, Requirements and other. Respond with ok."


def startup() -> None:
    '''
    start up and login
    '''
    global driver
    global resume
    global query
    global HEADER
    global FOOTER
    global NAME
    

    options = webdriver.ChromeOptions()
    options.headless = False

    with open('user_info\\query.json', 'r') as file:
        query = json.loads(file.read()) #this contains the prompts for the LLM to generate the cover letter modify at owen risk
    with open('user_info\\personal_info.json', 'r') as file:
        info = json.load(file) # your personal information must be filled in by user
    with open('user_info\\work history.json', 'r') as file:
        resume = json.loads(file.read()) #your work/project history must be filled in by user
    NAME = info['name']
    query['name'] = NAME
    resume['task'] = "Act as "+NAME+". Respond with ok."
    HEADER = info['name'] + '\n' + info['address'] + '\n' + info['location'] + ' ' + info['zip'] + '\n' + info['email'] + '\n' + info[
            'phone'] + '\n' + str(date.today().strftime('%b, %d')) + '\n\n'

    driver = uc.Chrome(options=options, version_main=119, enable_cdp_events=True)

    driver.set_window_size(1000, 1000)
    driver.get(URL)

    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//div[text() = 'Log in']"))).click()
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-provider = 'google']"))).click()
    time.sleep(.1)
    #use gmail account to login
    google_account_login(info['chatgpt password'], info['chatgpt email'], driver)
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Okay')]"))).click()
    except:
        pass


def ask_question(crystal_ball, message: str) -> str:
    '''
    wait for chat gpt to add a new response line and return the text
    '''
    text_ref = "//div[contains(@class,'markdown prose w-full break-words dark:prose-invert dark')]"

    crystal_ball.send_keys(message)
    time.sleep(.1)
    crystal_ball.send_keys(Keys.ENTER)
    count = len(driver.find_elements(By.XPATH, text_ref))
    text = ''
    while count >= len(driver.find_elements(By.XPATH, text_ref)) or text != driver.find_elements(By.XPATH, text_ref)[-1].text:
        if len(driver.find_elements(By.XPATH, text_ref)) > 0:
            text = driver.find_elements(By.XPATH, text_ref)[-1].text
        time.sleep(1)

    return driver.find_elements(By.XPATH, text_ref)[-1].text

def google_account_login(password,email,driver):
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//input[@type = 'email']"))).send_keys(email)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//span[text() = 'Next']"))).click()
    time.sleep(.1)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//input[@type = 'password']"))).send_keys(password)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//span[text() = 'Next']"))).click()
    time.sleep(1)
    
def format_coverletter(res: str, current_job) -> str:
    '''
    makes response from chat gpt look like a cover letter
    '''
    res = res.replace('\n', '\n\n')
    if "Dear" in res:
        res = res[res.index("Dear"):]
    if NAME in res:
        res = res[:res.index(NAME) + len(NAME)]
    while '[' in res:
        res = res[:res.index('[')] + res[res.index(']') + 1:]
    res = HEADER + 'Hiring Team \n' + current_job.company + '\n' + current_job.location + '\n\n' + res
    return res


def answer(question: str, current_job, as_file: bool) -> str:
    '''
    answers question using chat gpt referencing the description and the user's resume
    '''
    startup()

    time.sleep(.1)
    crystal_ball = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//textarea[@id = 'prompt-textarea']")))
    ask_question(crystal_ball, json.dumps(resume))
    job_processing = {'Task': TASK,
                      'Company': current_job.company,
                      'Title': current_job.title,
                      'Location': current_job.location,
                      'Description': current_job.description
                      }
    ask_question(crystal_ball, json.dumps(job_processing))

    res = format_coverletter(ask_question(crystal_ball, json.dumps(query)), current_job)
    
    driver.close()
    if as_file:
        with open("cover-letter "+current_job.company+".txt", "w") as file:
            file.write(res)
    return res


def write_coverletter(current_job) -> str:
    return answer("cover letter", current_job, True)

class JobInfo:
    def __init__(self, description: str, title: str, company: str, location: str):
        self.description = description
        self.title = title
        self.company = company
        self.location = location
        
if __name__ == "__main__":
    with open('job description.txt', 'r') as file:
        descrip = file.read()
    with open('job details.json','r') as file:
        deets = json.loads(file.read())
        job = JobInfo(descrip, deets['title'], deets['company'], deets['location'])
    write_coverletter(job)
    
