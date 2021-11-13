#!/usr/bin/env python3.7

import argparse
import requests
from bs4 import BeautifulSoup, Tag
import json
import os
import platform
import re
import time

from replit_keep_alive import replit_keep_alive

replit_keep_alive.keep_alive()


parser = argparse.ArgumentParser()
parser.add_argument("--add", dest='name', help="name of new tracking to be added")
parser.add_argument("--url", help="url for your new tracking's search query")
parser.add_argument("--delete", help="name of the search you want to delete")
parser.add_argument('--refresh', '-r', dest='refresh', action='store_true', help="refresh search results once")
parser.set_defaults(refresh=False)
parser.add_argument('--daemon', '-d', dest='daemon', action='store_true', help="keep refreshing search results forever (default delay 120 seconds)")
parser.set_defaults(daemon=False)
parser.add_argument('--delay', dest='delay', help="delay for the daemon option (in seconds)")
parser.set_defaults(delay=120)
parser.add_argument('--list', dest='list', action='store_true', help="print a list of current trackings")
parser.set_defaults(list=False)
parser.add_argument('--short_list', dest='short_list', action='store_true', help="print a more compact list")
parser.set_defaults(short_list=False)
parser.add_argument('--tgoff', dest='tgoff', action='store_true', help="turn off telegram messages")
parser.set_defaults(tgoff=False)
parser.add_argument('--notifyoff', dest='win_notifyoff', action='store_true', help="turn off windows notifications")
parser.set_defaults(win_notifyoff=False)
parser.add_argument('--addtoken', dest='token', help="telegram setup: add bot API token")
parser.add_argument('--addchatid', dest='chatid', help="telegram setup: add bot chat id")
#my parsers
parser.add_argument("--only_with_price", dest='only_with_price', help="show ads without price: default True")
parser.set_defaults(only_with_price=True)
parser.add_argument("--min_price", dest='min_price', help="min price for captured ads; default 0")
parser.set_defaults(min_price=0)
parser.add_argument("--max_price", dest='max_price', help="max price for captured ads; default 10.000")
parser.set_defaults(min_price=10000)
parser.add_argument("--location", dest='location', help="ads geographical location")
parser.set_defaults(location='Reggio Emilia')
parser.add_argument("--keyword_in_title", dest='keyword_in_title', help="show only ads with keyword in the title: default False")
parser.set_defaults(keyword_in_title=False)
parser.add_argument("--first_notify", dest='first_notify', help="notifies all results upon first search: default False")
parser.set_defaults(first_notify=False)


args = parser.parse_args()

queries = dict()
apiCredentials = dict()
dbFile = "searches.tracked"
telegramApiFile = "telegram_api_credentials"

#other settings
min_price = None
max_price = None

# Windows notifications
if platform.system() == "Windows":
    from win10toast import ToastNotifier
    toaster = ToastNotifier()

# load queries from db file
def load_queries():
    global queries
    global dbFile
    if not os.path.isfile(dbFile):
        return

    with open(dbFile) as file:
        queries = json.load(file)

def load_api_credentials():
    global apiCredentials
    global telegramApiFile
    if not os.path.isfile(telegramApiFile):
        return

    with open(telegramApiFile) as file:
        apiCredentials = json.load(file)

def print_queries():
    global queries
    # print(queries, "\n\n")
    for search in queries.items():
        print("\nsearch: ", search[0])
        for query_url in search[1]:
            print("query url:", query_url)
            for url in search[1].items():
                for result in url[1].items():
                    print("\n", result[1].get('title'), ":", result[1].get('price'), "-->", result[1].get('location'))
                    print(" ", result[0])

# printing a compact list of trackings
def print_sitrep():
    global queries
    i = 1
    for search in queries.items():
        print('\n{}) search: {}'.format(i, search[0]))
        for query_url in search[1]:
            print("query url:", query_url)
        i+=1

