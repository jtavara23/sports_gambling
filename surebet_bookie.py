#https://medium.com/datadriveninvestor/make-money-with-python-the-sports-arbitrage-project-3b09d81a0098
import subprocess
import pandas as pd
import pickle
from fuzzywuzzy import process, fuzz
from sympy import symbols, Eq, solve

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

#scrape in parallel (at the same time)
#subprocess.run("python3 live_tipico_scrapper.py & python3 live_bwin_scrapper.py & python3 live_betfair_scrapper.py & wait", shell=True)

# Glambing at TIPICO
#1.#transforming data bookie 1,2 and 3
df_tipico = pickle.load(open('df_tipico','rb'))
# there was an error creating this column! 
df_tipico = df_tipico[['Teams', '3-way']] 
df_tipico = df_tipico.rename(columns={"3-way":"btts"})

df_tipico = df_tipico.replace(r'', '0\n0', regex=True)#odds with no values
#Turns huge odds like 40\n into ‘0\n0’. We use regular expressions to catch the pattern of these odds.
df_tipico = df_tipico.replace(r'^\d+\.\d+$', '0\n0', regex=True)#odds with only one element


# Glambing at BWIN
df_bwin = pickle.load(open('df_bwin','rb'))
df_bwin = df_bwin[['Teams', 'btts']]
df_bwin = df_bwin.replace(r'', '0\n0', regex=True)
df_bwin = df_bwin.replace(r'^\d+\.\d+$', '0\n0', regex=True)


# Glambing at BetFair
df_betfair = pickle.load(open('df_betfair','rb'))
df_betfair = df_betfair[['Teams', 'btts']]
df_betfair = df_betfair.replace(r'', '0\n0', regex=True)
df_betfair = df_betfair.replace(r'^\d+\.\d+$', '0\n0', regex=True)

#print(df_tipico.shape)
#print(df_tipico.head())
#print(df_betfair.shape)
#print(df_betfair.head())
#print(df_bwin.shape)
#print(df_bwin.head())

#2.String matching
teams_tipico = df_tipico['Teams'].tolist()
teams_bwin = df_bwin['Teams'].tolist()
teams_betfair = df_betfair['Teams'].tolist()

# Team names and scores, matched by Fuzzy rules

# Tipico vs Bwin
df_tipico[['Teams_matched_bwin', 'Score_bwin']] = df_tipico['Teams'].apply(
    lambda x:process.extractOne(x, teams_bwin, scorer=fuzz.token_set_ratio)).apply(pd.Series)
#Tipico vs BetFair
df_tipico[['Teams_matched_betfair', 'Score_betfair']] = df_tipico['Teams'].apply(
    lambda x:process.extractOne(x, teams_betfair, scorer=fuzz.token_set_ratio)).apply(pd.Series)
#Bwin vs BetFair
df_bwin[['Teams_matched_betfair', 'Score_betfair']] = df_bwin['Teams'].apply(
    lambda x:process.extractOne(x, teams_betfair, scorer=fuzz.token_set_ratio)).apply(pd.Series)

# PD.Series transforms the 2 outputs into a data frame that are assigned to the columns df_tipico[[‘Teams_matched_bwin’, ‘Score_bwin’]]

#print(df_tipico.head())
#print(df_bwin.head())

# I’ll use 60 and 55 as the minimum scores needed to consider two names are the same. 
# However, sometimes this still might match different teams.
# Once a surebet is found, use your common sense to see if the teams are actually the same.

df_surebet_tipico_bwin = pd.merge(df_tipico, df_bwin, left_on='Teams_matched_bwin', right_on='Teams')
df_surebet_tipico_bwin = df_surebet_tipico_bwin[df_surebet_tipico_bwin['Score_bwin']>60]
df_surebet_tipico_bwin = df_surebet_tipico_bwin[['Teams_x', 'btts_x', 'Teams_y', 'btts_y']]

df_surebet_tipico_betfair = pd.merge(df_tipico, df_betfair, left_on='Teams_matched_betfair', right_on='Teams')
df_surebet_tipico_betfair = df_surebet_tipico_betfair[df_surebet_tipico_betfair['Score_betfair']>55]
df_surebet_tipico_betfair = df_surebet_tipico_betfair[['Teams_x', 'btts_x', 'Teams_y', 'btts_y']]

df_surebet_bwin_betfair = pd.merge(df_bwin, df_betfair, left_on='Teams_matched_betfair', right_on='Teams')
df_surebet_bwin_betfair = df_surebet_bwin_betfair[df_surebet_bwin_betfair['Score_betfair']>55]
df_surebet_bwin_betfair = df_surebet_bwin_betfair[['Teams_x', 'btts_x', 'Teams_y', 'btts_y']]

#print(df_surebet_tipico_bwin.head(10))
#print(df_surebet_tipico_bwin.size)
#print(df_surebet_tipico_betfair.head(10))
#print(df_surebet_tipico_betfair.size)
#print(df_surebet_bwin_betfair.head(100))
#print(df_surebet_bwin_betfair.size)


