import pandas as pd
import requests
import os
import pickle
import sys
import numpy as np

# we used this website as reference to dowload the data :
#https://towardsdatascience.com/nhl-analytics-with-python-6390c5d3206d
def tidyData (year) :
    """
      Clean the pkl files downloaded with data_Acquistion.py function
      year : season year
      Returns
      pd.DataFrame
      pandas DataFrame where each row is an play event.
      with column names:
         gameID : unique identifier of a play
         events_types: events of the type “shots” and “goals”,we will need only these two for this project
         period : period of the game (the game is 60 min and it had  3 periods : 20 min per period)
         periodTime : time period information 
         periodType :  season_type playoffs pr regular
         teamOfShooter : Team name
         homeOrAway : homeTeam or awayTeam 
         (xCoord, yCoord) : the on-ice coordinates
         shooter : shooter name
         goalie : goalie name
         shotType : the type of the shot ('Wrap-around','Slap Shot','Wrist Shot','Backhand','Snap Shot','Deflected', 'Tip-In')
         emptyNet :  if it was on an empty net - emptyNet
         strength : whether or not a goal was at even strength
         season : the year of the currentplay
         rinkSide : left or right side of the rink where the team is playing

  """
    event_types = ['Shot','Goal'] 
    data_final =[] 
    TARGET_ATTRIBUTES = ["gameID","eventType","period","periodTime","periodType","teamOfShooter","homeOrAway","xCoord", "yCoord","shooter","goalie","shotType","emptyNet","strength","season","rinkSide"]
    if  os.path.exists('./'+str(year)+'finalDataset.csv') :
        print('file already exsiste')  # if the files already exists no need to dowlead them again
    else : 
        with open('./'+str(year)+'FullDataset.pkl', 'rb') as f:
            data_processed = pickle.load(f)
            for data in data_processed:
                if 'liveData' not in data:
                    continue
                allplays_data = data['liveData']['plays']['allPlays'] 
                for play in allplays_data: # For each play
                     for event in event_types:  # For each event (Shot,Goal)
                        if play['result']['event'] in [event]: 
                            eventType= play['result']['event']
                            period=play['about']['period']
                            periodTime = play['about']['periodTime']
                            periodType =play['about']['periodType']
                            teamOfShooter=play['team']['name']
                            gameID=data['gamePk']
                            if str(play['team']['name'])==str(data['gameData']['teams']['away']['name']):
                                homeOrAway= "away"
                            if str(play['team']['name'])==str(data['gameData']['teams']['home']['name']):
                                homeOrAway = "home" 
                            if 'x' in play['coordinates']:
                                xCoord= play['coordinates']['x']
                            else:
                                xCoord= np.nan
                            if 'y' in play['coordinates']:
                                yCoord =play['coordinates']['y']
                            else:
                                yCoord =np.nan
                            shooter =play['players'][0]['player']['fullName']
                            goalie=play['players'][len(play['players'])-1]['player']['fullName']
                            if 'secondaryType' in play['result']:
                                shotType=play['result']['secondaryType']
                            else:
                                shotType=np.nan  
                            if str(play['result']['event']) == 'Shot':
                                emptyNet= np.nan
                            if str(play['result']['event']) == 'Goal':
                                if 'emptyNet' in play['result']:
                                    emptyNet=play['result']['emptyNet']
                                else:
                                    emptyNet=np.nan      
                            if str(play['result']['event']) == 'Shot':
                                strength=np.nan
                            if str(play['result']['event']) == 'Goal':
                                strength=play['result']['strength']['name']
                            if str(periodType)!="SHOOTOUT" and 'rinkSide' in data['liveData']['linescore']['periods'] [int(period)-1][str(homeOrAway)]:
                                rinkSide=data['liveData']['linescore']['periods'][int(period)-1][str(homeOrAway)]['rinkSide']
                            else:
                                rinkSide= np.nan
                            
                            season=str(gameID)[0:4]
                            data_final.append([gameID,eventType,period,periodTime,periodType,teamOfShooter,homeOrAway,xCoord, yCoord,shooter,goalie,shotType,emptyNet,strength,season,rinkSide]) 

        #Transform into into a dataframe
        df = pd.DataFrame(data = data_final, columns= TARGET_ATTRIBUTES)
        df.to_csv('./'+str(year)+'finalDataset.csv', index=False) 
    return
    
     
                        
