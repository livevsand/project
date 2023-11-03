from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.remote.webelement import WebElement
import time
import os
import re
import traceback
from datetime import date
import bigQuestion as bQ
import sharedUtil as util

QUESTIONS_FOR_CHATGPT = ['cover letter', 'what do you already know about', 'why are you interested', "particular topics you're interested",
                         'recent machine learning paper that you have read', 'why did you find this paper interesting', 'paper relevant to the work',
                         'please give 1-2 sentences', 'provide brief answers', 'summary', 'please elaborate',
                         'what about this role in particular interests you',
                         'provide which relevant technologies you are experienced with', 'why are you looking for a new opportunity',
                         'message to the hiring manager', 'what makes you unique', 'list your top 5 technical skills', 'aligns with what you’re looking',
                         'describe', 'what is an exciting', 'in your opinion', 'what most excites', 'why would you like', 'discuss your experience',
                         'what was your area of focus', 'tell us about a time', 'why do you want to join','What interests you to apply for this role']


def popup_remove(driver: webdriver) -> None:
    '''
    remove linkedin popups after applying
    '''
    time.sleep(1)
    try:
        y = driver.find_element(By.XPATH, "//li-icon[@class= 'artdeco-button__icon'] | //button[@type='submit'] | //button[@aria-label='Dismiss']")
        driver.execute_script("arguments[0].scrollIntoView();", y)
        time.sleep(.5)
        ActionChains(driver).move_to_element(y).click().perform()
    except NoSuchElementException:
        pass
    try:
        driver.find_element(By.XPATH, "//div[@class='scaffold-layout__list ']").click()
    except NoSuchElementException:
        pass
    time.sleep(.1)


def questions_for_chatGPT_check(question: str) -> bool:
    '''
    checks if question contains a phrase that should be answered by a LLM
    '''
    for x in QUESTIONS_FOR_CHATGPT:
        if x in question:
            return True
    return False


def question_process(x: WebElement, user_info: dict, driver: webdriver, current_job, chatGPT: bool) -> None:
    '''
    make sure we have a question and get our response
    '''
    question = x.text.lower()

    if len(question) == 0:
        # find question
        try:
            question = x.find_element(By.XPATH, ".//*[@placeholder]").get_attribute("placeholder")
        except NoSuchElementException:
            pass
    if '\n' in question:
        question = question.split('\n')[0]
    # if "date" in question:
    #    datebox(x)
    if len(question) > 0 and "resume" not in question:
        res = find_response(question, user_info)
        if res is None and questions_for_chatGPT_check(question):
            if chatGPT:
                res = bQ.answer(question, current_job, False)
            else:
                return
        if res is None:
            print(question)
            print('could not find answer')
        get_element_type(x, res, driver)


def send_files(driver: webdriver, current_job, user_info: dict, chatGPT: bool) -> None:
    '''
    upload files to job app site
    '''
    files_to_send = driver.find_elements(By.XPATH, "//input[@type='file']")
    # smart recuiter does not like send file
    if len(files_to_send) > 0:
        files_to_send[0].send_keys(os.getcwd() + "\\user_info\\" + user_info['resume'])
    if len(files_to_send) > 1 and chatGPT:
        bQ.write_coverletter(current_job)
        files_to_send[1].send_keys(os.getcwd() + "\\user_info\\" + "cover-letter.txt")
    if len(files_to_send) > 2:
        try:
            files_to_send[2].send_keys(os.getcwd() + "\\user_info\\" + user_info['transcript'])
        except FileNotFoundError:
            print('Transcript not found')


