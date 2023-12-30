from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By 
from selenium import webdriver
from bs4 import BeautifulSoup
from pprint import pprint
import json
from time import sleep

clikable_links = 'body > div:nth-child(21) > div.container > div.row > div > div > div.ibox-content > table > tbody > tr > td:nth-child(2) > a'
table_name = '#ngo_name_title'
members_table = '#member_table'
key_issue = '#printThis > div > div > table:nth-child(8) > tbody > tr:nth-child(1) > td:nth-child(2)'
contacts_table = '#printThis > div > div > table:nth-child(16)'


def get_contacts(page_soup):
	table = page_soup.select(contacts_table)[0]
	table_obj = {}
	for row in table.select('tbody > tr'):
		data = row.select('td')
		key = data[0].get_text(strip=True)
		val = data[1].get_text(strip=True)
		table_obj[key] = val

	return table_obj

def get_members(page_soup):
	table = page_soup.select(members_table)[0]
	headers = [x.get_text(strip=True) for x in table.select('tbody > tr > th')]
	table_obj = {x:[] for x in headers}
	for row in table.select('tbody>tr')[1:]:
		all_td = row.select('td')
		for header,td in zip(headers,all_td):
			table_obj[header].append(td.get_text(strip=True))
	
	return table_obj


driver = webdriver.Chrome()
final_data = []

for page_no in range(1,90):
	URL = f'https://ngodarpan.gov.in/index.php/home/statewise_ngo/8865/24/{page_no}?per_page=100'
	driver.get(URL)
	links = driver.find_elements(by=By.CSS_SELECTOR,value=clikable_links)
	ngo_obj = {}
	for link in links:
		link.click()
		sleep(1)
		page_soup = BeautifulSoup(driver.page_source,'html.parser')
		ngo_obj['name'] = page_soup.select(table_name)[0].get_text(strip=True)
		ngo_obj['key_issue'] = page_soup.select(key_issue)[0].get_text(strip=True)
		ngo_obj['contacts'] = get_contacts(page_soup)
		ngo_obj['members'] = get_members(page_soup)
		final_data.append(ngo_obj)
		sleep(1)	
		webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
		sleep(1)

with open('./data.json','w') as f:
	json.dump(final_data,f,indent=4)