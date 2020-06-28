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

conn = sqlite3.connect('countries.sqlite')
cur = conn.cursor()

# to erase the data, enable the next two lines, they will take care of deleting the current table
# and resetting the 'last_updated' year in the 'Indicators' table
# cur.execute('DROP TABLE IF EXISTS AllData')
# cur.execute('UPDATE Indicators SET last_updated = (?)' , (1960, ) )

# create the table if it has not already been created that will hold all of the data
cur.execute('''CREATE TABLE IF NOT EXISTS AllData
        (id INTEGER PRIMARY KEY, country_id INTEGER, indicator_value TEXT, indicator_id INTEGER,
        date INTEGER, UNIQUE(indicator_id, date, country_id) )''')


# retrieve all of the current indicator codes and map them to the last_updated year (from AllData)
# NOTE: There must be indicator codes in the 'Indicators' table for this script to run.
current_indicators = dict()
cur.execute('SELECT indicator, last_updated FROM Indicators')
for row in cur:
    # print(row)
    current_indicators[row[0]] = row[1]



# properly formatted api url call
    # http://api.worldbank.org/v2/country/indicator/SP.POP.TOTL?format=json&date=2019

base_url = 'http://api.worldbank.org/v2/country/indicator/'
# this could take a while with alot of new indicators, so lets add a limit to
# the number of indicators you can update at one time
updated_indicators = 0
# find the latest year data has been found for a single indicator, and set that to the max_date
# this way, the code will check for every year up to that point.  The data can be very sparse so this is a must.
cur.execute('SELECT MAX(date) FROM AllData')
max_date = cur.fetchone()[0]
print("The current maximum date is:", max_date)

total_records = 0
for ind in current_indicators:
    print("Retrieving data for", ind+'.')
    # if the date is set to 1960, the indicator was just added, so start checking from 1960,
    # if the date is anything else, the assumption is that the last_updated column in 'Indicators'
    # has actually been fully updated ... actually, lets not assume that, if you get a timeout error,
    # you definitely have not finished so always start at the 'last_updated' year

    check_date = current_indicators[ind]
    current_page = 1
    new_records = 0
    while True:
        num_updates = 0
        try:
            webpage_handle = urlopen(base_url + ind + '?format=json&date=' + str(check_date)+'&page='+str(current_page) )
            html = webpage_handle.read()
            json_data = json.loads(html)
        except urllib.error.HTTPError as e:
            # if you cannot connect retrieve the page, go on to the next indicator
            print("Unable to retrieve or parse page, please try again.")
            print("Error Code: ", e.code)
            # do something about these guys for sure ... no need, the code takes care of it, the 'last_updated' column will
            # ensure that you come back to this guy when you run this script again, pretty cool tbh...
            print(base_url + ind + '?format=json&date=' + str(check_date)+'&page='+str(current_page) )
            break

        # check to see if there is any new data, this will trigger when the date is too recent and the json_data is note
        # structurally set up yet.  Also note that this break ensures that you check the most recent year with data again.
        if json_data[0]["pages"] == 0:
            cur.execute('UPDATE Indicators SET last_updated = (?) WHERE indicator = (?)' , (check_date-1, ind) )
            print("The data for", ind, "is up to date.")
            break
        else:
            cur.execute('UPDATE Indicators SET last_updated = (?) WHERE indicator = (?)' , (check_date, ind) )

        # if the webpage return properly formatted json, look through it, sometimes you will get all nulls, so skip those
        for record in json_data[1]:
            if record["value"] is None:
                # print(json.dumps(record, indent = 8))
                continue
            else:
                country_name = record["country"]["value"].strip()
                indicator_value = record["value"]
                # if we have actual data, retrieve the foreign keys necessary to populate a row in AllData
                cur.execute('SELECT id FROM Countries WHERE country_name =(?)', (country_name, ) )
                country_id = cur.fetchone()[0]
                cur.execute('SELECT id FROM Indicators WHERE indicator = (?)', (ind, ) )
                indicator_id = cur.fetchone()[0]

                # add the new record to AllData
                cur.execute(''' INSERT OR IGNORE INTO AllData (country_id, indicator_value, indicator_id, date)
                VALUES (?,?,?,?)
                ''', (country_id, indicator_value, indicator_id, check_date) )
                conn.commit()
                num_updates = num_updates + 1

        new_records = new_records + num_updates
        total_records = total_records + num_updates
        # this statement assumes that the world bank will always have the most recent year empty, currently,
        # population data for 2019 is empty for every country, which means you will have to check again later
        # also, because there is a possibility of a timeout error, it is best to update the 'last_updated'
        # column after each year has been succesfully retrieved and not wait until it reaches the
        # most recent empty year that still returns properly formatted JSON

        # if no new data for the current check_date was found, then break the while loop.
        # this loop only works if the only year that is entirely null is the most current year, which
        # presumably has not been filled, the question now is, what to do for indicators that are entirely missing for
        # a certain year ... say 1964 is all empty ... the quick fix is add in a hard coded value for the max year ...
        # or we could look at the highest year found in the database and set that to the max year,
        # if the first three indicators are all empty in 1960, then max = 1960, so you will need some indicator in the 'Indicators'
        # table to eventually give you a year beyond 1960, then, the next time this script is run, the code will be forced to check
        # the following years as well, until it catches up to the current max year.  It is recursive in nature ... next level
        # note that the check_date >= max_date helps ensure that if the current max year has some info, that you check the following year,
        # for updates, if it is structurally set up, the assumption is that all of the current max date data is done being recorded
        # for all indicators ... , if not then I need to patch this up some and set the max date to a year prior ...
        if num_updates < 1 and check_date >= max_date:
            # the following update might not be needed after moving the date update from the if statement that increments the year
            # below, to the if statement that check is the check_date json data has been set up, even with all nulls
            cur.execute('UPDATE Indicators SET last_updated = (?) WHERE indicator = (?)' , (check_date, ind) )
            print("All of the data for",ind , "for", str(check_date), "is currently empty.  Check again later.\n")
            break

        current_page = current_page + 1

        # once you have looped through every page in the current year, move on to the next year
        # and reset the current page, also update the 'Indicators' table column 'last_updated'
        if current_page > json_data[0]["pages"]:
            print(str(check_date) + ", " + str(new_records) + " new records, " + str(total_records) + " total records")
            check_date = check_date + 1
            current_page = 1
            new_records = 0

        # break the while loop if you have retrieved 10,000 total records
        if total_records > 10000:
            break
    # Also break the for loop after retrieving 10,000 total records
    if total_records > 10000:
        print("More than 10,000 records have been retrieved.")
        break

conn.commit()
cur.close()



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