def get_element_type(x: WebElement, res: str, driver: webdriver) -> None:
    '''
    determine type of element we need to respond to
    '''

    if len(x.find_elements(By.XPATH, ".//input[@type='date']")) > 0:
        x = x.find_element(By.XPATH, ".//input[@type='date']")
        datebox(x)
    elif len(x.find_elements(By.XPATH,
                             ".//*[@role='combobox' or @aria-haspopup='true' or @aria-haspopup='listbox'] | .//input[contains(@class,'autocomplete')]")) > 0:
        combobox(x, res, driver)
    elif len(x.find_elements(By.XPATH, ".//input[@type='text' or @type='email' or @type='password']")) > 0:
        x = x.find_element(By.XPATH, ".//input[@type='text' or @type='email' or @type='password']")
        textbox(x, res)
    elif len(x.find_elements(By.XPATH, ".//textarea[not(contains(@title,'Enter manually'))]")) > 0:
        x = x.find_element(By.XPATH, ".//textarea[not(contains(@title,'Enter manually'))]")
        textbox(x, res)
    elif len(x.find_elements(By.XPATH, ".//select")) > 0:
        x = x.find_element(By.XPATH, ".//select")
        selectbox(x, res, driver)
    elif len(x.find_elements(By.XPATH, ".//input[@type='number' or @type='tel' or contains(@id,'numeric')]")) > 0:
        x = x.find_element(By.XPATH, ".//input[@type='number' or @type='tel' or contains(@id,'numeric')]")
        numberbox(x, res)
    elif len(x.find_elements(By.XPATH, ".//button")) > 0:
        x = x.find_elements(By.XPATH, ".//button")
        button(x, res)
    elif len(x.find_elements(By.XPATH, ".//input[@type='radio' or @type='checkbox']")) > 0:
        x = x.find_elements(By.XPATH, ".//input[@type='radio' or @type='checkbox']")
        radio_button(x, res, driver)

    elif x.get_attribute('type') == 'text' or x.tag_name == 'textarea':
        textbox(x, res)
    elif x.get_attribute('type') == 'numeric' or x.get_attribute('type') == 'tel':
        numberbox(x, res)
    else:
        print("could not determine type of elem")


def datebox(y: WebElement) -> None:
    '''
    HTML datebox object
    '''
    d = date.today()
    d = str(d.month) + '/' + str(d.day) + '/' + str(d.year)
    try:
        x.find_element(By.XPATH, ".//input[contains(@aria-label,'Month')]").send_keys(str(d.month))
        x.find_element(By.XPATH, ".//input[contains(@aria-label,'Day')]").send_keys(str(d.day))
        x.find_element(By.XPATH, ".//input[contains(@aria-label,'Year')]").send_keys(str(d.year))
        return
    except:
        pass
    try:
        t = y.find_element(By.XPATH, ".//input[@calendar-picker]")
        d = date.today()
        t.send_keys(str(d.month) + str(d.day) + str(d.year))
        return
    except Exception:
        traceback.print_exc()
        pass
    y.send_keys(d)


def button(y: list, res: str) -> None:
    for x in y:
        for r in res.split('|'):
            if x.text.lower() == r.lower():
                x.click()
                return
    y[0].click()
    print('default')


def find_elem(t: WebElement, xpath_list: list) -> WebElement | None:
    for x in xpath_list:
        try:
            return t.find_element(By.XPATH, x)
        except NoSuchElementException:
            pass
    return None


def combobox(t: WebElement, res: str, driver: webdriver) -> None:
    '''
    HTML combobox object
    if we cannot find response use last option on dropdown
    '''

    dropdown_elem = find_elem(t,
                              [".//button[@aria-haspopup='listbox']", ".//div[contains(@class,'select2-container')]", ".//input[@role='combobox']", ".//div"])
    if dropdown_elem is None:
        dropdown_elem = t

    util.strong_click(dropdown_elem, driver)

    '''
        combo box w/ search feature
    '''
    try:
        DROPDOWN_CHOICES = ".//*[@role='option'] | //div[@id='select2-drop']//ul//div[@role='option'] | //*[@role='menuitem' and not(ancestor::div[contains(@style,'display: none')])] | .//div[contains(@class,'autocomplete-dropdown')]"
        time.sleep(.1)
        percent_off = 1
        final_choice = None
        if res == None:
            elem = driver.switch_to.active_element
            elem.send_keys(Keys.DOWN)
            elem.send_keys(Keys.ENTER)
            print ('could not find response sending defalut')
            return
        for res2 in res.split('|'):
            # elem = t.find_elements(By.XPATH, ".//*[@role ='combobox'] | //div[@id ='select2-drop']//div//input | .//input[@aria-label='Search']")
            elem = driver.switch_to.active_element
            elem.send_keys(Keys.CONTROL + "a")
            elem.send_keys(Keys.DELETE)
            elem.send_keys(res2)
            time.sleep(1)
            option = t.find_elements(By.XPATH, DROPDOWN_CHOICES)
            for choice in option:
                if res2.lower() in choice.text.lower() and (len(choice.text) - len(res2)) / len(choice.text) < percent_off:
                    final_choice = choice.text
                    percent_off = (len(choice.text) - len(res2)) / len(choice.text)
                    if percent_off == 0:
                        break
            if percent_off == 0:
                break
        # this is a more robust method for cicking then finding the element from options and sending a click
        # y tho?
        if final_choice is not None:
            for res2 in res.split('|'):
                elem = driver.switch_to.active_element
                elem.send_keys(Keys.CONTROL + "a")
                elem.send_keys(Keys.DELETE)
                elem.send_keys(res2)
                time.sleep(1)
                option = t.find_elements(By.XPATH, DROPDOWN_CHOICES)
                for choice in option:
                    if choice.text == final_choice:
                        elem.send_keys(Keys.ENTER)
                        return
                    elem.send_keys(Keys.DOWN)

        raise Exception

    except NoSuchElementException:
        '''
            w/o
        '''
        time.sleep(.1)
        options = t.find_elements(By.XPATH, ".//*[@role='option'] | .//*[@role='menuitem'] |//div[@id='select2-drop']//ul//div[@role='option']")
        if len(options) == 0:
            options = t.find_elements(By.XPATH, "//*[@role='option'] | .//*[@role='menuitem']")

        if res is None:
            util.strong_click(options[-1], driver)
            print('default')
            return
        most_likely = None
        most_likely_len = 0
        for z in options:

            for r in res.split('|'):
                if ('yes' in z.text.lower() or 'no' == z.text.lower()) and r.lower() != 'no':
                    r = 'yes'
                if r.lower() == z.text.lower():
                    util.strong_click(z, driver)
                    return
                if r.lower() in z.text.lower() and most_likely_len < len(z.text.lower()):  # fix
                    most_likely = z
                    most_likely_len = len(z.text.lower())

        time.sleep(.1)
        if most_likely is not None:
            util.strong_click(most_likely, driver)
        else:
            util.strong_click(options[-1], driver)
            print('could not find response')


