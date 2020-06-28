# Creating visuals of the extracted data from the world bank.
# This script will contain all of the functions used to compare indicator(s) between country(ies).
import matplotlib.pyplot as plt
import sqlite3
import numpy as np


def plot_indicator_countries(cur, country_codes, indicator):
    fig, ax = plt.subplots()
    num_countries = len(country_codes)
    for i in range(num_countries):
        # extract the country id
        cur.execute('SELECT id, country_name FROM Countries WHERE country_code = (?)', (country_codes[i].upper(), ) )
        (country_id, country_name) = cur.fetchone()
        # extract the indicator id and indicator name (title of plot)
        cur.execute('SELECT id, name FROM Indicators WHERE indicator = (?)', (indicator.upper(), ))
        (indicator_id, indicator_name) = cur.fetchone()
        # extract the rows in 'AllData' that correspond to the indicator and country code given
        cur.execute('SELECT indicator_value, date FROM AllData WHERE country_id = (?) AND indicator_id = (?)', (country_id, indicator_id))
        # create a list of the indicator values and dates
        indicator_value = []
        date =[]
        for row in cur:
            # note that the indicator values where stored as text, so cast to float because most of the percentages come in decimal form
            indicator_value.append(float(row[0]))
            date.append(row[1])
        ax.plot(date, indicator_value, 'o', label = country_codes[i])
        ax.legend(frameon = True)
        ax.set(xlabel = 'year', ylabel = indicator_name, title = indicator + ' for ' + country_name)
        ax.xaxis.set_major_locator(plt.MaxNLocator(5))
        ax.yaxis.set_major_locator(plt.MaxNLocator(10))
    plt.show()



def plot_indicators_country(cur, country_code, indicators):
    num_indicators = len(indicators)
    base_dim = int(np.floor(np.sqrt(num_indicators)))
    if base_dim * (base_dim + 1) > num_indicators:
        rows = base_dim
        columns = base_dim + 1
    else:
        rows = base_dim + 1
        columns = base_dim + 1

    fig, ax = plt.subplots(rows, columns)
    for j in range(num_indicators):
        # extract the country id
        cur.execute('SELECT id, country_name FROM Countries WHERE country_code = (?)', (country_code.upper(), ) )
        (country_id, country_name) = cur.fetchone()
        # extract the indicator id and indicator name (title of plot)
        cur.execute('SELECT id, name FROM Indicators WHERE indicator = (?)', (indicators[j].upper(), ))
        (indicator_id, indicator_name) = cur.fetchone()
        # extract the rows in 'AllData' that correspond to the indicator and country code given
        cur.execute('SELECT indicator_value, date FROM AllData WHERE country_id = (?) AND indicator_id = (?)', (country_id, indicator_id))

        # create a list of the indicator values and dates
        indicator_value = []
        date =[]
        for row in cur:
            # note that the indicator values where stored as text, so cast to float because most of the percentages come in decimal form
            indicator_value.append(float(row[0]))
            date.append(row[1])

        index = j+1
        ax_current = plt.subplot(rows, columns, index)        # calling 'subplot' creates an axis handle that you can use directly
        plt.plot(date, indicator_value, label = country_code)
        ax_current.legend(frameon = True)
        ax_current.set(xlabel = 'year', ylabel = indicator_name, title = indicators[j] + ' for ' + country_name)
        ax_current.xaxis.set_major_locator(plt.MaxNLocator(5))
        ax_current.yaxis.set_major_locator(plt.MaxNLocator(10))
    plt.show()


def plot_indicators_countries(cur, country_codes, indicators):
    num_countries = len(country_codes)
    num_indicators = len(indicators)
    rows = num_indicators
    columns = num_countries
    fig, ax = plt.subplots(rows, columns)
    for i in range(num_indicators):
        for j in range(num_countries):
            # extract the country id
            cur.execute('SELECT id, country_name FROM Countries WHERE country_code = (?)', (country_codes[j].upper(), ) )
            (country_id, country_name) = cur.fetchone()
            # extract the indicator id and indicator name (title of plot)
            cur.execute('SELECT id, name FROM Indicators WHERE indicator = (?)', (indicators[i].upper(), ))
            (indicator_id, indicator_name) = cur.fetchone()
            # extract the rows in 'AllData' that correspond to the indicator and country code given
            cur.execute('SELECT indicator_value, date FROM AllData WHERE country_id = (?) AND indicator_id = (?)', (country_id, indicator_id))

            # create a list of the indicator values and dates
            indicator_value = []
            date =[]
            for row in cur:
                # note that the indicator values where stored as text, so cast to float because most of the percentages come in decimal form
                indicator_value.append(float(row[0]))
                date.append(row[1])

            # create the plot with 10 tick marks for the indicator value, and 5 for the year
            current_index = columns*i + (j+1)
            ax_current = plt.subplot(rows, columns, current_index)
            ax_current.plot(date, indicator_value, 'o', label = country_codes[j])
            ax_current.legend(frameon = True)
            ax_current.set(xlabel = 'year', ylabel = indicator_name, title = indicators[i]+' for '+country_name)
            ax_current.xaxis.set_major_locator(plt.MaxNLocator(5))
            ax_current.yaxis.set_major_locator(plt.MaxNLocator(10))
    plt.show()
