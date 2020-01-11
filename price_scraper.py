import requests
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from product import Product

URL = "http://www.amazon.fr/"
NOMBRE_DE_PAGE_A_VERIFIER = 3

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome("/Users/idan/chromedriver", chrome_options=options)

search_term = input("Que voulez vous chercher ? ")

driver.get(URL)
element = driver.find_element_by_xpath('//*[@id="twotabsearchtextbox"]')
element.send_keys(search_term)
element.send_keys(Keys.ENTER)

products = []


def convert_price_toNumber(price):
    tuple_price = price.split("\n")
    if len(tuple_price) == 1:
        new_price = float(tuple_price[0].split("€")[0].replace(",", "."))
        return new_price, new_price
    else:
        new_price = float(tuple_price[0].split("€")[0].replace(",", "."))
        prev_price = float(tuple_price[1].split("€")[0].replace(",", "."))

        return new_price, prev_price


def findBestDiscount(products):
    biggest_discount = 0.0
    lowest_price = 0.0
    chepest_product = Product("", "", "", "")
    best_deal_product = Product("", "", "", "")
    search_terms = search_term.split(" ")
    run = 0

    for product in products:
        if run == 0:
            lowest_price = product.price
            chepest_product = product
            run = 1
        elif product.price < lowest_price:
            lowest_price = product.price
            chepest_product = product
        discount = product.prev_price - product.price
        if discount > biggest_discount:
            biggest_discount = discount
            best_deal_product = product
    return chepest_product, best_deal_product


def writeResultOnJSON(products):
    with open('products.json', 'w') as json_file:
        data = {}
        data["Products"] = []
        for prod in products:
            data["Products"].append(prod.serialize())
        json.dump(data, json_file, sort_keys=True, indent=4)


def openTheDeal(best_deal_product):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome("/Users/idan/chromedriver", chrome_options=options)
    driver.get(best_deal_product.link)
    driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')




page = 1
while True:
    if page != 1:
        try:
            driver.get(driver.current_url + "&page=" + str(page))
        except:
            break

    counter_name = 0
    counter_price = 0
    should_add = True
    name = ""
    price = ""
    prev_price = ""
    link = ""

    element_page = driver.find_elements_by_xpath('//*[@id="search"]/div[1]/div[2]/div/span[4]/div[1]')[0]
    while True:
        try:
            namePath = element_page.find_elements_by_tag_name('h2')[counter_name]
            link = element_page.find_elements_by_xpath('//h2/a')[counter_name].get_attribute("href")

            pricePath = element_page.find_elements_by_xpath('//div/div/div[2]/div[2]/div/div[2]/div[1]/div/div[1]/div/div/a')[counter_price]

            loc_y_name = namePath.location["y"]
            loc_y_price = pricePath.location["y"]

            if loc_y_price - loc_y_name < 100:
                price, prev_price = convert_price_toNumber(pricePath.text)
                product = Product(namePath.text, price, prev_price, link)
                products.append(product)
                counter_price += 1

            counter_name += 1

        except:
            break

    print(str(len(products)) + " produits verifiés")
    page = page + 1
    if page == NOMBRE_DE_PAGE_A_VERIFIER + 1:
        break


chepest_product, best_deal_product = findBestDiscount(products)

print(json.dumps(chepest_product.serialize(), indent=4, sort_keys=True))
print(json.dumps(best_deal_product.serialize(), indent=4, sort_keys=True))
newlist = sorted(products, key=lambda product: product.prev_price - product.price, reverse=True)
writeResultOnJSON(newlist)

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome("/Users/idan/chromedriver", chrome_options=options)
driver.get(newlist[0].link)


driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')