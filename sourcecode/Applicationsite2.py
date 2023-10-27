from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webelement import WebElement
import time
import os
import re
import traceback
from datetime import date
import bigQuestion as bQ
import appUtil
import sharedUtil as util


#app.trinthire.com
#recruiting.ultipro.com w/ login
#rippling
def Generic_Apply(driver: webdriver, user_info: dict) -> None:

    driver.find_element(By.XPATH, "//input[contains(@id,'FIRST')] | //input[contains(@id,'First')] | //input[contains(@id,'first')]").send_keys(user_info["first name"])
    driver.find_element(By.XPATH, "//input[contains(@id,'LAST')] | //input[contains(@id,'Last')] | //input[contains(@id,'last')]").send_keys(user_info["last name"])
    driver.find_element(By.XPATH, "//input[contains(@id,'EMAIL')] | //input[contains(@id,'Email')] | //input[contains(@id,'email')]").send_keys(user_info["email"])
    util.strong_click(driver.find_element(By.XPATH, "//*[contains(text(),'APPLY')] | //*[contains(text(),'Apply')] | //*[contains(text(),'apply')] |"
                                                    "//*[contains(text(),'SUBMIT')] | //*[contains(text(),'Submit')] | //*[contains(text(),'submit')]"), driver)
    return

class GenericApplicationSite:
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool):
        self.driver, self.user_info, self.current_job, self.chatGPT = driver, user_info, current_job, chatGPT
        self.element, self.submit, self.next = None, None, None
        # //div[@class='form-field'] //button[@name='submit']
    def login(self):
        pass

    def error_exit(self):
        '''
        stops infinite loop
        '''
        raise Exception("caught in infinite loop exiting")

    def question_cycle2(self, index=0):

        t = self.driver.find_elements(By.XPATH, self.element)
        for x in range(index, len(t)):
            try:

                appUtil.question_process(t[x], self.user_info, self.driver, self.current_job, self.chatGPT)
            #except WebDriverException:
            #    self.question_cycle2(x)
            #    break
            except Exception:
                traceback.print_exc()
                print('error answering question')
                pass
            # reload elem and try again

    def question_cycle(self) -> bool:
        time.sleep(1)
        appUtil.send_files(self.driver, self.current_job, self.user_info, self.chatGPT)
        time.sleep(5)
        if self.element is None:
            '''
            true generic
            '''
            #self.element = "//div[@class='form-group'] | //div[@class='form-group ']"
            
            #Generic_Apply(self.driver, self.user_info)
            #return False
        # raise NotImplementedError
        if self.next is None:
            # will crash here if element = None and will stop apply to job
            self.question_cycle2()

        else:
            count = 0
            while len(self.driver.find_elements(By.XPATH, self.submit)) == 0:
                count += 1
                if count > 10:
                    self.error_exit()
                self.question_cycle2()
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, self.next))).click()
                time.sleep(2)

        util.strong_click(self.driver.find_element(By.XPATH, self.submit), self.driver)
        time.sleep(1)
        if isinstance(self, LinkedIn):
            appUtil.popup_remove(self.driver)
            return True
        else:
            if len(self.driver.find_elements(By.XPATH, self.submit)) == 0:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                return True
        self.driver.switch_to.window(self.driver.window_handles[0])
        return False

#needs work still detect as bot
class SmartRecruiters(GenericApplicationSite):
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool):
        super().__init__(driver, user_info, current_job, chatGPT)
        self.next = "//button[text()='Next']"
        self.element="//*[@class='hydrated'] | //div[contains(@data-test,'personal-info-')] | //*[@data-test='consent']"
        self.submit = "//button[text()='Submit']"
        self.login()
    def login(self):
        time.sleep(.5)
        try:
            self.driver.find_element(By.XPATH,"//a[@id='st-apply']").click()
        except:
            pass





