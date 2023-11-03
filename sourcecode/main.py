from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.remote.webelement import WebElement

import time
import traceback
import random
import sys

import jobhostUtil
import sharedUtil as util


class JobSite(ABC):
    def __init__(self, url: str, chatGPT: bool):
        self.url = url
        self.chatGPT = chatGPT
        self.applied_message = None
        self.driver, self.user_info, self.applied_list = jobhostUtil.load(url)

    @abstractmethod
    def startup(self):
        '''
        every jobsite has its own BS we need to click through
        '''
        pass

    def get_info(self, x: webdriver) -> util.JobInfo:
        '''
        retrieve job info from site and save as object
        '''
        # t= self.driver.find_elements(By.XPATH, self.job)
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, self.job)))
        description = self.driver.find_element(By.XPATH, self.job).text
        description = description.replace('About the job', '')
        description = jobhostUtil.strip_non_ascii(description)
        description = description.replace('\n', '')
        description = description[:2000]
        title = jobhostUtil.strip_non_ascii(x.find_element(By.XPATH, self.title_ref).text)
        if '\n' in title:
            title = title.splt('\n')[0]
        # glassdoor takes company title plus rating
        company_name = jobhostUtil.strip_non_ascii(x.find_element(By.XPATH, self.company_ref).text)
        location = jobhostUtil.strip_non_ascii(x.find_element(By.XPATH, self.location_ref).text)
        if '(' in location:
            location = location[:location.find('(')].strip()
        return util.JobInfo(description, title, company_name, location)

    def apply_to_job(self, current_job: util.JobInfo):
        '''
        click apply and try to determine job before switching tab to new window
        '''
        # retry for stale elements
        try:
            apply = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, self.apply_ref)))
        except (TimeoutException, StaleElementReferenceException):
            print('could not find apply button retry')
            time.sleep(1)
            try:
                apply = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, self.apply_ref)))
            except (TimeoutException, StaleElementReferenceException):
                print('could not find apply button exiting')
                return
        util.strong_click(apply, self.driver)
        if isinstance(self, Glassdoor):
            try:
                WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Skip For Now']"))).click()
            except TimeoutException:
                pass
        site = jobhostUtil.determine_website(self.driver, self.user_info, self.chatGPT, current_job, apply)
        applied = site.question_cycle()

        jobhostUtil.status(self.applied_list, applied, current_job, self.driver.current_url)

    def find_jobs(self, rounds: int):
        '''
        crawl job site and apply to all jobs
        '''
        time.sleep(1)
        while len(self.driver.find_elements(By.XPATH, self.job_grid)) == 0:
            print("captcha")
            time.sleep(5)
        for i in range(rounds):
            time.sleep(2)
            for x in self.driver.find_elements(By.XPATH, self.job_grid):
                try:
                    time.sleep(1)
                    # try:
                    #    WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable(x))
                    # except StaleElementReferenceException:
                    #    WebDriverWait(self.driver, 2).until(EC.staleness_of(x))

                    # self.driver.execute_script("return arguments[0].scrollIntoView(true);", x)
                    ActionChains(self.driver).move_to_element(x).click().perform()
                    current_job = self.get_info(x)
                    try:
                        if (self.applied_message is None or len(x.find_elements(By.XPATH, self.applied_message)) == 0) and not jobhostUtil.should_apply(
                                current_job, self.applied_list):
                            self.apply_to_job(current_job)
                    except Exception:
                        print('could not apply to job')
                        traceback.print_exc()
                        jobhostUtil.status(self.applied_list, False, current_job, self.driver.current_url)
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        time.sleep(.1)
                        pass

                except Exception:
                    print('missed job post')

                    traceback.print_exc()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    time.sleep(.1)
                    pass

            if isinstance(self, LinkedIn):
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Page " + str(i + 2) + "']"))).click()
            else:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, self.next_button))).click()


