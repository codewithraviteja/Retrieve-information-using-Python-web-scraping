import requests
from bs4 import BeautifulSoup
from models import Product
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DiorScraper:
    def __init__(self, country_code):
        self.BASE_URL = f'https://www.dior.com/en_{country_code}'
        self.headers = {
            'authority': 'www.dior.com',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': 'x-is-crawler=false;',
            'purpose': 'prefetch',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        }
        self.PROXIES = {
            'http': 'http://127.0.0.1:24000',
            'https': 'https://127.0.0.1:24000'
        }

    def get_categories(self):
        return [
            ('/fashion/womens-fashion/bags/all-the-bags', 'Women', 'Bags'),
            ('/fashion/womens-fashion/small-leather-goods/all-small-leather-goods', 'Small Leather Goods', 'Women'),
            ('/fashion/womens-fashion/ready-to-wear/all-ready-to-wear', 'Ready To Wear'),
            ('/fashion/womens-fashion/shoes/all-shoes', 'Shoes', 'Women'),
            ('/fashion/womens-fashion/accessories/all-accessories', 'Accessories', 'Women'),
            ('/fashion/womens-fashion/fashion-jewellery/jewellery', 'Jewellery', 'Women'),
            ('/fashion/mens-fashion/bags/all-bags', 'Men', 'Bags'),
            ('/fashion/mens-fashion/small-leather-goods/all-small-leather-goods', 'Small Leather Goods', 'Men'),
            ('/fashion/mens-fashion/ready-to-wear/all-ready-to-wear', 'Ready To Wear', 'Men'),
            ('/fashion/mens-fashion/shoes/all-shoes', 'Shoes', 'Men'),
            ('/fashion/womens-fashion/fashion-jewellery/jewellery', 'Jewellery', 'Men'),
            ('/fashion/baby/newborn/all-products', '', 'New Born'),
            ('/fashion/baby/baby-girls-1-36-months/all-products', '', 'Baby Girl'),
            ('/fashion/baby/baby-boys-1-36-months/all-products', '', 'Baby Boy'),
            ('/fashion/baby/girls/all-products', '', 'Girls'),
            ('/fashion/baby/boys/all-products', '', 'Boys'),
            ('/fashion/maison/collections/all-collections', '', 'Maison Collections'),
            ('/fashion/maison/tableware/all-products', '', 'Maison Art'),
            ('/fashion/maison/objects/all-products', '', 'Maison Objects'),
            ('/fashion/maison/decor/all-products', '', 'Maison Decor'),
            ('/fashion/maison/textile/all-products', '', 'Maison Textile'),

            # ('https://www.dior.com/en_gb/beauty/mens-fragrance', 'Men', 'Fragrance'),
            # ('https://www.dior.com/en_gb/beauty/womens-fragrance', 'Women', 'Fragrance'),
        ]
    
    def get_products(self):
        for category in self.get_categories():
            products = self.get_products_urls(category)
            for product in products:
                yield from self.get_product_info(product, category)
    
    def get_products_urls(self, category):
        links = []
        for i in range(5):
            response = requests.get(self.BASE_URL + category[0], headers=self.headers, proxies=self.PROXIES, verify=False)
            if response.status_code == 200: break
        else: return links
        soup = BeautifulSoup(response.content, 'html.parser')
        products = soup.find_all('li', class_='grid-item')
        for product in products:
            product_id = product['data-object-id']
            if not product_id.startswith('prd'): continue
            product_id = product_id[:-4] + '_' + product_id[-4:]
            links.append(product_id.split('prd-')[-1])
        return links
    
    def get_product_info(self, product_id, category):
        url = 'https://www.dior.com/en_gb/fashion/products/' + product_id
        for i in range(5):
            response = requests.get(url, headers=self.headers, proxies=self.PROXIES, verify=False)
            if response.status_code == 200: break
        else: return
        soup = BeautifulSoup(response.content, 'html.parser')
        for script in soup.find_all('script'):
            if '@type' in script.text and json.loads(script.text)['@type'] == 'Product':
                data = json.loads(script.text)
                break
        NEXT_DATA = json.loads(soup.find('script', id='__NEXT_DATA__').text)

        yield Product(
            name=data['name'],
            sku=data['sku'],
            price=data['offers']['price'] if 'price' in data['offers'] else None,
            currency=data['offers']['priceCurrency'] if 'priceCurrency' in data['offers'] else None,
            images=[x.find('img')['src'] for x in soup.find_all('button', class_='product-media') if x.find('img')],
            description=soup.find('p', class_='multiline-text').text.strip(),
            category=category[2],
            brand='Dior',
            country='UK',
            availability='In Stock' if 'InStock' in data['offers']['availability'] else 'Out of Stock',
            sizes=[NEXT_DATA['props']['pageProps']['__APOLLO_STATE__'][x]['sizeLabel'] for x in NEXT_DATA['props']['pageProps']['__APOLLO_STATE__'] if 'sizeLabel' in NEXT_DATA['props']['pageProps']['__APOLLO_STATE__'][x]],
            available_sizes=[NEXT_DATA['props']['pageProps']['__APOLLO_STATE__'][x]['sizeLabel'] for x in NEXT_DATA['props']['pageProps']['__APOLLO_STATE__'] if 'sizeLabel' in NEXT_DATA['props']['pageProps']['__APOLLO_STATE__'][x] and NEXT_DATA['props']['pageProps']['__APOLLO_STATE__'][x]['status'] == 'AVAILABLE'],
            colors=[],
            gender=category[1],
            url=url
        )