def find_response(question: str, response: dict) -> None | str:
    '''
    check if question is answered in user info and if so returns answer else None
    '''
    if question is None:
        return None
    question = question.lower()

    if question in response.keys():
        return response[question]

    saved_key = ''
    percent_off = 1
    for key, value in response.items():
        if key in question and (len(question) - len(key)) / len(question) < percent_off:
            saved_key = key
            percent_off = (len(question) - len(key)) / len(question)
            if percent_off == 0:
                return response[saved_key]

    if len(saved_key) == 0:
        return None
    return response[saved_key]


def radio_button(t: list, res: str, driver: webdriver) -> None:
    '''
    HTML radiobutton object
    if we cannot find response use last button in radiomenu
    '''
    # change values to binary if that is the only way we are alowed to interact
    # old format
    # print(t[0].get_attribute("value").lower() )

    if t[0].accessible_name.lower() in ['true', 'false'] and res not in ['true', 'false']:
        res = 'true'
    elif t[0].accessible_name.lower() in ['yes', 'no'] and res not in ['yes', 'no', 'no|never']:
        res = 'yes'

    if res is None:
        util.strong_click(t[0], driver)
        print('default')
        return
    for y in t:
        for r in res.split('|'):
            if r.lower() in y.accessible_name.lower():
                util.strong_click(y, driver)
                return
    print("could not find response")
    util.strong_click(t[-1], driver)


def numberbox(t: WebElement, res: str) -> None:
    '''
    HTML numberbox object
    if we cannot find response use 0
    '''
    t.send_keys(Keys.CONTROL + "a")
    t.send_keys(Keys.DELETE)
    if res is None:
        print(0)
        t.send_keys(0)
    elif res.isdigit():
        t.send_keys(int(res))
    else:
        try:
            t.send_keys(float(res))
        except NoSuchElementException:
            textbox(t, res)


def selectbox(t: WebElement, res: str, driver: webdriver) -> None:
    '''
    HTML selectbox object
    if we cannot find response use 2nd from top
    '''
    # util.strong_click(t, driver)
    select = Select(t)
    if res is None:
        select.select_by_index(1)
        print('default')
        return
    final_choice = ''
    for x in select.options:
        try:
            x_text = x.accessible_name
        except:
            x_text = x.text
        percent_off = 1
        for r in res.split('|'):
            if r.lower() in x_text.lower() and (len(x_text) - len(r)) / len(x_text) < percent_off:
                final_choice = x_text
                percent_off = (len(x_text) - len(r)) / len(x_text)
                if percent_off == 0:
                    select.select_by_visible_text(final_choice)
                    return

    if len(final_choice) > 0:
        select.select_by_visible_text(final_choice)
    else:
        select.select_by_index(1)
        print('could not find response')


def textbox(t: WebElement, res: str) -> None:
    '''
    HTML textbox object
    if we cannot find response use yes
    '''
    try:
        t.click()
    except:
        pass
    t.send_keys(Keys.CONTROL + "a")
    t.send_keys(Keys.DELETE)
    if res is None:
        print('yes')
        t.send_keys("yes")
    else:
        res = res.split("|")[0]
        t.send_keys(res)
