import os
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, \
    ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

FACEBOOK_EMAIL = os.environ.get("FACEBOOK_EMAIL")
FACEBOOK_PASSWORD = os.environ.get("FACEBOOK_PASSWORD")
SLEEP_TIME = 2

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)  # Keeps the browser open!
chrome_options.add_argument("--start-maximized")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get("https://tinder.com/")

# Proceed to log in
time.sleep(SLEEP_TIME)
login_btn = driver.find_element(By.XPATH, '//*[@id="c-60880778"]/div/div[1]/div/main/div['
                                          '1]/div/div/div/div/header/div/div[2]/div[2]/a')

login_btn.click()

# Facebook login
time.sleep(SLEEP_TIME)
fb_login_btn = driver.find_element(By.XPATH,
                                   '//*[@id="c160459658"]/main/div/div/div[1]/div/div/div[3]/span/div[2]/button')
fb_login_btn.click()

# Switch to Facebook window and allow cookies
tinder_window = driver.window_handles[0]
fb_login_window = driver.window_handles[1]
driver.switch_to.window(fb_login_window)

time.sleep(SLEEP_TIME)
buttons = driver.find_elements(By.TAG_NAME, "button")

# Find the correct cookie button
for btn in buttons:
    if btn.get_attribute("title") == "Only allow essential cookies":
        btn.click()

# Find elements and pass in the credentials
time.sleep(SLEEP_TIME)
email_input = driver.find_element(By.ID, "email")
password_input = driver.find_element(By.ID, "pass")
sign_in_btn = driver.find_element(By.NAME, "login")

email_input.send_keys(FACEBOOK_EMAIL)
password_input.send_keys(FACEBOOK_PASSWORD)
sign_in_btn.click()

# Switch back to Tinder window: allow location, disable notifications, reject cookies
driver.switch_to.window(tinder_window)

tinder_loaded = None
while not tinder_loaded:
    try:
        allow_location_btn = driver.find_element(
            By.XPATH, '//*[@id="c160459658"]/main/div/div/div/div[3]/button[1]/div[2]/div[2]'
        )
    except NoSuchElementException:
        print("Tinder hasn't loaded yet - sleeping for 10s...")
        time.sleep(10)
    else:
        tinder_loaded = True
        allow_location_btn.click()

time.sleep(SLEEP_TIME)
disable_notifications_btn = driver.find_element(By.XPATH, '//*[@id="c160459658"]/main/div/div/div/div[3]/button['
                                                          '2]/div[2]/div[2]')
disable_notifications_btn.click()

time.sleep(SLEEP_TIME)
reject_cookies_btn = driver.find_element(By.XPATH, '//*[@id="c-60880778"]/div/div[2]/div/div/div[1]/div['
                                                   '2]/button/div[2]/div[2]')
reject_cookies_btn.click()
time.sleep(5)

cards_available = True

while cards_available:

    # Try to locate the card. Go to sleep if not available
    card_loaded = None
    retries = 0

    while not card_loaded:

        # Refresh the page after 5 retries to load a card.
        if retries == 3:
            print("That didn't work - refreshing the page...")
            driver.refresh()

        try:
            time.sleep(10)
            bullets_div = driver.find_element(By.XPATH,
                                              '//*[@id="c-60880778"]/div/div[1]/div/main/div[1]/div/div/div[1]/div['
                                              '1]/div/div[2]/div[1]/div[2]'
                                              )
            bullets = bullets_div.find_elements(By.TAG_NAME, "button")

        except NoSuchElementException:
            print("Couldn't find any bullets - checking if this is a single picture card...")
            try:
                btns = driver.find_elements(By.CSS_SELECTOR, "span.Hidden")
                for btn in btns:
                    if btn.text == "Like":
                        like_btn = btn
                    elif btn.text == "Nope":
                        nope_btn = btn
                    else:
                        print("Neither of the available buttons is like/hope - going ahead...")
                        continue
            except NoSuchElementException:
                # Couldn't find the buttons - card hasn't been loaded yet - sleeping for 5s...
                print("Couldn't find any buttons - sleeping for 5s and retrying..")
                time.sleep(5)
                retries += 1
            else:  # Try block successful
                print("Like/nope buttons found. Click!")
                like_btn.click()
        else:
            pics_count = len(bullets)
            print(f"There are {pics_count} pictures available!")
            card_loaded = True

    # Browse photos
    for index, bullet in enumerate(bullets):
        try:
            bullet.click()
        except ElementNotInteractableException:  # Catch preview
            print("Preview detected! Breaking the loop...")
            break
        except ElementClickInterceptedException:  # 'Add to Home Screen' modal
            print("Annoying modal detected! Trying to close it...")
            time.sleep(2)
            try:
                close_modal_btn = driver.find_element(By.XPATH, "/html/body/div[2]/main/div/div[2]/button[2]")
                close_modal_btn.click()
            except ElementClickInterceptedException:  # 'Out of likes' modal
                print("Looks like we're out of likes! Closing the modal and the browser.")
                close_modal_btn = driver.find_element(By.XPATH, "/html/body/div[2]/main/div/div[3]/button[2]")
                close_modal_btn.click()
                time.sleep(10)
                driver.quit()
        else:
            print(f"Pic #{index + 1} - sleeping for 3s...")
            time.sleep(3)

    time.sleep(3)

    try:
        like_btn = driver.find_element(
            By.XPATH, "/html/body/div[1]/div/div[1]/div/main/div[1]/div/div/div[1]/div[1]/div/div[3]/div/div[4]/button"
        )

        nope_btn = driver.find_element(
            By.XPATH, "/html/body/div[1]/div/div[1]/div/main/div[1]/div/div/div[1]/div[1]/div/div[3]/div/div[2]/button"
        )
    except NoSuchElementException:
        print("Couldn't find like/nope button :( Trying an alternative...")
        for btn in driver.find_elements(By.CSS_SELECTOR, "span.Hidden"):
            if btn.text == "Like":
                like_btn = btn
            elif btn.text == "Nope":
                nope_btn = btn

    like_btn.click()
