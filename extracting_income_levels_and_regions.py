import sqlite3
import urllib.error
import ssl
import json
import time
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.request import urlopen





# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# info for a single country : this gives info like region, adminregion, income level, lending type, and capital city
    # http://api.worldbank.org/v2/country/BRA?format=json

# income level code definitions: a total of 7 = high income, low, lower middle, low and middle, upper middle, and not classified
    # http://api.worldbank.org/v2/incomelevel?format=json

# region codings: a total of 48 regions
    # http://api.worldbank.org/v2/region?format=json

# this guy gives you the second page, all you have to do is loop through every page, so much easier ...
    # http://api.worldbank.org/v2/country?page=2&format=json

# api calls to retrieve income level and region information
urls = ["http://api.worldbank.org/v2/incomelevel?format=json", "http://api.worldbank.org/v2/region?format=json"]
attributes = dict()
# the following dictionaries will help me automate the process of filling in two tables at once since the data is not
# retrieved from the same api call
attributes[urls[0]] = ["id", "value", "IncomeLevel"]
attributes[urls[1]] = ["code", "name", "Region"]


conn = sqlite3.connect('countries.sqlite')
cur = conn.cursor()

# cur.execute('''DROP TABLE IF EXISTS IncomeLevel''')
# cur.execute('''DROP TABLE IF EXISTS Region''')


cur.execute('''CREATE TABLE IF NOT EXISTS IncomeLevel
    (uid INTEGER PRIMARY KEY, id TEXT UNIQUE, value TEXT)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Region
    (id INTEGER PRIMARY KEY, code TEXT UNIQUE, name TEXT)''')


# let us begin by creating a dictionary with each country code as the key, and the population of that country code as the value (in 2018)



for url in urls:
    Retrieved = False
    current_page = 1
    column_1_name = attributes[url][0]
    column_2_name = attributes[url][1]
    table_name = attributes[url][2]

    while not Retrieved:

        # try to connect to the url, then read it.  Handle keyboard interruptions and http error exceptions
        try:
            # connect to the url and create a handle
            document = urlopen(url+'&page='+str(current_page), context=ctx)
            # read the document
            html = document.read()
            # check http status code
            if document.getcode() != 200 :
                print("Error on page: ",document.getcode())
            # print(document.info().get_content_type)

        except KeyboardInterrupt:
            print('')
            print('Program interrupted by user...')
            break

        # if the link did not open, print out the error code given, then restart
        except urllib.error.HTTPError as e:
            print(e.code)
            # print(e.read())
            print("Unable to retrieve or parse page")
            continue

        # if the connection was successful, then load the json data, my assumption is that the json library handles
        # the headers of the html, just like BeautifulSoup does
        json_data = json.loads(html)

        # if the query url does not work, print out the message the api gives you, note, still in json format
        if len(json_data) == 1:
            print(json_data[0]["message"][0]["value"])
            continue

        # print out the json data
        # print(json.dumps(json_data, indent=8))

        # extract the number of pages and the number of total records
        pages = int(json_data[0]["pages"])
        #total_records = json_data[0]["total"]

        for record in json_data[1]:
            column_1 = record[column_1_name]
            column_2 = record[column_2_name]

            # on database syntax, when inserting values in python, you have to use '(?,?)', string.format(insert this) will not work ...
            # insert or ignore did not do its job when the column values where the same, probably because of the unique primary key
            # that is added to each row, making it different ... to fix, add a uniqueness constraint to one of the columns
            cur.execute('INSERT OR IGNORE INTO {} ({}, {}) VALUES (?,?)'.format( table_name, column_1_name, column_2_name) , (column_1, column_2) )


        current_page += 1
        if current_page > pages:
            Retrieved = True


conn.commit()
cur.close()
