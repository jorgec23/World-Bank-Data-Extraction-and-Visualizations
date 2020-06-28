# testing out plots/importing functions
import sqlite3
import matplotlib.pyplot as plt

from plotting_indicators_over_time import plot_indicator_over_time as plt_ind_time

conn = sqlite3.connect('countries.sqlite')
cur = conn.cursor()



plt_ind_time(cur, 'USA', 'SP.pop.Totl')
