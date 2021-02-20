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