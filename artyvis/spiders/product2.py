# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest

class ProductsSpider(scrapy.Spider):
    name = 'product'
    
    def start_requests(self):
        # this function will go through all the top level titles such as dresses, shorts , jumpsuits etc
        url = 'https://in.seamsfriendly.com/collections/title?page=1'
        titles = ['dresses','jumpsuits','topwear','pants','skirts','shorts','outerwear']
        links = list(map(lambda x:url.replace('title',x),titles))

        for num,link in enumerate(links):
            yield SplashRequest(link, callback = self.parse,endpoint='render.html',dont_filter=True,meta={'title':titles[num]})

    def parse(self,response): 
        # this function will go through all the products in the top level items 
        title = response.meta.get('title') 
        products = response.xpath('//div[@class="ProductItem__Wrapper"]/a/@href').extract()

        for product in products:
            product_full = response.urljoin(product)
            yield SplashRequest(product_full, callback = self.product_page,endpoint='render.html',dont_filter=True,meta={'title':title})

        if response.xpath('//div[@class="ProductItem__Wrapper"]/a/@href') != []: # to check if we are at last page
            link = response.url
            yield SplashRequest(link.split('=')[0]+'='+str(int(link.split('=')[-1])+1), callback = self.parse,endpoint='render.html',dont_filter=True,meta={'title':title})   

    def product_page(self,response):
        # this function is to collect all the details of the products 
        title = response.meta.get('title')
        
        try:
            description = response.xpath('//h1[@class="ProductMeta__Title Heading u-h2"]/text()').extract_first().strip()
        except:
            description = 'No description'

        price = response.xpath('//span[@class="ProductMeta__Price Price  u-h4"]/text()').extract_first()
        colors = response.xpath('//ul[@class="swatch-view swatch-view-custom-image"]/li/@orig-value').extract()

        try:
            image_urls = response.xpath('//div/a[@data-offset="-25"]/img/@src').extract()

            # to convert urls from '//cdn.shopify.com/s/files/1/0534/2501/2925/products/blue-dabu-print-button-down-jumpsuit-button-down-jumpsuit-189169_160x.jpg?v=1625844180'
            # to 
            # this 'cdn.shopify.com/s/files/1/0534/2501/2925/products/blue-dabu-print-button-down-jumpsuit-button-down-jumpsuit-189169_1600x.jpg'
            image_urls = list(map(lambda x:x[2:].split('?')[0].replace('160','1600'),image_urls))

        except:
            image_urls = 'No image urls'

        yield{
            'title': title,
            'Description': description,
            'Price': price,
            'Colors': colors,
            'Image Urls': image_urls,
            'Link':response.url
        }