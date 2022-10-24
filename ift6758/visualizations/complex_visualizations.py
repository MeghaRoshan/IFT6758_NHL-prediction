import numpy as np
import pandas as pd
######################## question 6-1 #######################################

def shotsCoordinatedCorrection (path)  -> pd.DataFrame: 
    """since we will be working only with one side of the rink , this function will Return a dataframe with a
     transformed coordinates. 
    :param path: path of the dataframe
    :type path: String
    
    :rtype: DataFrame
    :return: return a dataframe  
    """
    df = pd.read_csv(path)
    df['x_bin'] = np.where(df['xCoord'] <0 ,( -df['xCoord'] ),( df['xCoord']))
    df['y_bin'] = np.where(df['xCoord'] <0 ,(  -df['yCoord']),(df['yCoord']))
    return df
######################## question 6-2 #######################################


def leagueAverageShotRatePerHour(df):
    """Return a dataframe that contains the total shoots for each coordinate overall 
     plays as well as an average per hour of these totals. 
    :param df: dataframe
    :type df: dataframe
    
    :rtype: DataFrame
    :return: return a dataframe  
    """
    # get number of hours playes, since each game is last 1 hour    
    nbHours = len(df['gameID'].unique())   
    # compute number of shots per (x,y) for the league (all the teams)     
    df_shots = df.groupby(['x_bin', 'y_bin']).agg({'gameID' : 'count'}).reset_index()
    # compute average shots per (x,y) in the league 
    df_shots['avgShotsPerHour'] = df_shots['gameID'] / nbHours
    df =  df_shots.rename(columns={"gameID": "totalShoots"})
    return df


def leagueAverageShotRatePerTeam(df,team):
    """Return a dataframe that contains the number of shots for the given team per coordinates.
    
    :param df:  dataframe
    :type df: dataframe
    
    :param team: name of the team
    :type team: String
    
    :rtype: DataFrame
    :return: return a dataframe  
    """
    teamShots = df.loc[df['teamOfShooter'] == team]
    # compute number of shots for the given team   
    df_team_shots = teamShots.groupby(['x_bin', 'y_bin']).agg({'gameID' : 'count'}).reset_index()
    df = df_team_shots.rename(columns={"gameID": "totalShotsPerTeam"})
    return df

def dataframesCombination(df,team) : 
    """Return a dataframe that merge the last two dataframes in order to calculate the excess shot rate
    
    :param df: dataframe
    :type df: dataframe
    
    :param team: name of the team
    :type team: String
    
    :rtype: DataFrame
    :return: return a dataframe  
    """
    df_shots = leagueAverageShotRatePerHour(df)
    df_team_shots = leagueAverageShotRatePerTeam(df,team)
    jointure =df_team_shots.merge(df_shots, on=['x_bin', 'y_bin'], how='left')
    jointure['excessShotRate'] = jointure['totalShotsPerTeam'] - jointure['avgShotsPerHour']

    return jointure

######################################################################
def selectDataFrame(year) ->pd.DataFrame: 
    """Return a dataframe for a specefic year
    
    :param year: season year
    :type year: int
    
    :rtype: DataFrame
    :return: return a dataframe  
    """
    df = shotsCoordinatedCorrection('./'+str(year)+'finalDataset.csv')
    return df


####################################################################
def teamList(season_year) :
    """Return a list of all teams in order to use it for visualizations ( the list will change depending of the year season)
    
    :param season_year: season year
    :type season_year: int
    
    :rtype: list
    :return: return a list 
    """
    df = pd.read_csv('./'+str(season_year)+'finalDataset.csv')
    list = df.teamOfShooter.unique()
    return list

#########################################

def selectDataFrameForPlotly(season, team)  ->pd.DataFrame: 
    """Return a dataframe for a specefic year and team to use for ploty 
    
    :param season: season year
    :type season: int
    
    :param team: team name
    :type seateamson: String
    
    :rtype: DataFrame
    :return: return a dataframe  
    """
    df = shotsCoordinatedCorrection('./'+str(season)+'finalDataset.csv')
    df = df[df['teamOfShooter'] == team]
    return df
    