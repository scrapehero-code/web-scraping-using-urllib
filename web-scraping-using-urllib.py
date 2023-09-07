import urllib.request
import urllib.error
import csv
from lxml.html import fromstring

homepage_url = 'http://scrapeme.live/shop/'

headers = {
    'authority': 'scrapeme.live',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.8',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'referer': 'https://www.google.com/',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-user': '?1',
    'sec-gpc': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}


def write_to_csv(first_row, each_product_details):
    with open('product_details.csv', 'a', newline='') as csvfile:
        fieldnames = ['title', 'price', 'description', 'stock', 'SKU', 'product_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not first_row:
            writer.writeheader()
        row = {key: value for key, value in zip(fieldnames, each_product_details)}
        writer.writerow(row)


collected_product_urls = []


def hit_collected_products():
    for index, product_url in enumerate(collected_product_urls):

        response_bytes = get_response_bytes(product_url, headers)
        parser = fromstring(response_bytes)

        product_title_xpath = "//h1[contains(@class,'product_title')]/text()"
        price_xpath = "//p[@class='price']/span/text()"
        description_xpath = "//div[contains(@class,'short-description')]/p/text()"
        stock_xpath = "//p[contains(@class,'stock')]/text()"
        sku_xpath = "//span[@class='sku']/text()"

        each_product_details = []
        for required_xpath in [product_title_xpath, price_xpath, description_xpath, stock_xpath, sku_xpath]:
            data = parser.xpath(required_xpath)
            data = data[0] if data else None
            each_product_details.append(data)
        each_product_details.append(product_url)

        write_to_csv(index, each_product_details)


def get_response_bytes(url, headers):
    for _ in range(3):
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request) as response:
                if response.status != 200:
                    continue
                return response.read()
        except urllib.error.HTTPError as Error:
            print("exception occured:", Error.code)
            continue
    return


def scrape(url, headers):
    response_bytes = get_response_bytes(url, headers)
    if not response_bytes:
        print('scraping failed')
        return

    parser = fromstring(response_bytes)
    product_url_xpath = "//a[contains(@class,'product__link')]/@href"
    product_urls = parser.xpath(product_url_xpath)
    collected_product_urls.extend(product_urls)

    next_page_xpath = "(//a[@class='next page-numbers']/@href)[1]"
    next_page = parser.xpath(next_page_xpath)
    if next_page:
        next_page_url = next_page[0]
        scrape(next_page_url, headers)
        return

    hit_collected_products()
    print('scraping finished successfully')


scrape(homepage_url, headers)
