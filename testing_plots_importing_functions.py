# testing out plots/importing functions
import sqlite3
import matplotlib.pyplot as plt
import numpy as np

from plotting_indicators_over_time import plot_indicators_country, plot_indicator_countries, plot_indicators_countries

conn = sqlite3.connect('countries.sqlite')
cur = conn.cursor()

see_curr_ind = input("Do you wish to see the current indicators? (Y/N): ").upper()
if see_curr_ind == 'Y':
    cur.execute('SELECT indicator, name FROM Indicators')
    for row in cur:
        print(row[0], row[1])




country_code_list = ['USA', 'ITA', 'MEX']
indicator_list = 'sp.pop.totl'
# plot_indicator_countries(cur, country_code_list, indicator_list)

country_code = 'USA'
indicators = ['sp.pop.0014.to.zs','sp.pop.1564.to.zs','sp.pop.65up.to.zs']
# plot_indicators_country(cur, country_code, indicators)

country_code_list = ['USA', 'ITA', 'MEX']
indicators = ['sp.pop.0014.to.zs','sp.pop.1564.to.zs','sp.pop.65up.to.zs']
# plot_indicators_countries(cur, country_code_list, indicators)
