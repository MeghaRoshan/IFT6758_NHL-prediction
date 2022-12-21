import pandas as pd
import requests
import os
import pickle
import sys
import numpy as np
import datetime
from sklearn import preprocessing
from sklearn.impute import SimpleImputer
import json
from ift6758.data.Feature_Engineering1 import combineAllFeatures
from ift6758.data.Feature_Engineering2 import getPreviousEvent
import warnings
warnings.filterwarnings('ignore')

def getGameData (gameId,idx) : 
    r = requests.get(url='http://statsapi.web.nhl.com/api/v1/game/' + gameId+'/feed/live')
    data = r.json()
    data_final =[] 
    TARGET_ATTRIBUTES = ["gameID","eventType","period","periodTime","periodType","teamOfShooter","homeOrAway","xCoord", "yCoord" ,"shooter", "goalie", "shotType", "emptyNet", "strength", "season", "rinkSide"]
    allplays_data = data['liveData']['plays']['allPlays'] 
    for play in allplays_data: # For each play
        eventType= play['result']['event']
        period=play['about']['period']
        periodTime = play['about']['periodTime']
        periodType =play['about']['periodType']
        if str(play['result']['event']) in ["Shot", "Goal"]  :
            teamOfShooter = play['team']['name']
            if str(play['team']['name'])==str(data['gameData']['teams']['away']['name']):
                homeOrAway= "away"
            if str(play['team']['name'])==str(data['gameData']['teams']['home']['name']):
                homeOrAway = "home"
            shooter =play['players'][0]['player']['fullName']
            goalie=play['players'][len(play['players'])-1]['player']['fullName']
            if str(periodType)!="SHOOTOUT" and 'rinkSide' in data['liveData']['linescore']['periods'] [int(period)-1][str(homeOrAway)]:
                rinkSide=data['liveData']['linescore']['periods'][int(period)-1][str(homeOrAway)]['rinkSide']
            else:
                rinkSide= np.nan
        else : 
            teamOfShooter =  np.nan
            homeOrAway = np.nan
            goalie = np.nan
            shooter = np.nan
            rinkSide =np.nan
        gameID=data['gamePk']
        if 'x' in play['coordinates']:
            xCoord= play['coordinates']['x']
        else:
            xCoord= np.nan
        if 'y' in play['coordinates']:
            yCoord =play['coordinates']['y']
        else:
            yCoord =np.nan
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
                emptyNet =np.nan 
        else :
            emptyNet =np.nan
        if str(play['result']['event']) == 'Shot':
            strength=np.nan
        if str(play['result']['event']) == 'Goal':
            strength=play['result']['strength']['name']
        else :
            strength=np.nan
                            
        season=str(gameID)[0:4]
        data_final.append([gameID,eventType,period,periodTime,periodType,teamOfShooter,homeOrAway,xCoord, yCoord, shooter, goalie, shotType, emptyNet, strength, season, rinkSide]) 
        #Transform into into a dataframe
    df = pd.DataFrame(data = data_final, columns= TARGET_ATTRIBUTES)
    df_feature_eng1= combineAllFeatures(df)
    df_feature_eng1 = df_feature_eng1[df_feature_eng1.index >= idx]
    last_idx = df_feature_eng1.shape[0]
    df_feature_eng2= getPreviousEvent(df_feature_eng1)
    return df_feature_eng2, last_idx

def PreprocessData(gameId, idx) :
    df, last_idx= getGameData (gameId, idx)
    df["rebound"].fillna(value=0)
    df['rebound'].astype(int)
    FinalDf = df[['Is_goal','period','periodSeconds',
              'last_EventType',
              'last_period',
             # 'last_periodTime',(not needed dince we have lastperiodseconds)
              'last_eventxCoord','last_eventyCoord',
             'last_shotType',
              'last_periodSeconds','last_Distance_from_net',
              'last_Angle_from_net',
              'time_from_last_event',
              'distance_from_last_event','rebound','change_in_angle','speed']]
    obj_df=FinalDf.select_dtypes(include=['object']).copy()
    FinalDf=FinalDf.drop(obj_df.columns, axis=1)
    obj_df=obj_df.apply(preprocessing.LabelEncoder().fit_transform)
    Frame=pd.concat([FinalDf,obj_df],axis=1)
    imp_mean = SimpleImputer(missing_values=np.nan, strategy='median')
    imp_mean.fit(FinalDf)
    Transformed_Values=imp_mean.transform(FinalDf)
    TransformedDf = pd.DataFrame(Transformed_Values, index=FinalDf.index, columns=FinalDf.columns)
    TransformedDf_=TransformedDf.drop("period",axis=1)
    test_X = TransformedDf_.drop('Is_goal',axis=1)
    test_X =  test_X.reset_index().drop(columns ='index')
    ###aditinal information 
    df_add,idxx = getGameData (gameId,idx )
    df_add= df_add[['gameID','period','eventType','periodTime','teamOfShooter','homeOrAway']].reset_index().drop(columns ='index')
    result =pd.concat([df_add,test_X],axis=1)
    result['homeTeam'] = result[result['homeOrAway']=='home'].teamOfShooter.unique()[0]
    result['AwayTeam'] = result[result['homeOrAway']=='away'].teamOfShooter.unique()[0]
    ##################### time left before end of period ############################
    periodSeconds = []
    for row in result['periodTime']:
        date_time = datetime.datetime.strptime(row, "%M:%S")
        a_timedelta = date_time - datetime.datetime(1900, 1, 1)
        periodSeconds.append(a_timedelta.total_seconds())
    result['periodTime'] = periodSeconds
    result['timeLeft'] =  1200-result['periodSeconds'] 
    return result, last_idx