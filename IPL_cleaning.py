import pandas as pd
import regex
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
from requests.packages.urllib3.exceptions import InsecureRequestWarning
#===============================players_info========================================================
response = requests.get("https://en.wikipedia.org/wiki/List_of_Chennai_Super_Kings_cricketers", verify=False)
soup = BeautifulSoup(response.text, "html.parser")
rows = soup.find_all('tr')

#extracting table_data which is <td> tag from web page
final = []
#looping through all td's
for row in rows:
    td = row.find_all("td")
    text = str(td)
    res = BeautifulSoup(text, 'lxml').get_text()
    final.append(res)
df = pd.DataFrame(final)

#expadning the list
df1 = df[0].str.split(",", expand=True)

#dropping unwamted rows
df1 = df1.drop(index=[0, 1, 104, 105, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119])

#dropping none or null values
df2 = df1.dropna(how="all")

# df2 = df2.head(10)

#replacing \n characters
df2 = df2.replace("\n", " ", regex=True)
# df2 = df2[0].str.strip("[]")
# df2 = df2[21].str.strip("]")

#stripping of square brackets
df2 = df2.apply(lambda x: x.str.strip('[]'))
df2 = df2.replace("-", 0, regex=True)
df2 = df2.reset_index(drop=True)

#extracting headers from web page with same above process
head = soup.find_all("th")
header = []
text = str(head)
final_text = BeautifulSoup(text, "lxml").get_text()
header.append(final_text)
df3 = pd.DataFrame(header)
df3 = df3[0].str.split(",", expand=True)
df3 = df3.iloc[:, 5:27]
df3 = df3.replace("\n", " ", regex=True)
df3 = df3.apply(lambda x: x.str.strip('[]'))
# print(df2)
# print(df3)
player_infocsv = df2.to_csv('player_info.csv', index=False)
#==========================================season_summary batting================================================
tool = pd.read_csv("D:/IPL/raw/all_season_batting_card.csv", usecols = [0,8,11,12,13,15,16,17])
df1 = tool[tool['current_innings'] == 'CSK']
df1['total_runs'] = df1.groupby(['fullName', 'season'])['runs'].transform('sum')
df1['HS'] = df1.groupby(['fullName', 'season'])['runs'].transform('max')
df1["four's"] = df1.groupby(['fullName', 'season'])['fours'].transform('sum')
df1["sixe's"] = df1.groupby(['fullName', 'season'])['sixes'].transform('sum')
df1["100s"] = df1.groupby(['fullName', 'season'])['runs'].transform(lambda x: (x >= 100).sum())
df1["50s"] = df1.groupby(['fullName', 'season'])['runs'].transform(lambda x: ((x >= 50) & (x < 99)).sum())
df1['strikeRate'] = pd.to_numeric(df1['strikeRate'], errors='coerce')
df1["strikerate"] = round(df1.groupby(['fullName', 'season'])['strikeRate'].transform('mean'), 2)
df1['no_of_boundaries'] = df1["four's"] + df1["sixe's"]
df1["boundary%"] = (df1['no_of_boundaries'] / df1['total_runs']) * 100
df1 = df1.drop(columns=['current_innings', 'runs', 'ballsFaced', 'fours', 'sixes', 'strikeRate'])
df1 = df1.drop_duplicates()
df1 = df1.to_csv('season_batting_summary.csv', index=False)
# print(df1)
#=====================================season_summary bowling=========================================================
tool2 = pd.read_csv("D:/IPL/raw/all_season_bowling_card.csv", usecols=[0, 1, 5, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21])
df2 = tool2[tool2['bowling_team'] == 'CSK']
df2['economyRate'] = pd.to_numeric(df2['economyRate'], errors='coerce')
df2['total_overs'] = df2.groupby(['fullName', 'season'])['overs'].transform('sum')
df2['total_maidens'] = df2.groupby(['fullName', 'season'])['maidens'].transform('sum')
df2['runs_conceded'] = df2.groupby(['fullName', 'season'])['conceded'].transform('sum')
df2['total_wickets'] = df2.groupby(['fullName', 'season'])['wickets'].transform('sum')
df2['dot_balls'] = df2.groupby(['fullName', 'season'])['dots'].transform('sum')
df2['runs_conceded'] = df2.groupby(['fullName', 'season'])['conceded'].transform('sum')
df2['fours_conceded'] = df2.groupby(['fullName', 'season'])['foursConceded'].transform('sum')
df2['sixes_conceded'] = df2.groupby(['fullName', 'season'])['sixesConceded'].transform('sum')
df2['total_economy'] = df2.groupby(['fullName', 'season'])['economyRate'].transform('mean')
df2['fi_wickets'] = (df2.groupby(['fullName', 'season', 'match_id'])['wickets'].transform('sum') >= 5)
df2['5W_count'] = df2.groupby(['fullName', 'season'])['fi_wickets'].transform('sum')
df2['wide_extras'] = df2.groupby(['fullName', 'season'])['wides'].transform('sum')
df2['nobe_extras'] = df2.groupby(['fullName', 'season'])['noballs'].transform('sum')
df2['extras'] = df2['wide_extras']+df2['nobe_extras']
df2 = df2.drop(columns=['overs', 'maidens', 'conceded', 'wickets', 'economyRate', 'dots', 'foursConceded', 'sixesConceded', 'fi_wickets', 'match_id', 'wides', 'noballs', 'wide_extras', 'nobe_extras'])
df2 = df2.drop_duplicates()
df2 = df2.to_csv('season_bowling_summary.csv', index=False)
# print(df2)