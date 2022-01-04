import argparse
import requests
from bs4 import BeautifulSoup, Tag
import json
import os
import platform
import re
import time

url = 'https://www.facebook.com/marketplace/111926645500644/search/?minPrice=1000&maxPrice=6000&query=fiat&exact=false'


def run_query(url, name, notify):
    print("running query (\"{}\" - {})...".format(name, url))
    global queries
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    print(soup.prettify())

    testscraper = soup.find_all('span', {'class':'d2edcug0 hpfvmrgz qv66sw1b c1et5uql oi732d6d ik7dh3pa ht8s03o8 a8c37x1j keod5gw0 nxhoafnm aigsh9s9 fe6kdd0r mau55g9w c8b282yb d9wwppkn mdeji52x a5q79mjw g1cxx5fr lrazzd5p oo9gr5id'})
    product_list_items = soup.find_all('div', class_=re.compile(r'item-key-data'))
    msg = []

    for product in product_list_items:
        title = product.find('h2').string

        try:
            price =product.find('p' ,class_=re.compile(r'price')).contents[0]
            # check if the span tag exists
            price_soup = BeautifulSoup(price, 'html.parser')
            if type(price_soup) == Tag:
                continue
            # at the moment (20.5.2021) the price is under the 'p' tag with 'span' inside if shipping available

        except:
            price = "Unknown price"
        link = product.parent.parent.parent.parent.get('href')

        location = product.find('span' ,re.compile(r'town')).string + product.find('span' ,re.compile(r'city')).string


        if not queries.get(name):   # insert the new search
            queries[name] = {url: {link: {'title': title, 'price': price, 'location': location}}}
            print("\nNew search added:", name)
            print("Adding result:", title, "-", price, "-", location)
        else:   # add search results to dictionary
            if not queries.get(name).get(url).get(link):   # found a new element
                tmp = "New element found for  " + name +":  " + title +" @  " + price +" -  " +location +" -->  " +link +'\n'
                msg.append(tmp)
                queries[name][url][link] = {'title': title, 'price': price, 'location': location}

    # if len(msg) > 0:
    #     if notify:
    #         # Windows only: send notification
    #         if not args.win_notifyoff and platform.system() == "Windows":
    #             global toaster
    #             toaster.show_toast("New announcements", "Query: " + name)
    #         if is_telegram_active():
    #             send_telegram_messages(msg)
    #         print("\n".join(msg))
    #         print('\n{} new elements have been found.'.format(len(msg)))
    #     save_queries()
    # else:
    #     print('\nAll lists are already up to date.')
    # print("queries file saved: ", queries)


run_query(url, 'fiat', True)
