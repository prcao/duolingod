from fnmatch import translate
import googletrans
from googletrans import Translator
from matplotlib.style import available
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from pypinyin import pinyin
import random
from dragonmapper.transcriptions import accented_to_numbered, numbered_to_accented
import util
from selenium.webdriver.common.keys import Keys

translator = Translator()

options = Options()
options.add_argument("--disable-notifications")

driver = webdriver.Chrome(
    executable_path=ChromeDriverManager().install(), chrome_options=options)
# driver.implicitly_wait(10)

wait = WebDriverWait(driver, 10)

# go to duolingo
driver.get("https://www.duolingo.com/learn")

ac = ActionChains(driver)

login_xpath = "//span[contains(text(),'I ALREADY HAVE AN ACCOUNT')]"
wait.until(EC.presence_of_all_elements_located((By.XPATH, login_xpath)))
login = driver.find_element(By.XPATH, login_xpath)
login.click()

user_field_xpath = "//input[@placeholder='Email or username']"
wait.until(EC.presence_of_all_elements_located((By.XPATH, user_field_xpath)))
user_field = driver.find_element(By.XPATH, user_field_xpath)
user_field.send_keys("duolingod@mailinator.com")

pw_field_xpath = "//input[@placeholder='Password']"
pw_field = driver.find_element(By.XPATH, pw_field_xpath)
pw_field.send_keys("duolingod")

login_btn_xpath = "//span[contains(text(), 'LOG IN')]"
login_btn = driver.find_element(By.XPATH, login_btn_xpath)
login_btn.click()

