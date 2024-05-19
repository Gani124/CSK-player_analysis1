import pandas as pd
import numpy as np
import regex
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
from requests.packages.urllib3.exceptions import InsecureRequestWarning

#==============================match summary========================================================
# df = pd.read_csv("D:/IPL/raw/match_info_data.csv")
# chennai_records1 = df[(df['team1'] == 'Chennai Super Kings') | (df['team2'] == 'Chennai Super Kings')]
# # chennai_records1 = df[df['team1'] == 'Chennai Super Kings']
# columns_to_remove1 = ['toss_winner','toss_decision','result','dl_applied','umpire3']
# chennai_records1 = chennai_records1.drop(columns = columns_to_remove1)
# chennai_records1 = chennai_records1.rename(columns = {'player_of_match':'man_of_match'})
# chennai_records1 = chennai_records1.sort_values('season')
# df1 = chennai_records1.to_csv('match_summary1.csv', index=False)
# print(chennai_records1)
# ===================================batting_summary==========================================
df = pd.read_csv("D:/IPL/raw/match_data.csv")
df1 = df[df['batting_team'] == 'Chennai Super Kings']
# df1 = df1.groupby(['striker', 'match_id'])['runs_off_bat'].sum()
df1['balls_faced'] = df1.groupby(['striker', 'match_id'])['striker'].transform('size')
df1['total_runs'] = df1.groupby(['striker', 'match_id'])['runs_off_bat'].transform('sum')
df1["four's"] = df1.groupby(['striker', 'match_id'])['runs_off_bat'].transform(lambda x: (x == 4).sum())
df1["sixes"] = df1.groupby(['striker', 'match_id'])['runs_off_bat'].transform(lambda x: (x == 6).sum())
df1['no_of_boundaries'] = df1.groupby(['striker', 'match_id'])['runs_off_bat'].transform(lambda x: ((x == 6) | (x == 4)).sum())
df1['boundary_percentage'] = round((df1['no_of_boundaries'] / df1['balls_faced']) * 100, 2)

#power_play
powerplay_runs = df1[df1['ball'] <= 6.0].groupby(['striker', 'match_id'])['runs_off_bat'].sum().reset_index()
powerplay_runs.rename(columns={'runs_off_bat': 'power_play'}, inplace=True)
df1 = pd.merge(df1, powerplay_runs, on=['striker', 'match_id'], how='left')

# power_play_boundary%
powerplay_boundaries = df1[(df1['ball'] <= 6.0) & ((df1['runs_off_bat'] == 4) | (df1['runs_off_bat'] == 6))].groupby(['striker', 'match_id']).size().reset_index(name='power_play_boundaries')
df1 = pd.merge(df1, powerplay_boundaries, on=['striker', 'match_id'], how='left')
df1['power_play_boundary_percentage'] = (df1['power_play_boundaries'] / df1['power_play']) * 100

#middle_overs
middle_overs = df1[(df1['ball'] >= 6.0) & (df1['ball'] <=16.0)].groupby(['striker', 'match_id'])['runs_off_bat'].sum().reset_index()
middle_overs.rename(columns={'runs_off_bat': 'middle_overs'}, inplace=True)
df1 = pd.merge(df1, middle_overs, on=['striker', 'match_id'], how='left')

# Calculate total boundaries hit during middle overs (balls between 6.0 and 16.0) for each player in each match
middleovers_boundaries = df1[(df1['ball'] >= 6.0) & (df1['ball'] <= 16.0) & ((df1['runs_off_bat'] == 4) | (df1['runs_off_bat'] == 6))].groupby(['striker', 'match_id']).size().reset_index(name='middle_overs_boundaries')
df1 = pd.merge(df1, middleovers_boundaries, on=['striker', 'match_id'], how='left')
df1['middle_overs_boundary_percentage'] = (df1['middle_overs_boundaries'] / df1['middle_overs']) * 100

#death_overs
death_overs = df1[df1['ball'] >= 16.0].groupby(['striker', 'match_id'])['runs_off_bat'].sum().reset_index()
death_overs.rename(columns={'runs_off_bat': 'death_overs'}, inplace=True)
df1 = pd.merge(df1, death_overs, on=['striker', 'match_id'], how='left')

# deathover_boundary%
deathover_boundaries = df1[(df1['ball'] >= 16.0) & ((df1['runs_off_bat'] == 4) | (df1['runs_off_bat'] == 6))].groupby(['striker', 'match_id']).size().reset_index(name='death_over_boundaries')
df1 = pd.merge(df1, deathover_boundaries, on=['striker', 'match_id'], how='left')
df1['death_over_boundary_percentage'] = (df1['death_over_boundaries'] / df1['death_overs']) * 100

