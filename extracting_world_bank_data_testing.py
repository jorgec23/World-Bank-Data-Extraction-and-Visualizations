# this will be the beginning of my attempt at mining data from the US census.

import sqlite3
import urllib.error
import ssl
import json
import time
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.request import urlopen
from bs4 import BeautifulSoup


# My first order of business will be to create a basic heat map of population of each state
# then I will create a heat map of the percentage change in population, it would be cool to make the map have
# two different colors, say blue for growth and red for losses ...

# heat map link
# https://plotly.com/python/choropleth-maps/

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


# learning about different calls
all_countries = "http://api.worldbank.org/v2/country?format=json"

# info for a single country : this gives info like region, adminregion, income level, lending type, and capital city
    # http://api.worldbank.org/v2/country/BRA?format=json

# income level code definitions: a total of 7 = high income, low, lower middle, low and middle, upper middle, and not classified
    # http://api.worldbank.org/v2/incomelevel?format=json

# region codings: a total of 48 regions
    # http://api.worldbank.org/v2/region?format=json

# to apply a filter, for example, to see all of the countries in each income bracket:
    # http://api.worldbank.org/V2/incomeLevel/UMC/country?format=json

# to see all of the countries in a specific region
    # http://api.worldbank.org/v2/region/SAS/country?format=json

# to see the total population of afghanistan over the course of 50 years, note that there is a cap of 50 result per page
# when using json, so you have to use ':' to retrieve the previous entries, perhaps add a recursive call
# to the database, would be hard because not every piece of information is dated...
    # http://api.worldbank.org/v2/country/AF/indicator/SP.POP.TOTL?format=json

    # to retrieve the population during a time range: note that the api will take care of ignoring requested years
    # that do not have information.  Also note that the country id 'AF' and the countryiso3code 'AFG' are treated the same in the search parameters
        # http://api.worldbank.org/v2/country/AF/indicator/SP.POP.TOTL?date=2000:2010&format=json

    # to retrieve the population of every country in 2018, now, the website only
        # http://api.worldbank.org/v2/country/indicator/SP.POP.TOTL?date=2018&format=json

        # to retrieve the population of three countries in 2018: this means that to extract the population of every country,
        # you have to use ';' to combine every country code, use a loop that does this to extract every result, note that
        # the first dictionary in the json file will tell you how many results you need to retrieve, or you can just change the page ... smh
        # NOTE: A maximum of 60 indicators can be used. A maximum of 1,500 characters are allowed between two back-slashes (/).
        # A maximum of 4,000 characters are allowed in the entire URL.

            # http://api.worldbank.org/v2/country/AF;AL;DZ/indicator/SP.POP.TOTL?date=2018&format=json
            # http://api.worldbank.org/v2/country?page=2&format=json                                    # this guy gives you the second page, all you have to do is loop through every page, so much easier ...


# to see all of the indicators available: a total of 17447 indicators ... jesus ...
    # http://api.worldbank.org/v2/indicator?format=json

# to see all of the topics identified by the world bank: a total of 21
    # http://api.worldbank.org/v2/topic?format=json

    # each topic has a set of indicators that belong to it, for example, the topic of trade has 152 indicators associated with it
        # http://api.worldbank.org/v2/topic/21/indicator?format=json

# to see the sources of the data:
    # http://api.worldbank.org/v2/sources>format=json

    # to search within a source of information, through all of the variables that contain your search string
    # the way the search is split up is it categorizes based on source id, then concept id, then on variable id,
    # lastly, it looks at the metatype id contents (attributes if you will) to find a match with the provided search string
        # http://api.worldbank.org/v2/sources/2/search/solid%20fuel             note: the '%20' = space
    # or if you just want to search without specifying a source
        # http://api.worldbank.org/v2/search/solid%20fuel




# let us begin by creating a dictionary with each country code as the key, and the population of that country code as the value (in 2018)

Retrieved = True
total_records = 0
start_value = None
stop_value = None
tot_population = dict()
while Retrieved:
    input_url = input("Please enter the World Bank query you would like to make: ")
    if len(input_url)<1:
        input_url = 'http://api.worldbank.org/v2/country/indicator/SP.POP.TOTL?date=2018&format=json'

    try:
        # connect to the url and create a handle
        document = urlopen(input_url, context=ctx)
        # read the document
        html = document.read()

        # check http status code
        if document.getcode() != 200 :
            print("Error on page: ",document.getcode())

        # out of curiousity
        # print(document.info().get_content_type)


    # if the user tries to interrupt the program with the keyboard, ctrl-c, then you handle the exception
    # and stop running the program
    except KeyboardInterrupt:
        print('')
        print('Program interrupted by user...')
        break

    # if the link did not open, then try again
    except urllib.error.HTTPError as e:
        # this code is giving me a 403 error, forbidden access, so ... I either ditch the idea of using datausa.io,
        # or I make the queries through the web browser, and then export the data as a csv/json file ... how annoying

        print(e.code)
        # print(e.read())
        print("Unable to retrieve or parse page")
        continue

    json_data = json.loads(html)

    if len(json_data) == 1:
        print(json_data[0]["message"][0]["value"])
        continue

    # print(json.dumps(json_data, indent=8))

    print(len(json_data[1]))

    pages = json_data[0]["pages"]
    total_records = json_data[0]["total"]

    Retrieved = False
