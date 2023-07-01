import json
import time
import requests
from selenium.common import WebDriverException, NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from retry import retry
import os
from web_driver_factory import get_driver
import boto3


URL = r'https://www.airbnb.com/rooms/49618152?source_impression_id=p3_1687811285_G%2FolX9F31QF8p63U'
URL_2 = r'https://www.airbnb.com/rooms/726845935107239384?check_in=2023-07-05&check_out=2023-07-06&source_impression_id=p3_1687819777_BqNCRUgSPbNKcVUA&previous_page_section_name=1000&federated_search_id=59ba7a88-e9b2-424c-a79d-46562440ed81'
URL_3 = r'https://www.airbnb.com/rooms/50717920?check_in=2023-07-05&check_out=2023-07-06&source_impression_id=p3_1687819777_4oY1v%2FgWcVxfJrHp&previous_page_section_name=1000&federated_search_id=59ba7a88-e9b2-424c-a79d-46562440ed81'


POPUP_MODAL = (By.CSS_SELECTOR, '[data-testid="translation-announce-modal"]')
BUTTON_SHOW_PHOTO = (By.CLASS_NAME, "_uhxsfg")
BLOCK_PHOTOS_VISIBLE = (By.CSS_SELECTOR, '[data-testid="photo-viewer-section"]')

FOLDER = False


def _waiter_element_visible(driver: WebDriver, locator: tuple[str, str], time_out: int = 3) -> bool:
    try:
        element = EC.visibility_of_element_located(locator)
        WebDriverWait(driver, time_out).until(element)
        return True
    except TimeoutException:
        return False


def _waiter_element_clickable(driver: WebDriver, locator: tuple[str, str]) -> None:
    element = EC.element_to_be_clickable(locator)
    WebDriverWait(driver, 10).until(element)


@retry(NoSuchElementException, tries=3, delay=1)
def _get_main_description(driver: WebDriver) -> str:
    return driver.find_element(By.CSS_SELECTOR,
                               '[data-section-id="DESCRIPTION_DEFAULT"]').text.strip()


def get_info_from_url(driver: WebDriver, url: str) -> dict:

    driver.get(url)

    # We wait Modal
    translate_modal = _waiter_element_visible(driver=driver, locator=POPUP_MODAL)
    if translate_modal:
        # Close Modal window
        driver.find_elements(By.CSS_SELECTOR, '[role="dialog"]')[-1].find_element(By.TAG_NAME, 'svg').click()

    # Wait Button 'Show photo' clickable
    _waiter_element_clickable(driver=driver, locator=BUTTON_SHOW_PHOTO)

    # Get Description Location
    result = {'title': driver.find_element(By.TAG_NAME, 'h1').text.strip(),
              'description': _get_main_description(driver=driver),
              'url': url,
              }
    # Click on button 'Show photo
    driver.find_element(By.CLASS_NAME, '_uhxsfg').click()

    # Wait block photos visible
    _waiter_element_visible(driver=driver, locator=BLOCK_PHOTOS_VISIBLE)

    blocks = driver.find_elements(By.XPATH, "//div[contains(@style,'display: grid')]")
    count = 1
    print(f'Количество блоков: {len(blocks)}')
    for block in blocks:
        elements = block.find_elements(By.CLASS_NAME, '_cdo1mj')
        for element in elements:
            try:
                action = ActionChains(driver)
                action.move_to_element(element).perform()
                content = element.find_element(By.TAG_NAME, 'picture').find_element(By.TAG_NAME, 'img')
                key = str(count) + '.jpg'
                img_description = content.get_attribute('alt').strip()
                url = content.get_attribute('src')
                result[key] = [img_description, url]
                count += 1
            except WebDriverException as _ex:
                count += 1
                continue
    driver.close()
    driver.quit()
    return result


def _s3_worker(folder_name: str, file_name: str, data: bytes | dict) -> None:
    global FOLDER
    bucket_name = os.environ['BUCKET'].lower()
    s3 = boto3.resource('s3')
    if not FOLDER:
        s3.Bucket(bucket_name).put_object(Bucket=bucket_name, Key=(folder_name+'/'))
        FOLDER = True
    if isinstance(data, dict):
        data = json.dumps(data)
        content_type = 'application/json'
    else:
        content_type = 'image/jpeg'
    s3.Bucket(bucket_name).put_object(Key=f"{folder_name}/{file_name}", Body=data, ContentType=content_type)


def _create_folder_name(title: str) -> str:
    return title.rstrip('\n').replace(" ", "_")


def _create_folder(folder_name: str) -> str:
    folder_path = os.path.join(os.getcwd(), 'source', folder_name)
    if os.path.exists(folder_path):
        os.rmdir(folder_path)
    os.mkdir(folder_path)

    return folder_path


def _save_description(folder_path: str, data: dict) -> None:
    path = os.path.join(folder_path, 'description.json')
    with open(path, 'w') as fp:
        json.dump(data, fp, ensure_ascii=False)


def _save_image(folder_path: str, file_name: str, data: bytes) -> None:
    path = os.path.join(folder_path, file_name)
    with open(path, 'wb') as file:
        file.write(data)


def download_and_save_img(content: dict[str]) -> dict:
    global folder_path
    folder_name: str = _create_folder_name(title=content['title'])
    env_kind = os.environ.get('SAVE_LOCAL').lower()
    if env_kind == 'true':
        folder_path = _create_folder(folder_name)

    result = {}
    for key, val in content.items():
        if isinstance(val, list):
            url = val[1].replace('w=720', 'w=1440')
            response = requests.get(url=url)
            print(f'{url}, Content type : {response.headers["Content-Type"]}')
            file_name = f'{key}'
            # TODO Надо заменить этот параметр
            if 'BUCKET' in os.environ.keys():
                _s3_worker(folder_name=folder_name, file_name=file_name, data=response.content)
            else:
                _save_image(folder_path=folder_path, file_name=file_name, data=response.content)
            result[key] = val[0]
        else:
            result[key] = val
    if os.environ['SAVE_LOCAL'].lower() == 'true':
        _save_description(folder_path=folder_path, data=result)
    else:
        _s3_worker(folder_name=folder_name, file_name='description.json', data=result)

    return result


def main() -> None:
    start = time.time()
    driver = get_driver()
    r = get_info_from_url(driver=driver, url=URL_3)
    print('Количество фоток:', len(r))
    download_and_save_img(content=r)
    print(f'Затраченное время: {time.time() - start}')


if __name__ == '__main__':
    main()
