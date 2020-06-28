# This script will take care of creating the tables that contain the following:
    # Categories: Economy, Education, Employment, Population, Income

    # Indicators: This table will contain the indicator strings you want to retreive for each country.
    #             Note that you will have to assign a descriptor to the indicator strings you wish to
    #             to retrieve.

import sqlite3
import urllib.error
import ssl
import json
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.request import urlopen




conn = sqlite3.connect('countries.sqlite')
cur = conn.cursor()

# to reset the databases, enable the next two lines next time you run this script
# cur.execute('DROP TABLE IF EXISTS Categories')
# cur.execute('DROP TABLE IF EXISTS Indicators')


cur.execute('''CREATE TABLE IF NOT EXISTS Categories
    (id INTEGER PRIMARY KEY, category TEXT UNIQUE)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Indicators
    (id INTEGER PRIMARY KEY, indicator TEXT UNIQUE, category_id INTEGER, name TEXT, last_updated INTEGER)''')


# first output the current descriptors and indicators available, could maybe make this a function ...
cur.execute('SELECT category FROM Categories')
try:
    row_check = cur.fetchone()
    if row_check is None:
        print("There are currently no categories listed.")
    else:
        cur.execute('SELECT category FROM Categories')
        print("The current categories are the following: ")
        for row in cur:
            print(row[0])
        print('\n')
except:
    print("Unable to access the database.")

cur.execute('SELECT indicator FROM Indicators')
try:
    row_check = cur.fetchone()
    if row_check is None:
        print("There are currently no indicators listed.")
    else:
        cur.execute('SELECT indicator FROM Indicators')
        print("The current indicators are the following: ")
        for row in cur:
            print(row[0])
        print('\n')
except:
    print("Unable to access the database.")



# now I have to ask for indicators to be added, along with a category.
# add to the indicator table first, if the descriptor table does not have the category attached,
# create a new row for it.  Adding a new indicator guarantees that a new row will be
# added to "Indicators", but not to "Categories"

# for now, you can only add indicators, one at a time, lol ...

base_url = 'http://api.worldbank.org/v2/indicator/'
earliest_year = 1960
# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

while True:
    try:
        indicator = input("Enter the indicator code you want to add: ")
        indicator = indicator.upper()
        # if you hit enter here, exit the loop
        if len(indicator) < 1:
            break
        handle = urlopen(base_url+indicator+'?format=json')
        html = handle.read()
        data = json.loads(html)
        # print(len(data))
        if len(data) != 2:
            print("This is not a valid indicator.  Please try again.")
            continue
        indicator_name = data[1][0]["name"]
        print(indicator_name+'\n')
    except urllib.error.HTTPError as e:
        print(e.code)
        # print(e.read())
        print("Unable to retrieve or parse page, please try again.")
        continue

    # relying on the user to use good category names
    category = input("What category does this indicator belong to?  ")

    # check of the category in 'Categories', add if needed, extract the category id, to be used by 'Indicators'
    cur.execute('INSERT OR IGNORE INTO Categories (category) VALUES (?)', (category,) )
    cur.execute('SELECT id FROM Categories WHERE category = (?)', (category, ))
    row = cur.fetchone()
    cat_id = row[0]

    # insert indicator and category id into 'Indcators'
    cur.execute('INSERT OR IGNORE INTO Indicators (indicator, category_id, name, last_updated) VALUES (?,?,?,?)', (indicator, cat_id, indicator_name,earliest_year) )


# to delete a row, use the following line, you should probably make a function/script
# that handles deleting/changing categories and indicators
# cur.execute('DELETE FROM Indicators WHERE category_id = (?)' , (2, ) )

conn.commit()
cur.close()