class LinkedIn(GenericApplicationSite):
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool):
        super().__init__(driver, user_info, current_job, chatGPT)
        #self.element = "//*[@aria-invalid]"
        self.element = "//div[contains(@class ,'jobs-easy-apply-form-section__grouping')]"
        self.submit = "//button[@aria-label='Submit application']"
        self.next = "//button[@aria-label='Continue to next step'] | //button[@aria-label='Review your application'] | //button[@aria-label='Submit application']"

    def error_exit(self):
        WebDriverWait(self.driver, 1).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Dismiss']"))).click()
        WebDriverWait(self.driver, 1).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-control-name='discard_application_confirm_btn']"))).click()
        print('error exit')


class Workday(GenericApplicationSite):
    '''


    '''

    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool):
        super().__init__(driver, user_info, current_job, chatGPT)
        self.element = "//*[@required]/parent::*"
        self.submit = "//button[text()='Submit']"
        self.next = "//button[contains(text(),'Continue')]"

        self.login()

    def login(self):
        try:
            WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//a[text()='Apply']"))).click()
            WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@data-automation-id='autofillWithResume']"))).click()
        except TimeoutException:
            pass

        time.sleep(2)
        # login
        try:
            WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@aria-required='true']")))
            login = self.driver.find_elements(By.XPATH, "//input[@aria-required='true']")
            login[0].send_keys(self.user_info['workday email'])
            login[1].send_keys(self.user_info["workday paasword"])

            util.strong_click(self.driver.find_element(By.XPATH, "//button[text()='Sign In']"), self.driver)
        except TimeoutException:
            pass
        time.sleep(1)

    def question_cycle(self) -> bool:
        time.sleep(2)
        progress_bar = self.driver.find_element(By.XPATH, "//div[@data-automation-id='progressBar']").text.split('\n')
        for section in progress_bar:
            time.sleep(5)
            if section == 'My Experience':
                # skip for now
                appUtil.send_files(self.driver, self.current_job, self.user_info, self.chatGPT)
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, self.next))).click()
            elif section == 'Review':
                util.strong_click(self.driver.find_element(By.XPATH, self.submit), self.driver)
                time.sleep(1)
                if len(self.driver.find_elements(By.XPATH, self.submit)) == 0:
                    self.driver.close()
                    return True
                self.driver.switch_to.window(self.driver.window_handles[0])
                return False
            else:
                self.question_cycle2()
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, self.next))).click()


class Indeed(GenericApplicationSite):

    # manually fill this on out
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool):
        super().__init__(driver, user_info, current_job, chatGPT)

    def question_cycle(self) -> bool:
        self.driver.switch_to.window(self.driver.window_handles[-1])
        try:
            appUtil.textbox(WebDriverWait(self.driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@id='input-firstName']"))), self.user_info['first name'])
            appUtil.textbox(self.driver.find_element(By.XPATH, "//input[@id='input-lastName']"), self.user_info['last name'])
            try:
                appUtil.textbox(self.driver.find_element(By.XPATH, "//input[@id='input-phoneNumber']"), self.user_info['phone'])
            except NoSuchElementException:
                pass
            try:
                appUtil.textbox(self.driver.find_element(By.XPATH, "//input[@id='input-email']"), self.user_info['email'])
            except NoSuchElementException:
                pass
            self.driver.find_element(By.XPATH, "//button[starts-with(@class,'ia-continueButton')]").click()
        except TimeoutException:
            pass

        time.sleep(1)
        try:
            hold = self.driver.find_element(By.XPATH, "//input[@type='file']")
            hold.send_keys(os.getcwd() + "\\user_info\\" + self.user_info['resume'])
            time.sleep(1)
        except NoSuchElementException:
            self.driver.find_element(By.XPATH, "//div[@aria-controls='resume-display-content']").click()
            pass
        try:
            self.driver.find_element(By.XPATH, "//span[text()='Use original file']").click()
        except NoSuchElementException:
            pass
        WebDriverWait(self.driver, 1).until(
            EC.element_to_be_clickable((By.XPATH, "//button[starts-with(@class,'ia-continueButton')]"))).click()

        time.sleep(1)
        count = 0
        while len(self.driver.find_elements(By.XPATH, "//h1[contains(text(),'uestions from the employer')]")) > 0 and count < 10:
            count += 1
            q = self.driver.find_elements(By.XPATH, "//div[starts-with(@class,'ia-Questions-item')]")
            for x in q:
                appUtil.question_process(x, self.user_info, self.driver, self.current_job, self.chatGPT)
            WebDriverWait(self.driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, "//button[starts-with(@class,'ia-continueButton')]"))).click()
            time.sleep(1)

        if len(self.driver.find_elements(By.XPATH, "//h1[text()='The employer is looking for these qualifications']")) > 0:
            WebDriverWait(self.driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, "//button[starts-with(@class,'ia-continueButton')]"))).click()

        try:
            appUtil.textbox(self.driver.find_element(By.XPATH, "//input[@id='jobTitle']"), self.user_info['last job title'])
            appUtil.textbox(self.driver.find_element(By.XPATH, "//input[@id='companyName']"), self.user_info['last job company'])
            WebDriverWait(self.driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, "//button[starts-with(@class,'ia-continueButton')]"))).click()
        except NoSuchElementException:
            pass

        time.sleep(1)
        self.driver.find_element(By.XPATH, "//button[starts-with(@class,'ia-continueButton')]").click()
        time.sleep(1)
        # WebDriverWait(driver, 5).until(
        #    EC.element_to_be_clickable((By.XPATH, "//button[starts-with(@class,'ia-continueButton')]"))).click()

        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        return True