df1 = df1.drop(columns = ['innings','ball','bowler','extras','wides','noballs','byes','legbyes','penalty','wicket_type','player_dismissed', 'other_wicket_type','other_player_dismissed','runs_off_bat','non_striker','cricsheet_id'])
# df1 = df1.head(10)
df1 = df1.drop_duplicates()
df1 = df1.fillna(0)
df1 = df1.to_csv('match_batting_summary_samp.csv', index=False)
# print(df1)
#===================================Toss decisions==================================================================
# df = pd.read_csv("D:/IPL/raw/match_info_data.csv",usecols = [1,4,5,6,7])
# toss_df = df[(df['team1'] == 'Chennai Super Kings') | (df['team2'] == 'Chennai Super Kings')]
# toss_df['season_counts'] = toss_df.groupby('season').transform('size')
# toss_df['csk_toss_counts'] = toss_df[toss_df['toss_winner'] == "Chennai Super Kings"].groupby('season').transform('size')
# toss_df['toss_win_percentage'] = round((toss_df['csk_toss_counts']/toss_df['season_counts'])*100)
# toss_df = toss_df.head(20)
# print(toss_df)
#==================================bowling_summary==================================================================
# df = pd.read_csv("D:/IPL/raw/match_data.csv")
# df1 = df[df['bowling_team'] == 'Chennai Super Kings']
# df1['runs_leaked'] = df1.groupby(['bowler', 'match_id'])['runs_off_bat'].transform(lambda x: (x != 0).sum())
# df1['dots'] = df1.groupby(['bowler', 'match_id'])['runs_off_bat'].transform(lambda x: (x == 0).sum())
# df1['wides'] = df1.groupby(['bowler', 'match_id'])['wides'].transform('sum')
# df1['no_balls'] = df1.groupby(['bowler', 'match_id'])['noballs'].transform('sum')
# df1["bye's"] = df1.groupby(['bowler', 'match_id'])['byes'].transform('sum')
# df1['leg_byes'] = df1.groupby(['bowler', 'match_id'])['legbyes'].transform('sum')
# df1['extras'] = df1['wides'] + df1['no_balls'] + df1["bye's"] + df1['leg_byes']

# #power_play
# powerplay_runs = df1[df1['ball'] <= 6.0].groupby(['bowler', 'match_id'])['runs_off_bat'].sum().reset_index()
# powerplay_runs.rename(columns={'runs_off_bat': 'power_play'}, inplace=True)
# df1 = pd.merge(df1, powerplay_runs, on=['bowler', 'match_id'], how='left')

# #middle_overs
# middle_overs = df1[(df1['ball'] >= 6.0) & (df1['ball'] <=16.0)].groupby(['bowler', 'match_id'])['runs_off_bat'].sum().reset_index()
# middle_overs.rename(columns={'runs_off_bat': 'middle_overs'}, inplace=True)
# df1 = pd.merge(df1, middle_overs, on=['bowler', 'match_id'], how='left')

# #death_overs
# death_overs = df1[df1['ball'] >= 16.0].groupby(['bowler', 'match_id'])['runs_off_bat'].sum().reset_index()
# death_overs.rename(columns={'runs_off_bat': 'death_overs'}, inplace=True)
# df1 = pd.merge(df1, death_overs, on=['bowler', 'match_id'], how='left')

# #wickets
# df1['wickets'] = df1.groupby(['bowler', 'match_id'])['wicket_type'].transform('count')

# #power_play_wickets
# powerplay_wickets = df1[df1['ball'] <= 6.0].groupby(['bowler', 'match_id'])['wicket_type'].count().reset_index()
# powerplay_wickets.rename(columns={'wicket_type': 'Powerplay_wickets'}, inplace=True)
# df1 = pd.merge(df1, powerplay_wickets, on=['bowler', 'match_id'], how='left')

# #middle_over_wickets
# middle_over_wickets = df1[(df1['ball'] >= 6.0) & (df1['ball'] <=16.0)].groupby(['bowler', 'match_id'])['wicket_type'].count().reset_index()
# middle_over_wickets.rename(columns={'wicket_type': 'middle_over_wickets'}, inplace=True)
# df1 = pd.merge(df1, middle_over_wickets, on=['bowler', 'match_id'], how='left')

# #death_over_wickets
# death_over_wickets = df1[df1['ball'] >= 16.0].groupby(['bowler', 'match_id'])['wicket_type'].count().reset_index()
# death_over_wickets.rename(columns={'wicket_type': 'death_over_wickets'}, inplace=True)
# df1 = pd.merge(df1, death_over_wickets, on=['bowler', 'match_id'], how='left')

# df1 = df1.fillna(0)
# df1 = df1.drop(columns=['innings', 'ball', 'striker', 'non_striker', 'noballs', 'byes', 'legbyes', 'penalty', 'wicket_type', 'player_dismissed', 'other_wicket_type', 'other_player_dismissed', 'runs_off_bat', 'non_striker', 'cricsheet_id'])
# df1 = df1.drop_duplicates()
# df1 = df1.to_csv('match_bowling_summary.csv', index=False)
# print(df1) 