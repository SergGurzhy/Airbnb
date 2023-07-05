from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def main(event, context):
    options = Options()
    options.binary_location = '/opt/headless-chromium'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')
    s = Service('/opt/Chrome-driver')
    driver = webdriver.Chrome(options=options, service=s)

    driver.get('https://www.google.com/')
    title = driver.title

    driver.close()
    driver.quit()

    response = {
        "statusCode": 200,
        "body": title
    }
    print(title)
    return response

