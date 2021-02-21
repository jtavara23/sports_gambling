# taken from https://medium.com/datadriveninvestor/make-money-with-python-the-sports-arbitrage-project-3b09d81a0098

#import libraries
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time


web = 'https://sports.tipico.de/en/live/soccer'
path = 'C:/Users/Usuario/Documents/chromedriver'

#---------------------------------------------
#changing chromedriver default options
options = Options()
#options.headless = True
#options.add_argument('window-size=1920x1080') #Headless = True

#Alternative
options.headless=False

#execute chromedriver with edited options
driver = webdriver.Chrome(path, options=options)
#driver.maximize_window()
driver.get(web)

#---------------------------------------------
try:
    #option 1
    #accept = WebDriverWait(driver, 5)
    #accept = accept.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_evidon-accept-button"]')))
    #option 2
    time.sleep(5)
    accept = driver.find_element_by_xpath('//*[@id="_evidon-accept-button"]')
    accept.click()
except NoSuchElementException:
    print("no banner found and clicked")
    pass
#---------------------------------------------
#Initialize your storage
teams = []
x12 = []
#selection options
btts = []
over_under = []
odds_events = []

#select values from dropdown
first_dropdown = Select(WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/main/main/section/div/div/div[4]/div[1]/div/div[1]/select[1]'))))
second_dropdown = Select(WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/main/main/section/div/div/div[4]/div[1]/div/div[1]/select[2]'))))
third_dropdown = Select(WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/main/main/section/div/div/div[4]/div[1]/div/div[1]/select[3]'))))
first_dropdown.select_by_visible_text('Both teams to score?')
second_dropdown.select_by_visible_text('Over/Under')
third_dropdown.select_by_visible_text('3-Way')

#---------------------------------------------

#Looking for live events 'Program_LIVE'
box = driver.find_element_by_xpath('//div[contains(@testid, "Program_LIVE")]')
#Looking for 'sports titles'
sport_title = box.find_elements_by_class_name('SportTitle-styles-sport')
#---------------------------------------------

#Find empty events
for sport in sport_title:
    print('@sport: ',sport.text)
    # selecting only football
    if sport.text == 'Football':
        parent = sport.find_element_by_xpath('./..') #immediate parent node
        grandparent = parent.find_element_by_xpath('./..') #grandparent node = the whole 'football' section
        #3 empty groups
        try:
            empty_groups = grandparent.find_elements_by_class_name('EventOddGroup-styles-empty-group')
            empty_events = [empty_group.find_element_by_xpath('./..') for empty_group in empty_groups[:]]
            print('(@>> ',empty_events.text)
            print('')
        except:
            pass
         #Looking for single row events
        single_row_events = grandparent.find_elements_by_class_name('EventRow-styles-event-row')
        print("single_row_events: ", len(single_row_events))
        #4 Remove empty events from single_row_events
        
        try:
            empty_events
            single_row_events = [single_row_event for single_row_event in single_row_events if single_row_event not in empty_events]
        except:
            pass
        for n, match in enumerate(single_row_events):
            odds_event = match.find_elements_by_class_name('EventOddGroup-styles-odd-groups')
            #if n < 3:
            odds_events.append(odds_event)
            # teams
            for team in match.find_elements_by_class_name('EventTeams-styles-titles'):
                #print('>>team', len(team.text), team.text)
                teams.append(team.text)
    
        for odds_event in odds_events:
            for n, box in enumerate(odds_event):
                rows = box.find_elements_by_xpath('.//*')
                #print('>>row in box', rows[0].text)
                #print("----------------")
                if n == 0:
                    #6 both teams to score
                    btts.append(rows[0].text)
                if n == 1:
                    #5 over/under + goal line
                    parent = box.find_element_by_xpath('./..')
                    goals = parent.find_element_by_class_name('EventOddGroup-styles-fixed-param-text').text
                    over_under.append(goals+'\n'+rows[0].text)
                if n == 2:
                    #3-way
                    x12.append(rows[0].text)
        #"""
#print(len(btts))
#"""
import pandas as pd
import pickle
#7 #unlimited columns
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

#Storing lists within dictionary
dict_gambling = {'Teams': teams, 'btts': btts,
                 'Over/Under': over_under, '3-way': x12}
#Presenting data in dataframe
df_tipico = pd.DataFrame.from_dict(dict_gambling)
#clean leading and trailing whitespaces
df_tipico = df_tipico.applymap(lambda x: x.strip() if isinstance(x, str) else x) #14.0\n or 14 or \n14.0

#Save data with Pickle
output = open('df_tipico', 'wb') #don't forget to change name_of_file
pickle.dump(df_tipico, output)
output.close()
print(df_tipico)
#"""

"""
single_row_events:  45
                                        Teams                 btts        Over/Under        3-way
0                 Atletico Madrid\nUD Levante       400.00\n400.00        2.5\n15.00        15.00
1                   Real Oviedo B\nCD Lealtad    20.00\n4.00\n1.25   1.5\n2.40\n1.50   3.40\n1.25
2               SD Amorebieta\nDep. Alaves II         30.00\n50.00   4.5\n3.90\n1.20   1.90\n1.75
3                Union Mutilvera\nCD Tudelano    25.00\n4.50\n1.20   1.5\n2.70\n1.40   3.30\n1.25
4                Atzeneta UE\nAtl. Levante UD         50.00\n50.00   3.5\n3.20\n1.30   7.50\n1.04
5             Lorca Deportiva CF\nUCAM Murcia    10.00\n4.50\n1.30   1.5\n1.40\n2.70   2.10\n1.60
6          Real Betis B. B\nClub Rec. Granada     1.90\n3.10\n4.00   1.5\n1.60\n2.20   2.40\n1.50
7                     Genoa FC\nHellas Verona     2.80\n2.90\n2.80   2.5\n2.40\n1.50   2.00\n1.70
8                     AC Pisa 1909\nEmpoli FC     3.20\n3.30\n2.10   2.5\n1.85\n1.85   1.70\n2.00
9            Alanyaspor\nGalatasaray Istanbul     8.50\n4.00\n1.40   2.5\n1.85\n1.85   1.60\n2.20
10        Istanbulspor AS\nYilport Samsunspor     7.50\n4.00\n1.40   2.5\n1.95\n1.75   1.70\n2.00
11             FC Nantes\nOlympique Marseille     1.45\n3.60\n7.50   1.5\n1.50\n2.40   2.00\n1.70
12                      TSV Hartberg\nSV Ried     2.80\n2.20\n3.80   3.5\n2.55\n1.45
13                WSG Wattens\nSKN St. Polten     2.10\n2.50\n4.70   1.5\n2.20\n1.60   3.40\n1.27
14              FK Austria Vienna\nSCR Altach     2.10\n2.55\n4.50   3.5\n2.20\n1.60
15              MVV Maastricht\nSBV Excelsior     6.00\n1.50\n3.80   0.5\n2.10\n1.65  10.00\n1.01
16           Belenenses Lissabon\nCD Nacional    1.13\n5.50\n50.00   3.5\n2.20\n1.60
17                     FC Vizela\nCasa Pia AC     1.65\n3.30\n5.50   2.5\n2.10\n1.65   1.95\n1.70
18  TS Podbeskidzie B.\nJagiellonia Bialystok    1.27\n4.70\n11.00   2.5\n1.85\n1.85   1.70\n2.00
19          RTS Widzew Lodz\nKorona Kielce SA    1.30\n4.50\n11.00   2.5\n1.55\n2.20   1.55\n2.20
20           FC Fastav Zlin\nAC Sparta Prague       400.00\n250.00   3.5\n2.70\n1.40   5.00\n1.12
33               Al Muaither SC\nAl Mesaimeer  300.00\n10.00\n1.02   3.5\n5.50\n1.10
34                  Al Markhiya\nAl Shahaniya       250.00\n200.00  2.5\n10.00\n1.01        10.00
35                          Lusail\nAl Shamal        250.00\n50.00        1.5\n15.00        20.00
36             FUS Rabat\nAthletic Youssoufia    1.25\n4.50\n15.00   2.5\n2.50\n1.45   2.10\n1.60
37         Young Africans SC\nMtibwa Sugar FC     1.75\n2.70\n6.50   1.5\n2.10\n1.60   3.80\n1.20
38  Gambia Ports Authority\nGambia Armed For.     1.32\n4.30\n9.00   2.5\n2.60\n1.45   2.10\n1.65
39                   Gamtel FC\nBanjul United     2.70\n2.20\n3.80   0.5\n1.45\n2.55   5.00\n1.12
40                 Fortune FC\nBrikama United   1.11\n20.00\n35.00   3.5\n2.50\n1.47   3.30\n1.25
41                 AS Nianan\nC. O. de Bamako    30.00\n6.50\n1.10   3.5\n2.70\n1.40   1.90\n1.75
42                  Floriana FC\nGudja United     1.90\n3.10\n4.00   2.5\n1.95\n1.75   1.75\n1.90
43   Zejtun Corinthians F.c.\nGzira United FC    13.00\n6.50\n1.18   3.5\n1.85\n1.85   1.55\n2.20
44        AC Omonia Nicosia\nApoel Nicosia FC    1.22\n5.00\n12.00   2.5\n1.90\n1.80   1.90\n1.80
"""