class Jobvite(GenericApplicationSite):
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool):
        super().__init__(driver, user_info, current_job, chatGPT)
        self.element = ".//*[@aria-required='true']"
        self.submit = "//button[@aria-label='Send Application']"
        self.next = "//button[@aria-label='Next']"


class Greenhouse(GenericApplicationSite):
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool):
        super().__init__(driver, user_info, current_job, chatGPT)
        self.element = "//div[@class='field']"
        self.submit = "//input[@id='submit_app']"


class Lever(GenericApplicationSite):
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool):
        super().__init__(driver, user_info, current_job, chatGPT)
        self.element = "//li[@class='application-question custom-question'] | //div[@class='application-additional']"
        self.submit = "//button[text()='Submit application']"
        self.login()

    def login(self):
        # move to login if you encouter this
        try:
            WebDriverWait(self.driver, .5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[text()='Apply for this job']"))).click()
        except NoSuchElementException:
            pass


class JobJuncture(GenericApplicationSite):

    # manually fill this on out

    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool):
        super().__init__(driver, user_info, current_job, chatGPT)

    def question_cycle(self):
        self.driver.find_element(By.XPATH, "//a[contains(text(),'Apply')]").click()
        time.sleep(1)
        self.driver.find_element(By.XPATH, "//input[@name='fullname']").send_keys(self.user_info['first name'] + ' ' + self.user_info['last name'])
        self.driver.find_element(By.XPATH, "//input[@name='email']").send_keys(self.user_info['email'])
        self.driver.find_element(By.XPATH, "//input[@name='subscribe']").click()
        self.driver.find_element(By.XPATH, "//input[@name='topresume']").click()

        appUtil.send_files(self.driver, self.current_job, self.user_info)

        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.driver.close()
        self.driver.switch_to.window(driver.window_handles[0])
        return True


class ICIMS(GenericApplicationSite):
    '''

    '''

    # TODO: 2nd page has problems find elements xpath is correct
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool):
        super().__init__(driver, user_info, current_job, chatGPT)
        #div iCIMS_TableRow
        self.element = "//div[contains(@class,'iCIMS_FieldRow_Inline') and not(@style)] | //div[@class='iCIMS_TableRow ']"
        self.submit = "//input[@type='submit']"
        self.next = "//input[@type='submit']"
        self.login()

    def login(self):
        self.driver.switch_to.frame(self.driver.find_element(By.XPATH, "//iframe[@id='icims_content_iframe']"))
        try:
            WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable(
                    self.driver.find_element(By.XPATH, "//a[@title = 'Apply for this job online']"))).click()
            time.sleep(1)
        except NoSuchElementException:
            pass
        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable(
                self.driver.find_element(By.XPATH, "//input[@type = 'email']"))).send_keys(self.user_info['icims email'])
        try:
            self.driver.find_element(By.XPATH, "//input[@type = 'checkbox']").click()
        except NoSuchElementException:
            pass
        self.driver.find_element(By.XPATH, "//input[@value = 'Next']").click()
        time.sleep(1)
        try:
            self.driver.switch_to.default_content()
            time.sleep(.5)
            self.driver.find_element(By.XPATH, "//input[@type = 'password']").send_keys(self.user_info['icims paasword'])
            time.sleep(.5)
            # hidden element causing problems i do not like this solution
            self.driver.find_elements(By.XPATH, "//button[@type = 'submit']")[1].click()
        except NoSuchElementException:
            pass