while True:

    try:
        time.sleep(1)
        driver.get("https://www.duolingo.com/learn")
        time.sleep(3)

        check_btn = driver.find_elements(
            By.XPATH, "//button[@data-test='player-next' and @aria-disabled='false']")
        while check_btn:
            check_btn[0].click()
            check_btn = driver.find_elements(
                By.XPATH, "//button[@data-test='player-next' and @aria-disabled='false']")
            time.sleep(1)

        no_thanks_btn = driver.find_elements(
            By.XPATH, "//button[@data-test='plus-no-thanks']")
        if no_thanks_btn:
            no_thanks_btn[0].click()
            time.sleep(1)

        wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, '.Mr3if._2OhdT')))
        available_lessons = driver.find_elements(By.CSS_SELECTOR, '.Mr3if._2OhdT')

        for available_lesson in available_lessons:
            crown = available_lesson.find_elements(
                By.XPATH, "..//div[@data-test='level-crown']")
            if crown and crown[0].get_attribute('innerText') == '5':
                continue
            if crown:
                print("CROWN LEVEL", crown[0].get_attribute('innerText') == '5')

            lesson = available_lesson

        ac.move_to_element(lesson).click().perform()

        time.sleep(1)

        print('starting')
        start_btn = driver.find_element(By.XPATH, "//a[@data-test='start-button']")
        start_btn.click()

        # lesson started!
        answer_cache = {}
        while True:
            time.sleep(.5)

            # check if lesson is complete
            if driver.find_elements(
                    By.XPATH, "//span[contains(text(),'Lesson Complete!')]"):
                print(">>>>>>> Lesson complete!")
                break

            # check if there is a green button to be clicked
            check_btn = driver.find_elements(
                By.XPATH, "//button[@data-test='player-next' and @aria-disabled='false']")
            if check_btn:
                check_btn[0].click()
                time.sleep(.5)

            question_type = driver.find_elements(By.XPATH, "//h1/span")

            if not question_type:
                time.sleep(.5)
                continue

            # setup keyboard if needed
            keyboard_toggle_text = driver.find_elements(
                By.XPATH, "//div[contains(@class, 'yWRY8') and contains(@class, '_3yAjN')]")

            if keyboard_toggle_text:
                if keyboard_toggle_text[0].get_attribute('innerText') == 'USE KEYBOARD':
                    use_keyboard_toggle_btn = driver.find_element(
                        By.XPATH, "//button[@data-test='player-toggle-keyboard']")
                    use_keyboard_toggle_btn.click()

            question_type = question_type[0]
            print("===============")
            print(question_type.text)

            # start answering
            if question_type.text.startswith('Select the correct character(s) for'):
                choices = driver.find_elements(
                    By.XPATH, "//div[@data-test='challenge-choice']")

                print(choices[0].find_element(
                    By.XPATH, "./div[1]/span").get_attribute("innerText"))

                texts = [choice.find_element(
                    By.XPATH, "./div[1]/span").get_attribute("innerText") for choice in choices]
                print(texts)
                pinyins = [util.get_pinyin(text).replace(" ", "") for text in texts]

                target_pinyin = re.findall(
                    '“([^”]*)”', question_type.text)[0].replace(" ", "")

                print(pinyins)
                print('target=', target_pinyin)

                answer_index = util.pinyin_index(pinyins, target_pinyin)
                choices[answer_index].click()

            elif question_type.text.startswith('Write this in English'):
                foreign_text = driver.find_element(
                    By.XPATH, "//div[@dir='ltr']/span")
                text = foreign_text.get_attribute("innerText")

                if text in answer_cache:
                    eng_text = answer_cache[text]
                else:
                    possible_translations = [x[0] for x in translator.translate(
                        text).extra_data['parsed'][1][0][0][5][0][4]]
                    eng_text = random.choice(possible_translations)

                print(text, '->', eng_text)

                text_area = driver.find_element(By.XPATH, "//textarea")
                text_area.send_keys(eng_text)
                text_area.send_keys(Keys.ENTER)

                time.sleep(.5)

                if driver.find_elements(By.XPATH, "//h2[contains(text(), 'Correct solution:')]"):
                    correct_sol = driver.find_elements(By.XPATH, "//div[@class='_1UqAr _3Qruy']")
                    if correct_sol:
                        print("CACHING ANSWER", correct_sol[0].get_attribute('innerText'))
                        answer_cache[text] = correct_sol[0].get_attribute('innerText')
                    else:
                        print("Oh shit got this wrong and didnt get the answer")

            elif question_type.text.startswith('Write this in Chinese'):
                eng_text = driver.find_element(
                    By.XPATH, "//div[@dir='ltr']/span")
                text = eng_text.get_attribute("innerText")

                if text in answer_cache:
                    foreign_text = answer_cache[text]
                else:
                    foreign_text = translator.translate(
                        text, src="en", dest="zh-cn").text

                print(text, '->', foreign_text)

                text_area = driver.find_element(By.XPATH, "//textarea")
                text_area.send_keys(foreign_text)
                text_area.send_keys(Keys.ENTER)

                time.sleep(.5)

                if driver.find_elements(By.XPATH, "//h2[contains(text(), 'Correct solution:')]"):
                    correct_sol = driver.find_elements(By.XPATH, "//div[@class='_1UqAr _3Qruy']")
                    if correct_sol:
                        print("CACHING ANSWER", text, '->', correct_sol[0].get_attribute('innerText'))
                        answer_cache[text] = correct_sol[0].get_attribute('innerText')
                    else:
                        print("Oh shit got this wrong and didnt get the answer")

            elif question_type.text.startswith("Select the matching pairs"):

                choices = driver.find_elements(
                    By.XPATH, "//button[@data-test='challenge-tap-token']")

                pinyin_choices = choices[:len(choices)//2]
                char_choices = choices[len(choices)//2:]

                pinyin_texts = [choice.get_attribute("innerText").split(
                )[1].replace(" ", "") for choice in pinyin_choices]
                char_texts = [choice.get_attribute("innerText").split()[
                    1] for choice in char_choices]
                print(pinyin_texts)
                print(char_texts)

                for i in range(len(char_texts)):
                    py = util.get_pinyin(char_texts[i]).replace(" ", "")

                    j = util.pinyin_index(pinyin_texts, py)

                    print(py, '->', pinyin_texts[j])

                    char_choices[i].click()
                    time.sleep(.1)
                    pinyin_choices[j].click()
            elif question_type.text.startswith("What sound does this make?"):

                text = driver.find_element(
                    By.XPATH, "//span[@class='sSLeO _2QCqu']").get_attribute('innerText')
                py = util.get_pinyin(text)

                print(py)


                choices = driver.find_elements(
                    By.XPATH, "//div[@data-test='challenge-judge-text']")
                pinyin_choices = [choice.get_attribute(
                    "innerText") for choice in choices]

                print(pinyin_choices)

                i = util.pinyin_index(pinyin_choices, py)

                choices[i].click()
            elif question_type.text.startswith("Which one of these is"):

                # choose one randomly, can't be bothered
                choices = driver.find_elements(By.XPATH, "//div[@data-test='challenge-choice']")
                random.choice(choices).click()

            check_btn = driver.find_element(
                By.XPATH, "//button[@data-test='player-next']")
            check_btn.click()

        print('out of inner loop')
    except:
        print('Something went wrong')
