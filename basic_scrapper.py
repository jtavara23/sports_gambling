from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time
import pandas as pd

url = 'https://sports.tipico.de/en/todays-matches'
path = 'C:/Users/Usuario/Documents/chromedriver' #introduce your file's path inside '...'

driver = webdriver.Chrome(path)
driver.set_window_size(1000, 900)
driver.get(url)

time.sleep(5)

try:
    #driver.find_element_by_css_selector('[alt="Close"]').click() #clicking to the X.
    accept = driver.find_element_by_xpath('//*[@id="_evidon-accept-button"]')
    accept.click()
    print(' close click worked')
except NoSuchElementException:
    print(' close click failed')
    pass


teams = []
odds_events = []
x12 = [] #3-way

sport_title = driver.find_elements_by_class_name('SportTitle-styles-sport')

for sport in sport_title:
    # selecting only football
    if sport.text == 'Football':
        parent = sport.find_element_by_xpath('./..') #immediate parent node # SportHeader-styles-sport-wrapper
        grandparent = parent.find_element_by_xpath('./..') #grandparent node = the whole 'football' section # Sport-styles-sport-container
        #Looking for single row events
        single_row_events = grandparent.find_elements_by_class_name('EventRow-styles-event-row')
        #Getting data
        for match in single_row_events:
            #'odd_events'
            odds_event = match.find_elements_by_class_name('EventOddGroup-styles-odd-groups')
            odds_events.append(odds_event)
            # Team names
            for team in match.find_elements_by_class_name('EventTeams-styles-titles'):
                teams.append(team.text)
        #Getting data: the odds        
        for odds_event in odds_events:
            for n, box in enumerate(odds_event):
                rows = box.find_elements_by_xpath('.//*')# gives the child nodes inside each ‘odds box’. This gives a list with 1 row (when scraping upcoming matches) or 2 rows (when scraping live matches)
                if n == 0:
                    x12.append(rows[0].text)

#driver.quit()
#Storing lists within dictionary
dict_gambling = {'Teams': teams, '1x2': x12}
#Presenting data in dataframe
df_gambling = pd.DataFrame.from_dict(dict_gambling)
print(df_gambling)
"""
                                        Teams               1x2
0            FC Schalke 04\nBorussia Dortmund  7.30\n5.90\n1.32
1                    Liverpool FC\nEverton FC  1.37\n5.20\n7.30
2                 Fulham FC\nSheffield United  2.10\n3.20\n3.80
3                Torquay United\nHalifax Town  1.80\n3.70\n3.90
4               CF Valencia\nRC Celta de Vigo  2.45\n3.20\n3.00
..                                        ...               ...
115                  AS Real Bamako\nUSC Kita  1.80\n3.10\n4.20
116                        LCBA FC\nAS Police  2.10\n3.00\n3.30
117  Zejtun Corinthians F.c.\nGzira United FC  5.20\n3.80\n1.52
118                 Floriana FC\nGudja United  1.85\n3.40\n3.60
119       AC Omonia Nicosia\nApoel Nicosia FC  1.70\n3.20\n5.00

"""