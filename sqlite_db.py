import sqlite3
# from subito_searcher import Searches
import subito_searcher

class Searches():
    def __init__(self, active, name, min_price, max_price, area,
                 category, keywords, keywords_exclude, only_in_title, website):
        self.active = active
        self.name = name
        self.min_price = min_price
        self.max_price = max_price
        self.area = area
        self.category = category
        self.keywords = keywords
        self.keywords_exclude = keywords_exclude
        self.only_in_title = only_in_title
        self.website = website

conn = sqlite3.connect('searches.db')
c = conn.cursor()


def insert_search(search):
    with conn:
        c.execute('''INSERT INTO searches VALUES(:active, :name, :min_price, :max_price, :area,
                 :category, :keywords, :keywords_exclude, :only_in_title, :website)''',
                  {
                      'active': search.active,
                      'name':search.name,
                      'min_price':search.min_price,
                      'max_price': search.max_price,
                      'area': search.area,
                      'category':search.category,
                      'keywords': search.keywords,
                      'keywords_exclude': search.keywords_exclude,
                      'only_in_title': search.only_in_title,
                      'website': search.website
                  })




# c.execute("""CREATE TABLE searches (
#     id INTEGER PRIMARY KEY,
#     active integer,
#     search_name text,
#     min_price integer,
#     max_price integer,
#     search_area text,
#     category text,
#     keywords text,
#     keywords_exclude text,
#     only_in_title integer,
#     website text
#     )""")
#
# conn.commit()
#
# c.execute("""CREATE TABLE results (
#     id INTEGER PRIMARY KEY,
#     search_id integer,
#     area text,
#     url text,
#       FOREIGN KEY(search_id) REFERENCES searches(id)
#     )""")
#
# conn.commit()

# c.execute("""INSERT INTO searches VALUES (1, 'ramponi', 0, 30, 'RE', 'Sport', 'ramponi', '', 0, 'S')""")

# c.execute('''SELECT * FROM searches''')

# print(c.fetchone())


conn.commit()
conn.close()