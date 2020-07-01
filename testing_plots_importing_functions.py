# testing out plots/importing functions
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
# note that the libraries needed need to be a part of the function defining script for this to work
from plotting_indicators_over_time import plot_indicators_country, plot_indicator_countries, plot_indicators_countries, plot_indicator_indicator, stacked_bar_graphs

conn = sqlite3.connect('countries.sqlite')
cur = conn.cursor()

see_curr_ind = input("Do you wish to see the current indicators? (Y/N): ").upper()
if see_curr_ind == 'Y':
    cur.execute('SELECT indicator, name FROM Indicators')
    for row in cur:
        print(row[0], row[1])




country_code_list = ['USA', 'ITA', 'MEX']
indicator_list = 'sp.pop.totl'
#plot_indicator_countries(cur, country_code_list, indicator_list)

country_code = 'USA'
indicators = ['sp.pop.0014.to.zs','sp.pop.1564.to.zs','sp.pop.65up.to.zs']
# plot_indicators_country(cur, country_code, indicators)

country_code_list = ['USA', 'ITA', 'MEX']
indicators = ['sp.pop.0014.to.zs','sp.pop.1564.to.zs','sp.pop.65up.to.zs']
#plot_indicators_countries(cur, country_code_list, indicators)


# plot_indicator_indicator(cur, 'USA', 'sp.pop.0014.to.zs', 'sp.pop.1564.to.zs')
educational_indicators = ['se.sec.cuat.lo.zs', 'se.sec.cuat.up.zs', 'se.sec.cuat.po.zs' ]
stacked_bar_graphs(cur, educational_indicators, country_code_list, 1, 3, False)
