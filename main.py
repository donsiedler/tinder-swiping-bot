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


def login():
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

    # Switch back to Tinder window
    driver.switch_to.window(tinder_window)


def close_popups():
    tinder_loaded = None
    while not tinder_loaded:
        # Popups: allow location, disable notifications, reject cookies
        try:
            allow_location_btn = driver.find_element(
                By.XPATH, '//*[@id="c160459658"]/main/div/div/div/div[3]/button[1]/div[2]/div[2]'
            )
        except NoSuchElementException:
            print("Tinder hasn't loaded yet - sleeping for 5s...")
            time.sleep(5)
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
    time.sleep(2)


login()
close_popups()

cards_available = True
while cards_available:

    # Try to locate the card. Go to sleep if not available
    card_loaded = None
    retries = 0

    while not card_loaded:
        # Check for cards
        try:
            beacon = driver.find_element(By.CSS_SELECTOR, "div.beacon")
        except NoSuchElementException:
            card_loaded = True
        else:
            print("No cards available! Refreshing...")
            driver.refresh()
            time.sleep(10)

        # Refresh the page after 5 retries to load a card.
        if retries == 3:
            print("That didn't work - refreshing the page...")
            driver.refresh()
            time.sleep(10)

        try:
            time.sleep(5)
            bullets_div = driver.find_element(By.XPATH,
                                              '//*[@id="c-60880778"]/div/div[1]/div/main/div[1]/div/div/div[1]/div['
                                              '1]/div/div[2]/div[1]/div[2]'
                                              )
            bullets = bullets_div.find_elements(By.TAG_NAME, "button")

        except NoSuchElementException:
            print("Couldn't find any bullets - checking if this is a single picture card...")
            try:
                like_btn = driver.find_element(
                    By.XPATH,
                    "/html/body/div[1]/div/div[1]/div/main/div[1]/div/div/div[1]/div[1]/div/div[3]/div/div[4]/button"
                )

                nope_btn = driver.find_element(
                    By.XPATH,
                    "/html/body/div[1]/div/div[1]/div/main/div[1]/div/div/div[1]/div[1]/div/div[3]/div/div[2]/button"
                )

            except NoSuchElementException:
                btns = driver.find_elements(By.CSS_SELECTOR, "button span span span.Hidden")
                like_btn = None
                nope_btn = None

                for btn in btns:
                    print(btn.text)
                    if btn.text == "LIKE":
                        like_btn = btn
                        print("Like button found!")
                    elif btn.text == "NOPE":
                        nope_btn = btn
                        print("Nope button found!")
                if not like_btn and not nope_btn:
                    # Couldn't find the buttons - card hasn't been loaded yet - sleeping for 5s...
                    print("Couldn't find like/nope buttons - sleeping for 5s and retrying..")
                    time.sleep(5)
                    retries += 1
                else:
                    nope_btn.click()

            else:  # Try block successful
                if like_btn and nope_btn:
                    print("Like/nope buttons found. Click!")
                    like_btn.click()

                    # Check for match
                    try:
                        close_button = driver.find_element(
                            By.XPATH, '//*[@id="c-604412971"]/main/div/div[1]/div/div[4]/button'
                        )
                    except NoSuchElementException:
                        print("It's not a match after all...")
                    else:
                        print("Close button found! It's a match!")
                        close_button.click()
        else:
            pics_count = len(bullets)
            print(f"There are {pics_count} pictures available!")
            card_loaded = True

    # Browse photos
    for index, bullet in enumerate(bullets):
        try:
            bullet.click()

        except ElementNotInteractableException:  # Preview still displaying
            print("Preview detected! Breaking the loop...")
            break

        except ElementClickInterceptedException:  # Modal found
            print("Modal detected! Figuring out what it is...")
            time.sleep(1)

            try:  # "Add to home screen' modal error handler
                close_home_screen_modal_btn = driver.find_element(
                    By.XPATH, "/html/body/div[2]/main/div/div[2]/button[2]"
                )
                close_home_screen_modal_btn.click()

            except NoSuchElementException:  # Not a 'home screen' modal!
                try:  # "Out of likes' modal error handler
                    close_modal_btn = driver.find_element(By.XPATH, "/html/body/div[2]/main/div/div[3]/button[2]")
                    print("Looks like we're out of likes! Closing the modal and the browser.")
                    close_modal_btn.click()
                    time.sleep(10)
                    driver.quit()
                except NoSuchElementException:  # Not a 'Out of likes' modal!
                    print("Looks like it's a match! Trying to close the modal...")
                    close_modal_btn = driver.find_element(
                        By.XPATH, "/html/body/div[1]/div/div[1]/div/main/div[2]/main/div/div[1]/div/div[4]/button"
                    )
                    close_modal_btn.click()

        else:
            print(f"Pic #{index + 1} - sleeping for 3s...")
            time.sleep(3)

    time.sleep(1)

    try:
        like_btn = driver.find_element(
            By.XPATH, "/html/body/div[1]/div/div[1]/div/main/div[1]/div/div/div[1]/div[1]/div/div[3]/div/div[4]/button"
        )

        nope_btn = driver.find_element(
            By.XPATH, "/html/body/div[1]/div/div[1]/div/main/div[1]/div/div/div[1]/div[1]/div/div[3]/div/div[2]/button"
        )
    except NoSuchElementException:
        print("Couldn't find like/nope button :( Trying an alternative...")
        for btn in driver.find_elements(By.CSS_SELECTOR, "button span span span.Hidden"):
            print(btn.text)
            if btn.text == "LIKE":
                like_btn = btn
            elif btn.text == "NOPE":
                nope_btn = btn

    nope_btn.click()
