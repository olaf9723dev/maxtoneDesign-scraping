import os
import json
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
MAIN_URL = 'https://maxtondesign.com/eng_m_Our-Offer-1876.html'
PAGE_URL = 'https://maxtondesign.com/eng_m_Our-Offer-1876.html?counter={}'

class Data_Extractor:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.page_counts = 0
        pass

        try:
            os.mkdir('output')
        except FileExistsError:
            pass
    
    def get_request(self, url):
        response = self.session.get(url)
        return response

    def get_data(self):
        print('Start Getting Data from ------maxtondesign.com------')
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless= False
            )
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            self.page.goto('https://maxtondesign.com/eng_m_Our-Offer-1876.html', timeout=300000)
            self.page.locator('.acceptAll').click()

            self.page_counts = self.page.locator('#paging_setting_top > ul > li:nth-child(10)').text_content()
            print('Got Page Counts : ', self.page_counts , 'pages')
            for page in range(0, int(self.page_counts)-1):
                temp_url = []
    
                # self.page.goto(PAGE_URL.format(page), timeout=300000)
                temp_url = self.get_url(PAGE_URL.format(page))
    
                for url in temp_url:
                    product_id = str(url).split('-')[2]
                    self.get_data_detailpage(url, product_id)

            self.page.wait_for_timeout(100000000)
        except Exception as e:
            print('There is Error : ', e)
            return
    
    def get_url(self, url):

        temp_urls = []
        response = self.get_request(url)
        content = response.text
        
        soup_page= BeautifulSoup(content, 'html.parser')    
        
        for product in soup_page.find_all('div', 'product_wrapper_sub'):
            temp_urls.append(product.find('a')['href'])
        print(temp_urls)

        return temp_urls
    
    def get_data_detailpage(self, url, product_id):
        car_data = dict()
        response = self.get_request(url)
        content = response.text
        
        soup_page= BeautifulSoup(content, 'html.parser')     
        car_data['product_id'] = product_id
        car_data['title'] = soup_page.find(class_="projector_navigation").find('h1').string
        car_data['production_code'] = soup_page.find(class_= 'projector_navigation').find(class_='proj_code').find('strong').string
        # if soup_page.find('div','fake_name') is not None:
        #     car_data['surface'] =  soup_page.find('div','fake_name').string       
        try:
            car_data['production_info'] = soup_page.find(class_='param_informacje_desc').get_text()
        except:
            car_data['production_info'] = ""

        car_data['description'] = soup_page.find(class_='projector_longdescription').get_text()
        
        with open(str.format('output/{}.json', car_data['product_id']), 'w') as f:
            json.dump(car_data, f)

def main():
    extractor =Data_Extractor()
    extractor.get_data()

if __name__ == "__main__":
    main()