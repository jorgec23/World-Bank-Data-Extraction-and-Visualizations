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


all_countries_url = "http://api.worldbank.org/v2/country?format=json"

# info for a single country : this gives info like region, adminregion, income level, lending type, and capital city
    # http://api.worldbank.org/v2/country/BRA?format=json

# income level code definitions: a total of 7 = high income, low, lower middle, low and middle, upper middle, and not classified
    # http://api.worldbank.org/v2/incomelevel?format=json

# region codings: a total of 48 regions
    # http://api.worldbank.org/v2/region?format=json

# this guy gives you the second page, all you have to do is loop through every page, so much easier ...
    # http://api.worldbank.org/v2/country?page=2&format=json


conn = sqlite3.connect('countries.sqlite')
cur = conn.cursor()

# to restart the table, enable the following line
cur.execute('DROP TABLE IF EXISTS Countries')

# giving the country name a uniqueness constraint is enough because the country name will never be duplicated
cur.execute('''CREATE TABLE IF NOT EXISTS Countries
    (id INTEGER PRIMARY KEY, country_name TEXT UNIQUE, country_code TEXT, iso2code TEXT, income_id TEXT, region_id TEXT)''')

# let us begin by creating a dictionary with each country code as the key, and the population of that country code as the value (in 2018)

Retrieved = False
all_countries = dict()
current_page = 1
first_check = True
total_records = 0
while not Retrieved:
    # ask for the query url only once
    if first_check == True:
        input_url = input("Please enter the World Bank query you would like to make: ")
        if len(input_url)<1:
            input_url = all_countries_url
        first_check = False

    # try to connect to the url, then read it.  Handle keyboard interruptions and http error exceptions
    try:
        # connect to the url and create a handle
        document = urlopen(input_url+'&page='+str(current_page), context=ctx)
        # read the document
        html = document.read()
        # check http status code
        if document.getcode() != 200 :
            print("Error on page: ",document.getcode())
        # print(document.info().get_content_type)
        first_check = False

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

    # if the query url does not work
    if len(json_data) == 1:
        print(json_data[0]["message"][0]["value"])
        continue

    # print out the json data
    # print(json.dumps(json_data, indent=8))

    # extract the number of pages and the number of total records
    pages = json_data[0]["pages"]
    total_records = json_data[0]["total"]

    for record in json_data[1]:
        country_name = record["name"].strip()       # some country names had spaces at the end, so some minor clean up
        country_id = record["id"]
        country_iso_id = record["iso2Code"]

        income_level = record["incomeLevel"]["value"]
        region = record["region"]["value"]
        #print(income_level, region)

        # print(record["name"], record["id"], record["iso2Code"])
        # at the moment, this dictionary is not actually used ...
        all_countries[country_name] = [country_id , country_iso_id]

        try:
            cur.execute('SELECT uid FROM IncomeLevel WHERE value =  (?)', (income_level, ) )
            # ok, fetchone returns 'None', not a tuple with none stored inside, thus row[0] will not work
            # note: the country codes giving me trouble here either had aggretate values for income and region, or
            # no values at all, this gives me a way to filter country codes that are not actually countries!!!
            row_inc = cur.fetchone()
            if row_inc is None:
                income_id = None
            else:
                income_id = row_inc[0]

            cur.execute('SELECT id FROM Region WHERE name =  (?)', (region, ) )
            row_reg = cur.fetchone()
            if row_reg is None:
                region_id = None
            else:
                region_id = row_reg[0]
        except:
            # if you could not access the database at all
            print(json.dumps(record, indent = 8) )
            continue

        cur.execute('''INSERT OR IGNORE INTO Countries (country_name, country_code, iso2code, income_id, region_id)
            VALUES ( ?, ?, ?, ?, ?)''', ( country_name, country_id, country_iso_id, income_id, region_id) )


    current_page += 1
    if current_page > pages:
        Retrieved = True

print("Number of country designations: ", len(all_countries))
conn.commit()
cur.close()
