import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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
time.sleep(5)  # Wait a bit longer here

allow_location_btn = driver.find_element(By.XPATH, '//*[@id="c160459658"]/main/div/div/div/div[3]/button[1]/div['
                                                   '2]/div[2]')
allow_location_btn.click()

time.sleep(SLEEP_TIME)
disable_notifications_btn = driver.find_element(By.XPATH, '//*[@id="c160459658"]/main/div/div/div/div[3]/button['
                                                          '2]/div[2]/div[2]')
disable_notifications_btn.click()

time.sleep(SLEEP_TIME)
reject_cookies_btn = driver.find_element(By.XPATH, '//*[@id="c-60880778"]/div/div[2]/div/div/div[1]/div['
                                                   '2]/button/div[2]/div[2]')
reject_cookies_btn.click()
