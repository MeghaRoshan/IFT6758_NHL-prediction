import numpy as np
import pandas as pd
import math


def AddIsGoalFeature (df)  -> pd.DataFrame:   
    df['Is_goal'] = np.where(df['eventType'] == 'Goal', 1, 0)
    return df

def AddEmptyNetFeature (df)  -> pd.DataFrame:   
    df['empty_Net'] = np.where(df['emptyNet']== True, 1,0)
    return df

def rinkSideMissingValues2 (df) -> pd.DataFrame: 
    """Return a dataframe with no null values of rinkSide variable.
    
    :rtype: DataFrame
    :return: return a dataframe  
    """
    # create nets coordinates 
    df['X_net_left'] = -89 
    df['Y_net'] = 0 
    df['X_net_rght'] = 89
    # calculate the distance of the shot from both nets
    df['DistanceFromLeftNet'] = ((df["xCoord"] - df["X_net_left"])**2 + (df["yCoord"] - df["Y_net"])**2)**0.5
    df['DistanceFromRightNet'] =  ((df["xCoord"] - df["X_net_rght"])**2 + (df["yCoord"] - df["Y_net"])**2)**0.5
    
    #our new rinkside 
    df['new_rinkSide'] = np.where(df['DistanceFromLeftNet'] <df['DistanceFromRightNet'],'right','left')

    #filling the null values of the rinkside with the new values 
    df['rinkSide']= np.where(df['rinkSide'].isna(),df['new_rinkSide'],df['rinkSide'])
    df['X_net'] = np.where(df['rinkSide'] =='right', - 89,89)
    df = df.drop(['new_rinkSide','DistanceFromLeftNet', 'DistanceFromRightNet'], axis =1)
    return df


def addDistanceFromNet (df)-> pd.DataFrame: 
    df = rinkSideMissingValues2(df)
    df['Distance_from_net'] = np.where(df.xCoord is None or df.yCoord is None,
                                            None,((df["xCoord"] - df["X_net"])**2 + (df["yCoord"])**2)**0.5  )
    return df

def addAngleFromNet (df) -> pd.DataFrame:
    df = addDistanceFromNet (df)
    df["Angle_from_net"]  = df.apply( lambda row :  math.degrees(math.atan2(row.yCoord , row.xCoord -row.X_net)) if 
                                     (row.xCoord < 90)   else  math.degrees(math.atan2(row.yCoord , row.xCoord -row.X_net)),
                                     axis=1 , result_type="expand" )
    return df
        

def combineAllFeatures (df) -> pd.DataFrame: 
    """Return a dataframe with Distance and angle of the shot from the net
    """
    df1 = AddIsGoalFeature (df)
    df2 = AddEmptyNetFeature (df1)  
    df3 = addAngleFromNet (df2)
    return df3