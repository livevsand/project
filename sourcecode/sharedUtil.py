from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import time
import random

class JobInfo:
    #make it a dictionary?
    def __init__(self, description: str, title: str, company: str, location: str):
        self.description = description
        self.title = title
        self.company = company
        self.location = location


def strong_click(y: WebElement, driver: webdriver) -> None:
    try:
        y.click()
        return
    except (ElementClickInterceptedException, ElementNotInteractableException):
        pass
    try:
        time.sleep(.1)
        driver.execute_script("arguments[0].scrollIntoView();", y)
        time.sleep(.1)
        ActionChains(driver).move_to_element(y).click().perform()
        time.sleep(.1)
        return
    except (ElementClickInterceptedException, ElementNotInteractableException):
        pass

def indeed_login(driver, user_info):
    time.sleep(.1)
    try:
        driver.find_element(By.XPATH, "//a[text() = 'Sign in' and contains(@href,'login')]").click()
    except:
        pass
    time.sleep(0.1)
    email = WebDriverWait(driver, 1).until(
        EC.element_to_be_clickable(
           driver.find_element(By.XPATH, "//input[contains(@type,'email')]")))
    type_string(email, user_info['indeed email'])
    time.sleep(0.1)
    driver.find_element(By.XPATH, "//button[contains(@type,'submit')]").click()
    if fuck_captcha(driver):
        driver.find_element(By.XPATH, "//button[contains(@type,'submit')]").click()
    time.sleep(0.1)
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(
            driver.find_element(By.XPATH, "//a[contains(@id,'password-fallback')]"))).click()
    time.sleep(0.5)
    password = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(
            driver.find_element(By.XPATH, "//input[contains(@type,'password')]")))

    type_string(password, user_info['indeed password'])
    driver.find_element(By.XPATH, "//button[contains(@type,'submit')]").click()

    if fuck_captcha(driver):
        password = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                driver.find_element(By.XPATH, "//input[contains(@type,'password')]")))
        type_string(password, user_info['indeed password'])
        driver.find_element(By.XPATH, "//button[contains(@type,'submit')]").click()
    time.sleep(0.1)

def type_string(elem: WebElement, text: str) -> None:
    random.seed(420)
    for x in text:
        elem.send_keys(x)
        r = random.uniform(0, .1)
        time.sleep(r)


def fuck_captcha(driver: webdriver) -> bool:
    time.sleep(1)
    try:
        driver.switch_to.frame(driver.find_element(By.XPATH, "//iframe[contains(@title,'hCaptcha')]"))
        driver.find_element(By.XPATH, "//div[@id='checkbox']").click()
        driver.switch_to.default_content()
        return True
    except NoSuchElementException:
        return False
