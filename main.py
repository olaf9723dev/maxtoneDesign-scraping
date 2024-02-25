import os
import json
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
MAIN_URL = 'https://maxtondesign.com/eng_m_Our-Offer-1876.html'
PAGE_URL = 'https://maxtondesign.com/eng_m_Our-Offer-1876.html?counter={}'

class Data_Extractor:
    def __init__(self):
        self.session = requests.Session()
        self.page_counts = 0

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
            response = self.get_request(MAIN_URL)
            content = response.text
            soup_page= BeautifulSoup(content, 'html.parser')    
            self.page_counts = soup_page.find('ul', 'pagination').find_all('li')[9].get_text()
            
            print('Got Page Counts : ', self.page_counts , 'pages')
            
            for page in range(0, int(self.page_counts)-1):
                print('Started reading Page ', page , '...')

                temp_url = []
                temp_url = self.get_url(PAGE_URL.format(page))

                for url in temp_url:
                    product_id = str(url).split('-')[2]
                    self.get_data_detailpage(url, product_id)

                print('Finished reading Page ', page, '.')            

            self.browser.close()
            print('Finished Getting Data')

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
        
        print('Saving File (', (str.format('{}.json', car_data['product_id'])), ')...')
        with open(str.format('output/{}.json', car_data['product_id']), 'w') as f:
            json.dump(car_data, f)


def main():
    extractor =Data_Extractor()
    extractor.get_data()

if __name__ == "__main__":
    main()