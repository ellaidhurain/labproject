from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


def si_active(str):
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Remote(
        command_executor="http://20.40.10.43:4444",
        options=chrome_options,
        keep_alive=False,
    )
    driver.get(
        "https://www.startupindia.gov.in/content/sih/en/startupgov/validate-startup-recognition.html"
    )
    radio = WebDriverWait(driver, timeout=60).until(
        lambda d: d.find_element(By.ID, "RECOGNITION")
    )
    radio = driver.find_element(By.ID, "RECOGNITION")
    radio.click()

    elem = driver.find_element(By.NAME, "entname")
    elem.clear()
    elem.send_keys(str)
    elem.send_keys(Keys.PAGE_DOWN)

    submit = driver.find_element(By.NAME, "validateRecognitionCertificate")
    timeout = time.time() + 5
    while time.time() < timeout:
        continue

    submit.click()

    elem = driver.find_element(By.NAME, "viewRecognitionCertificate")
    is_displayed = elem.is_displayed()
    timeout = time.time() + 30
    while not is_displayed:
        elem = driver.find_element(By.NAME, "viewRecognitionCertificate")
        is_displayed = elem.is_displayed()
        pdflink = elem.get_attribute("pdflink")
        if pdflink and "download" in pdflink:
            return True

        elem = driver.find_element(By.CLASS_NAME, "validateStartupRecognition")
        driver.quit()
        if "No record found" in elem.text:
            return False
        if time.time() > timeout:
            return False
