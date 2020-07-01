# Creating visuals of the extracted data from the world bank.
# This script will contain all of the functions used to compare indicator(s) between country(ies).
import sqlite3
import matplotlib.pyplot as plt
import numpy as np


# things to improve: maybe scale the y axis values, for population for example, plot in (10 millions) or something like that
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
        # note that the for loop plots the indicator for each country first, plt.show is called after everything is on the graph
        ax.plot(date, indicator_value, 'o', label = country_codes[i])
        ax.legend(frameon = True)
        ax.set(xlabel = 'year', ylabel = indicator_name, title = indicator)
        ax.xaxis.set_major_locator(plt.MaxNLocator(5))
        ax.yaxis.set_major_locator(plt.MaxNLocator(10))
    plt.show()

# things to improve: if the indicators are related, add an option to normalize the y axis scales
# if the indicators are related, maybe plot them in a single row or column, based on user preference ...
# clean up the y axis labels as they overlap
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
    # extract the country id
    cur.execute('SELECT id, country_name FROM Countries WHERE country_code = (?)', (country_code.upper(), ) )
    (country_id, country_name) = cur.fetchone()
    for j in range(num_indicators):
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


# things to improve on: clean up the axes labels for the subplot, perhaps only keep the x labels for the bottom plots
# and the y labels for the plots on the far left
# normalize the y-axis scales to allow for better comparisons between countries
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


# to add: allow for multiple countries to be analysed
# give option to scale axis/input limits
# maybe connect the dots based on date ...
def plot_indicator_indicator(cur, country_code, indicator_1, indicator_2):
    # this function plots indicator 1 vs indicator 2 for a single country
    # extract the country id and name
    cur.execute('SELECT id, country_name FROM Countries WHERE country_code = (?)', (country_code.upper(), ) )
    (country_id, country_name) = cur.fetchone()
    # extract the indicator id and indicator name (title of plot) for each indicator, store in a dictionary
    indicator_id_name = dict()
    for indicator in [indicator_1, indicator_2]:
        cur.execute('SELECT id, name FROM Indicators WHERE indicator = (?)', (indicator.upper(), ))
        indicator_id_name[indicator] = cur.fetchone()

    # extracting the rows that correspond to indicator_1 or indicator_2 that have matching dates for the given country
    cur.execute('''SELECT A1.indicator_value AS ind_1, A2.indicator_value AS ind_2, A1.date AS date
            FROM AllData AS A1 JOIN AllData AS A2
            ON A1.date = A2.date AND A1.indicator_id = (?) AND A2.indicator_id = (?) AND A1.country_id = (?) AND A1.country_id = A2.country_id
            ''', (indicator_id_name[indicator_1][0] , indicator_id_name[indicator_2][0], country_id) )
            # the lines below do the same thing as the single ON statement above
            # ON A1.date = A2.date AND A1.indicator_id = (?) AND A2.indicator_id = (?)
            # WHERE A1.country_id = (?) AND A1.country_id = A2.country_id

    # loop through the rows selected by the self join query above
    indicator_value_1 = []
    indicator_value_2 = []
    date = []
    for row in cur:
        indicator_value_1.append(float(row[0]))
        indicator_value_2.append(float(row[1]))
        date.append(row[2])
    # set up the plot
    fig, ax = plt.subplots()
    ax.plot(indicator_value_1, indicator_value_2, 'o', label = country_code)
    ax.legend(frameon = True)
    # label each point with the year it corresponds to, enumerate just give you a counter, could have made earlier code cleaner ...
    for i,year in enumerate(date):
        # when using annotate, the second parameter, 'xy' has to be a tuple (x value, y value)
        ax.annotate(str(year), (indicator_value_1[i], indicator_value_2[i]), size = 10 )
    # name the axes with the corresponding indicator names
    ax.set(xlabel = indicator_id_name[indicator_1][1], ylabel = indicator_id_name[indicator_2][1], title = country_name)
    ax.xaxis.set_major_locator(plt.MaxNLocator(6))
    ax.yaxis.set_major_locator(plt.MaxNLocator(10))
    plt.show()


