import logging
import pickle
import time
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class WebDriver:
    school_data = {}

    def __init__(self, data: dict = None):
        self.PATH = "/home/matej/Documents/Projects/RejstrikSkolScraper/chromedriver.exe"
        self.options = Options()
        self.options.add_argument("--headless")
        self.driver = webdriver.Chrome(self.PATH, options=self.options)
        self.data = data
        self.base_url = ''

        self.school_data['schools'] = []

    def save_cookies(self):
        pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))

    def load_cookies(self, driver: webdriver = None):
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie) if driver else self.driver.add_cookie(cookie)

    def select_main_frame(self):
        self.driver.switch_to.frame('mainFrame')

    def fill_data(self):

        if self.data['include_invalid']:
            element = self.driver.find_element_by_id('chBoxNeplatne')
            element.click()
        if self.data['name']:
            element = self.driver.find_element_by_id('ctl02_txt')
            element.text = self.data['name']
        if self.data['place']:
            element = self.driver.find_element_by_id('ctl07_txt')
            element.text = self.data['place']
        if self.data['street']:
            element = self.driver.find_element_by_id('ctl12_txt')
            element.text = self.data['street']
        if self.data['red_izo']:
            element = self.driver.find_element_by_id('ctl17_txt')
            element.value = self.data['red_izo']
        if self.data['ico']:
            element = self.driver.find_element_by_id('ctl22_txt')
            element.text = self.data['ico']
        if self.data['izo']:
            element = self.driver.find_element_by_id('ctl27_txt')
            element.text = self.data['izo']

        if self.data['school_type']:
            element = self.driver.find_element_by_id('cmdSpravniUrad_dD')
            for option in element.find_elements_by_xpath('//select[@id="cmdSpravniUrad_dD"]/option'):
                if option.text == self.data['school_type']:
                    option.click()
                    break

        if self.data['district']:
            element = self.driver.find_element_by_id('ctl39')
            for option in element.find_elements_by_xpath('//select[@id="ctl39"]/option'):
                if option.text == self.data['district']:
                    option.click()
                    break

        if self.data['creator']:
            element = self.driver.find_element_by_id('cmdZrizovatel_dD')
            for option in element.find_elements_by_xpath('//select[@id="cmdZrizovatel_dD"]/option'):
                if option.text == self.data['creator']:
                    option.click()
                    break

        if self.data['head']:
            element = self.driver.find_element_by_id('ctl46_txt')
            for option in element.find_elements_by_xpath('//select[@id="ctl46_txt"]/option'):
                if option.text == self.data['head']:
                    option.click()
                    break

        if self.data['show_field']:
            element = self.driver.find_element_by_id('chBoxZobrazSkryjPanelOboru')
            element.click()

    def submit(self):
        element = self.driver.find_element_by_id('btnVybrat')
        element.click()
        time.sleep(5)

    def get_results_details(self):
        element = self.driver.find_element_by_id('lblPocetZaznamu')
        self.school_data['info'] = element.text

    def scrape_page(self):
        school_elements = self.driver.find_elements_by_tag_name('table')[3::2][:-1]
        for element in school_elements:
            table_data = element.find_elements_by_tag_name('td')
            self.get_school_detail(table_data[8].find_element_by_tag_name('a').get_attribute('href'))

    def get_school_detail(self, path: str):
        driver = webdriver.Chrome(self.PATH, options=self.options)
        url = urljoin(self.base_url, path)
        driver.get(url)
        driver.delete_all_cookies()
        self.load_cookies(driver)
        driver.get(url)
        time.sleep(5)

        result = {}

        result['name'] = driver.find_element_by_id('lblJmenoPravOsoby').text
        result['address'] = driver.find_element_by_id('lblAdresa').text
        result['ico'] = driver.find_element_by_id('lblICO').text
        result['head'] = driver.find_element_by_id('lblReditel').text

        self.school_data['schools'].append(result)

    def scrape(self, url: str):
        self.base_url = url
        try:
            self.driver.get(url)
        except:
            logging.warning('Driver closed unexpectedly')
            self.driver.quit()
            raise

        self.save_cookies()
        self.select_main_frame()

        if self.data:
            self.fill_data()

        self.submit()
        self.get_results_details()
        self.scrape_page()

        button_next = self.driver.find_element_by_id('btnNext2')
        while button_next.is_enabled():
            button_next.click()
            time.sleep(5)
            self.scrape_page()
            button_next = self.driver.find_element_by_id('btnNext2')

        self.driver.quit()
        return self.school_data


if __name__ == '__main__':
    form_data = {
        'include_invalid': None,
        'name': None,
        'place': None,
        'street': None,
        'red_izo': None,
        'ico': None,
        'izo': None,
        'school_type': None,
        'district': None,
        'creator': None,
        'head': None,
        'show_field': None,
    }
    link = 'https://rejstriky.msmt.cz/rejskol/'
    web_driver = WebDriver(form_data)
    print(web_driver.scrape(link))
