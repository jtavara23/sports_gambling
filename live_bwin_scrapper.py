from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import pickle
import re

options = Options()
#options.headless = True
options.headless = False
web = 'https://sports.bwin.com/en/sports/live/football-4?fallback=false'
path = 'C:/Users/Usuario/Documents/chromedriver'

options.add_argument('window-size=1920x1080')
driver = webdriver.Chrome(path, options=options)
#driver.maximize_window()
driver.get(web)

teams = []
x12 = []
btts = []
over_under = [] 
odds_events = []

#switching dropdown
#option1
# time.sleep(2)
# dropdown = driver.find_elements_by_css_selector("div.title.multiple")
#option2
dropdown_1 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main-view"]/ms-live/ms-live-event-list/div/ms-grid/ms-grid-header/div/ms-group-selector[3]/ms-dropdown/div')))
dropdown_1.click()
dropdown_1.find_element_by_xpath('//*[@id="main-view"]/ms-live/ms-live-event-list/div/ms-grid/ms-grid-header/div/ms-group-selector[3]/ms-dropdown/div[2]/div[10]').click()

box = driver.find_element_by_xpath('//ms-grid[contains(@sortingtracking,"Live")]') #livebox
rows = WebDriverWait(box, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'grid-event')))

for row in rows:
    odds = row.find_elements_by_class_name('grid-option-group')
    try:
        empty_events = row.find_elements_by_class_name('empty') #removing empty odds
        odds = [odd for odd in odds if odd not in empty_events]
    except:
        pass
    for n, odd in enumerate(odds[:3]): #only the 3 first dropdowns
        if n==0:
            x12.append(odd.text) # result 1x2
            grandparent = odd.find_element_by_xpath('./..').find_element_by_xpath('./..')
            teams.append(grandparent.find_element_by_class_name('grid-event-name').text)
        if n==1:
            over_under.append(odd.text)
        if n==2:
            btts.append(odd.text) # handicap 0:1

# Close page site
#driver.quit()

#unlimited columns
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

dict_gambling = {'Teams':teams,'btts': btts,
                 'Over/Under': over_under, '3-way': x12}

df_bwin = pd.DataFrame.from_dict(dict_gambling)
df_bwin['Over/Under'] = df_bwin['Over/Under'].apply(lambda x:re.sub(',', '.', x))
df_bwin = df_bwin.applymap(lambda x: x.strip() if isinstance(x, str) else x)

output = open('df_bwin', 'wb')
pickle.dump(df_bwin, output)
output.close()
print(df_bwin)