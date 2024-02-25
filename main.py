import os
import requests
import csv
import shutil
from bs4 import BeautifulSoup

SITE_URL = 'https://maxtondesign.com{}'
MAIN_URL = 'https://maxtondesign.com/eng_m_Our-Offer-1876.html'
PAGE_URL = 'https://maxtondesign.com/eng_m_Our-Offer-1876.html?counter={}'

class Data_Extractor:
    def __init__(self):
        self.session = requests.Session()
        self.page_counts = 0
        self.json_list = []
        try:
            os.mkdir('output')
            with open('output/result.csv', 'w') as file:
                file.write("")
        except FileExistsError:
            pass
    
    def get_request(self, url, stream_v):
        try:
            if stream_v == False:
                response = self.session.get(url)
            else:
                response = self.session.get(url, stream=stream_v)
            return response
        except Exception as e:
            print(e)
            pass
    # def export_data_csv(self):
    #     data_list = []
    #     data_list = self.json_list
    #     with open('output/result.csv', 'w', newline='', encoding='utf-8') as csvfile:
    #         writer = csv.DictWriter(csvfile, fieldnames=data_list[0].keys())
    #         writer.writeheader()
    #         for row in data_list:
    #             writer.writerow(row)

    def get_data(self):
        print('Start Getting Data from ------maxtondesign.com------')
        try:
            response = self.get_request(MAIN_URL, stream_v=False)
            content = response.text
            soup_page= BeautifulSoup(content, 'html.parser')    
            self.page_counts = soup_page.find('ul', 'pagination').find_all('li')[9].get_text()
            
            print('Got Page Counts : ', self.page_counts , 'pages')
            for page in range(0, int(self.page_counts)):
                print('Started reading Page ', page , '...')
                temp_url = []
                temp_url = self.get_url(PAGE_URL.format(page))
                for url in temp_url:
                    product_id = str(url).split('-')[2]
                    self.get_data_detailpage(url, product_id)
                print('Finished reading Page ', page, '.')   
            print('Finished Getting Data')
        except Exception as e:
            print('There is Error : ', e)
            return
    
    def get_url(self, url):
        temp_urls = []
        
        response = self.get_request(url, stream_v=False)
        content = response.text
        
        soup_page= BeautifulSoup(content, 'html.parser')    
        for product in soup_page.find_all('div', 'product_wrapper_sub'):
            temp_urls.append(product.find('a')['href'])

        return temp_urls
    
    def get_data_detailpage(self, url, product_id):
        try:
            car_data = dict()
            response = self.get_request(url,stream_v=False)
            content = response.text
            
            soup_page= BeautifulSoup(content, 'html.parser')     
            car_data['product_id'] = product_id
            car_data['title'] = soup_page.find(class_="projector_navigation").find('h1').string
            car_data['production_code'] = soup_page.find(class_= 'projector_navigation').find(class_='proj_code').find('strong').string
            car_data['surface']=""
            items = soup_page.find('div', 'product_info').find_all()
            for item in items:
                if "Surface" in str(item.get_text()):
                    parent_item = item.parent
                    for img_tag in parent_item.find_all('img'):
                        img_tag['src'] = SITE_URL.format(img_tag['src'])
                    car_data['surface'] = parent_item.prettify()
            try:
                car_data['production_info'] = soup_page.find(class_='param_informacje_desc').get_text()
            except:
                car_data['production_info'] = ""
            car_data['description'] = soup_page.find(class_='projector_longdescription').prettify()

            print('Added the ', car_data['product_id'],' to Excel File...')
            
            with open('output/result.csv', 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=car_data.keys())
                if csvfile.tell() == 0:
                    writer.writeheader()
                writer.writerow(car_data)
        except Exception as e:
            print('Accour error in  : ', product_id ," : ", e)
            pass

def main():
    extractor =Data_Extractor()
    extractor.get_data()
    print('Finished.')

if __name__ == "__main__":
    main()