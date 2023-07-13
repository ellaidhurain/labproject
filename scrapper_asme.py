from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


def asme_active(str):
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Remote(
        command_executor="http://20.40.10.43:4444",
        options=chrome_options,
        keep_alive=False,
    )
    driver.get("https://caconnect.asme.org/directory/")
    elem = WebDriverWait(driver, timeout=150).until(
        lambda d: d.find_element(By.ID, "company-name")
    )
    elem.clear()
    elem.send_keys(str)
    elem.send_keys(Keys.RETURN)

    elem = WebDriverWait(driver, timeout=60).until(
        lambda d: d.find_element(By.CLASS_NAME, "flex-grid")
    )

    soup = BeautifulSoup(driver.page_source, "html.parser")
    data = []
    table_selector = soup.find("div", class_="flex-grid")
    rows_selector = table_selector.find_all("div", class_="item-row")
    for row in rows_selector:
        divs = row.find_all("div")
        r = []
        for div in divs:
            text = div.get_text()
            r.append(text.strip())
        data.append(r)
    driver.quit()

    for r in data:
        if str in r:
            return True
    return False
