import pandas as pd
import requests
import pickle
import os

#we used this link for game id extraction : https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md#game-ids
def gameIdListExtraction(year,playoffs) : 
    """Return a list of all gameID for regular and playoffs seasons from 2016 to 2021 ,
    that we will use in the next function to extract data of each gameID.
 
    :param year: season year
    :type year: int
    
    :rtype: list
    :return: list of gameIds 
    """
    if playoffs ==False : 
        season_type = ['02']  # 02 is the indicator for regular season and 03 for playoffs season
    else : 
        season_type = ['02', '03' ] 
    gameIdList = [] # list of all game id from  2016 to 2021
    for season in season_type :
        if season =='02' :
            if year == 2016 : 
                for i in range(1230) :  # the regularseason 2016/2017 contains more games than the other seasons
                    game_number ="%04d" % i
                    gameIdList += [str(year)+season  + game_number]
            else : 
                for i in range(1271) :
                    game_number ="%04d" % i
                    gameIdList += [str(year)+season  + game_number]
        else :
            for digit2 in range(1,5):
                for digit3 in range(1,8):
                    for digit4 in range(1,8):
                        game_number ="0"+str(digit2)+str(digit3)+str(digit4)
                        gameIdList +=[str(year)+season + game_number]
    return gameIdList

# we used this website as reference to dowload the data :
#https://www.kaggle.com/code/kapastor/nhl-analytics-data-collection
def dataDownload(year,playoffs) : 
    game_data = []
    gameIdList = gameIdListExtraction(year,playoffs)
    if  os.path.exists('./'+str(year)+'FullDataset.pkl') :
        print('file already exsiste') 
    else : 
        for i in gameIdList :
            r = requests.get(url='http://statsapi.web.nhl.com/api/v1/game/' + i+'/feed/live')
            data = r.json()
            game_data.append(data)
    
        with open('./'+str(year)+'FullDataset.pkl', 'wb') as f:
            pickle.dump(game_data, f, pickle.HIGHEST_PROTOCOL)
    return