class Ashby(GenericApplicationSite):
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool):
        super().__init__(driver, user_info, current_job, chatGPT)
        self.element = "//div[contains(@class,'ashby-application-form-field-entry')]"
        self.submit = "//button[contains(@class,'submit')]"
        self.login()

    def login(self):
        try:
            WebDriverWait(self.driver, .5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Apply for this Job']"))).click()
            d = self.driver.find_element(By.XPATH, "//iframe[contains(@src,'jobs.ashby')]")
            self.driver.switch_to.frame(d)
        except NoSuchElementException:
            pass


# needs more testing
class Paylocity(GenericApplicationSite):
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool):
        super().__init__(driver, user_info, current_job, chatGPT)
        self.element = "//div[contains(@class,'form-group')]"
        self.submit = "//button[@id='btn-submit']"
        self.next = "//button[@id='btn-submit']"
        self.login()

    def login(self):
        try:
            WebDriverWait(self.driver, .5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[text()='Apply']"))).click()
        except TimeoutException:
            pass

    def question_cycle(self):
        appUtil.send_files(self.driver, self.current_job, self.user_info, self.chatGPT)
        time.sleep(2)
        appUtil.textbox(WebDriverWait(self.driver, .5).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='info.firstName']"))), self.user_info['first name'])

        appUtil.textbox(self.driver.find_element(By.XPATH, "//input[@id='info.lastName']"), self.user_info['last name'])
        appUtil.textbox(self.driver.find_element(By.XPATH, "//input[@id='info.email']"), "test" + self.user_info['email'])
        appUtil.textbox(self.driver.find_element(By.XPATH, "//input[@id='info.cellPhone']"), self.user_info['phone'])

        appUtil.combobox(self.driver.find_element(By.XPATH, "//div[@id='info.smsOptedIn']"), 'yes', self.driver)
        appUtil.combobox(self.driver.find_element(By.XPATH, "//div[@id='info.desiredSalaryType']"), 'yearly', self.driver)
        appUtil.numberbox(self.driver.find_element(By.XPATH, "//input[@id='info.minimumDesiredSalary']"), self.user_info['salary'])
        appUtil.numberbox(self.driver.find_element(By.XPATH, "//input[@id='info.maximumDesiredSalary']"), str(int(self.user_info['salary']) * 1.2))

        util.strong_click(self.driver.find_element(By.XPATH, self.next), self.driver)
        count = 0
        while len(self.driver.find_elements(By.XPATH, self.submit)) == 0:
            count += 1
            if count > 10:
                self.error_exit()
            self.question_cycle2()
            next = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, self.next)))
            util.strong_click(next, self.driver)
            time.sleep(2)
        if len(self.driver.find_elements(By.XPATH, self.submit)) == 0:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            return True
        self.driver.switch_to.window(self.driver.window_handles[0])
        return False


class Bamboo(GenericApplicationSite):
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool):
        super().__init__(driver, user_info, current_job, chatGPT)
        self.element = "//*[contains(@class,'CandidateField ')]"
        self.submit = "//span[text()='Submit Application']"
        self.login()

    def login(self):
        try:
            # i hate this solution
            time.sleep(.5)
            elem = self.driver.find_elements(By.XPATH, "//button//span[text()='Apply for This Job']")
            elem[2].click()
        except TimeoutException:
            pass
