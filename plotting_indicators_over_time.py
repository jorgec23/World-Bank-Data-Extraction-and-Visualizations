# creating visuals of the extracted data from the world bank

import matplotlib.pyplot as plt
import sqlite3



# optional: output the list of current indicators with their name

conn = sqlite3.connect('countries.sqlite')
cur = conn.cursor()

see_curr_ind = input("Do you wish to see the current indicators? (Y/N): ").upper()
if see_curr_ind == 'Y':
    cur.execute('SELECT indicator, name FROM Indicators')
    for row in cur:
        print(row[0], row[1])


# things to add, plot the indicator value for multiple countries on the same graph, that way
# the plotting library fixes the scaling, or plot multiple graphs on the same figure ...
# maybe it could also plot multiple indicators for the same country, that could be useful as well ...
# nested for loop would take care of this

def plot_indicator_over_time(cur, country_code, indicator):
    # cur = cursor pointing to the 'countries.sqlite' database
    # import mathplotlib.pyplot as plt  has to be at the top of the script for this funciton to run

    # extract the country id
    cur.execute('SELECT id, country_name FROM Countries WHERE country_code = (?)', (country_code.upper(), ) )
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
    # create the plot with 10 tick marks for the indicator value, and 5 for the year
    fig, ax = plt.subplots()
    ax.plot(date, indicator_value, 'bo', label = country_code)
    ax.legend(frameon = True)
    ax.set(xlabel = 'year', ylabel = indicator_name, title = indicator+' for '+country_name)
    ax.xaxis.set_major_locator(plt.MaxNLocator(5))
    ax.yaxis.set_major_locator(plt.MaxNLocator(10))
    plt.show()


# sample outputs of function
# plot_indicator_over_time(cur, 'ITA', 'SE.PRM.CMPT.ZS')
# plot_indicator_over_time(cur, 'USA', 'sp.pop.totl')
# plot_indicator_over_time(cur, 'AFG', 'sp.pop.totl')



# I think this could be the script where I define the functions that I plan to use in
# the Jupyter Notebook