# things to improve: cleaning axes labels for multiple countries
# when you only plot years where every indicator has values, normalize the x-axis scales)
def stacked_bar_graphs(cur, indicators, country_codes, plot_rows, plot_columns, show_all = True):
    # this plotting function will produce a stacked bar graph of indicators that are naturally grouped together, a separate graph for each country
    # you will need the following libraries: numpy as np, matplotlib.pyplot as plt, sqlite3

    # extract the name and id of every indicator
    indicator_id_name = []
    for indicator in indicators:
        cur.execute('SELECT id, name FROM Indicators WHERE indicator = (?)', (indicator.upper(), ))
        indicator_id_name.append(cur.fetchone())

    # the latest year currently in the database
    cur.execute('SELECT MAX(date) FROM AllData' )
    latest_year = cur.fetchone()[0]

    # initialize the plotting window
    fig, ax = plt.subplots(plot_rows, plot_columns)

    # extract the country id and name for each country, then loop through them to extract each indicator
    indicator_all_values=dict()
    for k, code in enumerate(country_codes):
        # extract the country id and name for each country
        cur.execute('SELECT id, country_name FROM Countries WHERE country_code = (?)', (code.upper(), ) )
        (country_id, country_name) = cur.fetchone()

        # extract the rows in 'AllData' that correspond to the indicator and country code given
        for id, name in indicator_id_name:
            cur.execute('SELECT indicator_value, date FROM AllData WHERE country_id = (?) AND indicator_id = (?)', (country_id, id))
            current_indicator_values = dict()
            # store the current indicator as a dictionary that maps the date to the indicator value
            for row in cur:
                current_indicator_values[row[1]] = row[0]
            # add the dictionary to another dictionary that maps the indicator id to the dictionary of indicator values ( {date: value} )
            indicator_all_values[id] = current_indicator_values

        # indicator_values_every_year is set up to be a list of lists.  Each sublist contains the indicator values
        # 'dates' holds the dates to be used in the plot, either every year in the database, or only years
        # where every indicator has values.
        indicator_values_every_year = []
        if show_all == True:
            # if every year is to be displayed, create the 'dates' list based on the hard coded 1960(earliest record of data in the world bank) and the latest year
            dates = list(range(1960,latest_year+1))
            indicator_values_every_year = []
            for id in indicator_all_values:
                # a temp list of the current indicators is initialized
                current_indicator_values_years = []
                for j in range(1960,latest_year+1):
                    # for each year, check to see if it is in the corresponding dictionary in 'indicator_all_values', if not set the value to zero
                    current_indicator_values_years.append(indicator_all_values[id].get(j , 0 ))
                # add the temp list to 'indicator_values_every_year'
                indicator_values_every_year.append(current_indicator_values_years)
        else:
            # if you only want to look for dates where evey indicator is filled, begin by initializing the dates to 1960-latest_year
            # each iteration of the for loop will update the dates so that you only keep years that are present for every indicator,
            # note that it does this by comparing two date lists at a time, until you finish with every indicator
            dates = list(range(1960,latest_year,1))
            for id in indicator_all_values:
                # get the dates for the current indicator (basically just retrieving the keys of the dictionary )
                current_dates = list(indicator_all_values[id])
                # compare the 'dates' list to the current dates and only keep their union (the years store in both)
                dates = [value for value in dates if value in set(current_dates)]
            # now that you have the overlapping 'dates', create a list of lists, where the inner lists contain the indicator values
            # in the 'indicator_all_values' dictionary that correspond to your overlapping 'dates', for each indicator
            for id in indicator_all_values:
                indicator_values_every_year.append([ indicator_all_values[id][date] for date in dates ])



        # plotting set up for each country
        ax_current = plt.subplot(plot_rows, plot_columns, k+1)
        bar_height = [0]*len(dates)
        bar_colors = ['maroon', 'indianred', 'lightcoral', 'pink', 'mistyrose']    # I believe the maximum number of colors that I will need is 5 so this should suffice for now
        bar_width = 1
        bar_names = [str(date) for date in dates]
        # I have indicator_values_every_year, so loop through them ...
        for i, values in enumerate(indicator_values_every_year):
            current_values = [float(value) for value in values]
            ax_current.bar(dates, current_values, bottom = bar_height, color = bar_colors[i], edgecolor ='white', width = bar_width, label = indicators[i])
            ax_current.legend(frameon = True)
            bar_height = [current_height + added_height for current_height,added_height in zip(bar_height, current_values )]
            # plt.xticks(dates, bar_names, fontweight = 'bold', size = 8)
            # ax_current.xlabel('year')
            ax_current.set(xlabel = 'year', ylabel = 'Percentages', title = country_name)

    # Show graphic once you have gone through every country
    plt.show()
















def test_code(cur, country_codes, indicator_1, indicator_2):


    # y-axis in bold
    rc('font', weight='bold')

    # Values of each group
    bars1 = [12, 28, 1, 8, 22]
    bars2 = [28, 7, 16, 4, 10]
    bars3 = [25, 3, 23, 25, 17]

    # Heights of bars1 + bars2
    bars = np.add(bars1, bars2).tolist()

    # The position of the bars on the x-axis
    r = [0,1,2,3,4]

    # Names of group and bar width
    names = ['A','B','C','D','E']
    barWidth = 1

    # Create brown bars
    plt.bar(r, bars1, color='#7f6d5f', edgecolor='white', width=barWidth)
    # Create green bars (middle), on top of the firs ones
    plt.bar(r, bars2, bottom=bars1, color='#557f2d', edgecolor='white', width=barWidth)
    # Create green bars (top)
    plt.bar(r, bars3, bottom=bars, color='#2d7f5e', edgecolor='white', width=barWidth)

    # Custom X axis
    plt.xticks(r, names, fontweight='bold')
    plt.xlabel("group")

    # Show graphic
    plt.show()
    return