class LinkedIn(JobSite):
    def __init__(self, url: str, chatGPT: bool):
        super().__init__(url, chatGPT)
        self.job = "//div[contains(@id,'job-details')]"
        self.company_ref = ".//span[@class = 'job-card-container__primary-description ']"
        self.title_ref = ".//a[@class = 'disabled ember-view job-card-container__link job-card-list__title']"
        self.location_ref = ".//div[@class = 'artdeco-entity-lockup__caption ember-view']"
        self.apply_ref = "//button[contains(@class,'jobs-apply-button')]"
        self.job_grid = "//li[contains(@class,'jobs-search-results')]"
        self.next_button = None
        self.applied_message = ".//span[contains(text(), 'Applied')]"
        self.startup()

    def startup(self):
        time.sleep(.1)
        self.driver.find_element(By.XPATH, "//a[contains(@data-tracking-control-name,'signin')]").click()
        time.sleep(.1)
        util.type_string(self.driver.find_element(By.XPATH, "//input[@id= 'username']"), self.user_info['linkedin email'])
        util.type_string(
            self.driver.find_element(By.XPATH, "//input[@id= 'password']"), self.user_info["linkedin password"])

        self.driver.find_element(By.XPATH, "//button[@type= 'submit']").click()


class Glassdoor(JobSite):
    def __init__(self, url: str, chatGPT: bool):
        super().__init__(url, chatGPT)
        # self.job_grid = "//li[starts-with(@class,'react-job-listing')]"
        self.job_grid = "//li[starts-with(@class,'JobsList')]"
        # self.job = "//div[@class='jobDescriptionContent desc']"
        self.job = "//div[contains(@class,'JobDetails_jobDescriptionWrapper__BTDTA')]"
        self.next_button = "//button[starts-with(@class,'nextButton')]"
        self.company_ref = "//div[starts-with(@class,'EmployerProfile_employerInfo')]"
        self.title_ref = "//div[contains(@class,'JobDetails_jobTitle')]"
        self.location_ref = "//div[contains(@class,'JobDetails_location')]"
        self.apply_ref = "//button[@data-test='apply-button'] | //button[@data-test='applyButton'] | //a[@data-test='applyButton']"
        self.startup()

    def startup(self):
        self.driver.find_element(By.XPATH, self.job_grid).click()
        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-role-variant='ghost']"))).click()
        self.driver.switch_to.default_content()


class Indeed(JobSite):
    def __init__(self, url: str, chatGPT: bool):
        super().__init__(url, chatGPT)

        # self.job_grid = "//ul[starts-with(@class,'jobsearch')]/li"
        self.job_grid = "//div[@id='mosaic-provider-jobcards']/ul/li"
        self.job = "//div[@id='jobDescriptionText']"
        self.next_button = "//a[contains(@data-testid,'page-next')]"
        # self.company_ref = "//span[@class='companyName']"
        self.company_ref = "//div[@data-company-name='true']/span/a"
        # self.title_ref = "//span[contains(@id,'jobTitle')]"
        self.title_ref = "//h2[contains(@class,'jobsearch-JobInfoHeader-title')]/span"
        self.location_ref = "//div[@data-testid='job-location'] | //div[contains(@data-testid,'Location')]"
        # self.location_ref = "//div[@class='companyLocation']"
        self.apply_ref = "//button[@id='indeedApplyButton'] | //button[contains(@aria-label,'Apply on company site')] "

        self.startup()
        time.sleep(1)
        self.driver.get(url)
        time.sleep(.5)
        self.driver.switch_to.frame(self.driver.find_element(By.XPATH, "//iframe[@title='Sign in with Google Dialog']"))
        time.sleep(1)
        self.driver.find_element(By.XPATH, "//div[contains(text(),'Continue as ')]").click()
        time.sleep(2)
        self.driver.switch_to.default_content()

    def startup(self):
        util.indeed_login(self.driver, self.user_info)


def start(URL, chatGPT):
    try:
        if 'linkedin' in URL:
            LinkedIn(URL, chatGPT).find_jobs(50)

        elif 'indeed' in URL:
            Indeed(URL, chatGPT).find_jobs(50)
        elif 'glassdoor' in URL:
            Glassdoor(URL, chatGPT).find_jobs(50)
        else:
            raise NotImplementedError
        print('done')

    except Exception:
        traceback.print_exc()
        print('error')
        raise SystemExit


if __name__ == '__main__':
    if len(sys.argv) > 0:
        URL = sys.argv[1]
        chatGPT = sys.argv[2] == 'True'

    URL = 'https://www.linkedin.com/jobs/search/?currentJobId=3743846126&distance=25&f_TPR=r604800&geoId=103644278&keywords=machine%20learning&origin=JOB_SEARCH_PAGE_JOB_FILTER'
    URL = 'https://www.indeed.com/jobs?q=machine+learning&l=&from=searchOnHP&vjk=d090c7b218f833ee'
    chatGPT = True
    start(URL, chatGPT)
