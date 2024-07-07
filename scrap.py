from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as Condition
from selenium.webdriver.support.wait import WebDriverWait as Wait
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import json
import os




link_selector =  '.table-striped > tbody:nth-child(2) > tr'
URL = 'https://ngodarpan.gov.in/index.php/home/statewise_ngo/772/24/{page}?per_page=100'
modal_box =  'div.modal-dialog:nth-child(2) > div:nth-child(1)'

def convert_html_to_json(html_data: str) -> dict:
    soup = BeautifulSoup(html_data, 'html.parser')
    NGO: dict = {}

    NGO['name'] = soup.find(id='ngo_name_title').get_text().strip() 
    NGO['Unique Id of VO/NGO'] = soup.find(id='UniqueID').get_text().strip()
    NGO['Details of Achievements'] = ' '.join(soup.find(id='activities_achieve').get_text().strip().split('\n'))

    reg_details: dict = {}
    NGO['Registration Details'] = reg_details
    table = soup.select_one('table.w3-table-all:nth-child(4)')
    for row in table.select('tbody > tr'):
        key, val = row.select('td')
        reg_details[key.get_text().strip()] = val.get_text().strip()
    
    key_issues: dict = {}
    NGO['Key Issues'] = key_issues
    table = soup.select_one('table.w3-table-all:nth-child(8)')
    for row in table.select('tbody > tr'):
        key, val = row.select('td')
        key_issues[key.get_text().strip()] = val.get_text().strip()

    contect_details: dict = {}
    NGO['Contact Details'] = contect_details
    table = soup.select_one('table.w3-table-all:nth-child(16)')
    for row in table.select('tbody > tr'):
        key, val = row.select('td')
        contect_details[key.get_text().strip()] = val.get_text().strip()

    members: list = [] 
    NGO['Members'] = members
    table = soup.select_one('#member_table')
    headers = [th.get_text().strip() for th in table.select_one('tbody > tr').select('th')]
    for row in table.select('tbody > tr')[1:]:
        member: dict = {}
        for key, val in zip(headers, row.select('td')):
            member[key] = val.get_text().strip() 
        members.append(member)
    
    fcra_details: list = []
    NGO['FCRA details'] = fcra_details
    table = soup.select_one('table.w3-table-all:nth-child(10)')
    headers = [th.get_text().strip() for th in table.select_one('tbody > tr').select('th')]
    for row in table.select('tbody > tr')[1:]:
        fcra_detail: dict = {}
        for key, val in zip(headers, row.select('td')):
            fcra_detail[key] = val.get_text().strip() 
        fcra_details.append(fcra_detail)
        
    source_of_funds: list = []
    NGO['Source of Funds'] = source_of_funds
    table = soup.select_one('#source_table')
    headers = [th.get_text().strip() for th in table.select_one('tbody > tr').select('th')]
    for row in table.select('tbody > tr')[1:]:
        source_of_fund: dict = {}
        for key, val in zip(headers, row.select('td')):
            source_of_fund[key] = val.get_text().strip() 
        source_of_funds.append(source_of_fund)

    return NGO


if __name__ == "__main__":
    browser = webdriver.Chrome()
    skipped = []
    os.makedirs('./NGO_DATA')
    i = 1 
    for page_no in range(1, 120+1):
        browser.get(URL.format(page=page_no))
        rows = browser.find_elements(By.CSS_SELECTOR, link_selector)

        for row in rows:
            link = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2) > a')

            isClickable = False
            while not isClickable:
                try:
                    link.click()
                    data_box = Wait(browser, 10).until(Condition.presence_of_element_located((By.CSS_SELECTOR, modal_box))) 
                except (ElementNotInteractableException, ElementClickInterceptedException) :
                    browser.implicitly_wait(1)
                    webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                except TimeoutException:
                    skipped.append(link.text.strip())
                    with open('./skipped.json', 'w') as f:
                        json.dump(skipped, f, indent=4)
                    break
                else:
                    isClickable = True
            else:
                html_data = data_box.get_attribute('innerHTML')
                if html_data is not None:
                    json_data = convert_html_to_json(html_data)
                    webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                    with open(f'./NGO_DATA/file{i}', 'w') as f:
                        json.dump(json_data, f, indent=4)
                    i += 1