def refresh(notify):
    global queries

    #todo cancellare, controllo la struttura dati
    # items = list(queries.items())
    # for i in items:
    #     print(i)

    try:
        for search in queries.items():

            # todo cancellare controllo struttura dati
            print(type(search[1]))
            print(search[1])

            for query_url in search[1]:

                #todo cancellare controllo struttura dati
                print(type(query_url))
                print()

                run_query(query_url, search[0], notify)
    except requests.exceptions.ConnectionError:
        print("***Connection error***")
    except requests.exceptions.Timeout:
        print("***Server timeout error***")
    except requests.exceptions.HTTPError:
        print("***HTTP error***")


def delete(toDelete):
    global queries
    queries.pop(toDelete)

def run_query(url, name, notify):
    print("running query (\"{}\" - {})...".format(name, url))
    global queries
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
        
    product_list_items = soup.find_all('div', class_=re.compile(r'item-key-data'))
    msg = []

    for product in product_list_items:
        title = product.find('h2').string
                
        try:
            price=product.find('p',class_=re.compile(r'price')).contents[0]
            # check if the span tag exists
            price_soup = BeautifulSoup(price, 'html.parser')
            if type(price_soup) == Tag:
                continue
            #at the moment (20.5.2021) the price is under the 'p' tag with 'span' inside if shipping available

        except:
            price = "Unknown price"
        link = product.parent.parent.parent.parent.get('href') 

        location = product.find('span',re.compile(r'town')).string + product.find('span',re.compile(r'city')).string


        if not queries.get(name):   # insert the new search
            queries[name] = {url: {link: {'title': title, 'price': price, 'location': location}}}
            print("\nNew search added:", name)
            print("Adding result:", title, "-", price, "-", location)
        else:   # add search results to dictionary
            if not queries.get(name).get(url).get(link):   # found a new element
                tmp = "New element found for "+name+": "+title+" @ "+price+" - "+location+" --> "+link+'\n'
                msg.append(tmp)
                queries[name][url][link] = {'title': title, 'price': price, 'location': location}

    if len(msg) > 0:
        if notify:
            # Windows only: send notification
            if not args.win_notifyoff and platform.system() == "Windows":
                global toaster
                toaster.show_toast("New announcements", "Query: " + name)
            if is_telegram_active():
                send_telegram_messages(msg)
            print("\n".join(msg))
            print('\n{} new elements have been found.'.format(len(msg)))
        save_queries()
    else:
        print('\nAll lists are already up to date.')
    # print("queries file saved: ", queries)


def save_queries():
    with open(dbFile, 'w') as file:
        file.write(json.dumps(queries, indent=4))

def save_api_credentials():
    with open(telegramApiFile, 'w') as file:
        file.write(json.dumps(apiCredentials))

def is_telegram_active():
    return not args.tgoff and "chatid" in apiCredentials and "token" in apiCredentials

def send_telegram_messages(messages):
    for msg in messages:
        request_url = "https://api.telegram.org/bot" + apiCredentials["token"] + "/sendMessage?chat_id=" + apiCredentials["chatid"] + "&text=" + msg
        requests.get(request_url)

#MAIN
if __name__ == '__main__':

    ### Setup commands ###
    load_queries()
    load_api_credentials()
    if args.list:
        print("printing current status...")
        print_queries()
    if args.short_list:
        print('printing quick sitrep...')
        print_sitrep()
    if args.url is not None and args.name is not None:
        run_query(args.url, args.name, False)
        print("Query added.")
    if args.delete is not None:
        delete(args.delete)

    # Telegram setup
    if args.token is not None and args.chatid is not None:
        apiCredentials["token"] = args.token
        apiCredentials["chatid"] = args.chatid
        save_api_credentials()

    ### Run commands ###
    if args.refresh:
        refresh(True)

    print()
    save_queries()

    # first_notify = args.first_notify
    if args.daemon:
        # notify = args.first_notify
        notify = False # Don't flood with notifications the first time
        while True:
            refresh(notify)
            notify = True
            print()
            print(str(args.delay) + " seconds to next poll.")
            save_queries()
            time.sleep(int(args.delay))