# 3. Finding Surebets
# Formula to find surebets
def find_surebet(frame):
    #splits the odds into 2 elements. The first is stored in the column 'btts_x_1' and the second in 'btts_x_2'. Both columns are being created as we apply the formula
    frame[['btts_x_1', 'btts_x_2']] = frame['btts_x'].apply(lambda x: x.split('\n')).apply(pd.Series).astype(float)
    frame[['btts_y_1', 'btts_y_2']] = frame['btts_y'].apply(lambda x: x.split('\n')).apply(pd.Series).astype(float)
    #this is the formula to find surebets. You can also find surebets in the pair of odds btts_x_2 and btts_y_1
    frame['sure_btts1'] = (1 / frame['btts_x_1']) + (1 / frame['btts_y_2'])
    frame['sure_btts2'] = (1 / frame['btts_x_2']) + (1 / frame['btts_y_1'])
    frame = frame[['Teams_x', 'btts_x', 'Teams_y', 'btts_y', 'sure_btts1', 'sure_btts2']]
    #  selects only matches that had results less than 1, which is a requirement for a surebet. The ‘|’ symbol is an ‘or’ conditional.
    frame = frame[(frame['sure_btts1'] < 1) | (frame['sure_btts2'] < 1)]
    #  resets the index. We need this to identify the matches in which the code found a surebet.
    frame.reset_index(drop=True, inplace=True)
    return frame

#applying formula
df_surebet_tipico_bwin = find_surebet(df_surebet_tipico_bwin)
df_surebet_tipico_betfair = find_surebet(df_surebet_tipico_betfair)
df_surebet_bwin_betfair = find_surebet(df_surebet_bwin_betfair)

#creating dictionary
dict_surebet = {'Tipico-Bwin':df_surebet_tipico_bwin,
                'Tipico-Betfair':df_surebet_tipico_betfair,
                'Bwin-Betfair':df_surebet_bwin_betfair}


# 4. Formula to calculate stakes
# We do this to find the stakes necessary for the bet and the profits we’ll make.
def beat_bookies(odds1, odds2, total_stake):
    x, y = symbols('x y')
    eq1 = Eq(x + y - total_stake, 0) # total_stake = x + y
    eq2 = Eq((odds2*y) - odds1*x, 0) # odds1*x = odds2*y
    stakes = solve((eq1,eq2), (x, y))
    total_investment = stakes[x] + stakes[y]
    profit1 = odds1*stakes[x] - total_stake
    profit2 = odds2*stakes[y] - total_stake
    benefit1 = f'{profit1 / total_investment * 100:.2f}%'
    benefit2 = f'{profit2 / total_investment * 100:.2f}%'
    dict_gabmling = {'Odds1':odds1, 'Odds2':odds2, '\nStake1':f'${stakes[x]:.0f}', ' - Stake2':f'${stakes[y]:.0f}',
                    '\nProfit1':f'${profit1:.2f}', '- Profit2':f'${profit2:.2f}',
                    '\nBenefit1': benefit1, ' - Benefit2': benefit2}
    return dict_gabmling

# total_stake is the total amount you’re willing to bet in each game. 
# You have to define the amount appropriate for you. In this example, I chose 100
total_stake = 100

#calculating stakes
for frame in dict_surebet:
    if len(dict_surebet[frame])>=1: # filters out frames where there wasn’t found any surebet
        print('\n\n------------------SUREBETS Found! '+ frame +' (check team names)--------------------------------------------------')
        print(dict_surebet[frame])
        print('------------------Stakes-------------------------')
        for i, value in enumerate(dict_surebet[frame]['sure_btts1']):
            if value<1: # filters out non-surebets inside ‘sure_btts1’ or ‘sure_btts2’
                # finds the first odds 
                odds1 = float(dict_surebet[frame].at[i, 'btts_x'].split('\n')[0]) # 
                odds2 = float(dict_surebet[frame].at[i, 'btts_y'].split('\n')[1])
                teams = dict_surebet[frame].at[i, 'Teams_x'].split('\n')
                dict_1 = beat_bookies(odds1, odds2, total_stake)
                print('[' + str(i) + '] '+'-'.join(teams)+ ': \n'+ ' '.join('{}: {}'.format(x, y) for x,y in dict_1.items()))
                
        for i, value in enumerate(dict_surebet[frame]['sure_btts2']):
            if value<1:
                odds1 = float(dict_surebet[frame].at[i, 'btts_x'].split('\n')[1])
                odds2 = float(dict_surebet[frame].at[i, 'btts_y'].split('\n')[0])
                teams = dict_surebet[frame].at[i, 'Teams_x'].split('\n')
                dict_2 = beat_bookies(odds1, odds2, total_stake)
                print('[' + str(i) + '] ' + '-'.join(teams) + ' : \n' + ' '.join('{}: {}'.format(x, y) for x, y in dict_2.items()))
            