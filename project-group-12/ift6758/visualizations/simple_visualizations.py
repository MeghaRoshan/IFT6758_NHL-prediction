import numpy as np
import pandas as pd
######################## question 5-1 #######################################
def simple_visualisation_1 (path) -> pd.DataFrame: 
    """Return an aggregated dataframe which count the number of games for each eventType and shotType and sort them 
        to have a nice visualization.
 
    :param path: path of the dataframe
    :type path: String
    
    :rtype: DataFrame
    :return: return a dataframe  
    """
    df = pd.read_csv(path)
    df = df.groupby(['eventType', 'shotType'])
    df= df.size().reset_index().rename(columns={0: "count"})
    df = df.sort_values(by=['eventType'], ascending=False)
    return df


def simple_visualisation_1_percentage (path) -> pd.DataFrame: 
    """Return an aggregated dataframe which count the percnetage of the number goals and shoots for each shotType.
 
    :param path: path of the dataframe
    :type path: String
    
    :rtype: DataFrame
    :return: return a dataframe  
    """
    df = simple_visualisation_1(path)
    df =pd.pivot_table(df, values='count', index=['shotType'],
                    columns=['eventType'], aggfunc=sum, fill_value=0).reset_index()
    df['somme'] = df['Goal'] + df['Shot']
    df['Goal']  =  df['Goal']/df['somme']
    df['Shot']  =  df['Shot'] /df['somme']
    df = df.drop(['somme'], axis=1)
    return df

######################## question 5-2 #######################################
def rinkSideMissingValues (path) -> pd.DataFrame: 
    """Return a dataframe with no null values of rinkSide variable. 
 
    :param path: path of the dataframe
    :type path: String
    
    :rtype: DataFrame
    :return: return a dataframe  
    """
    df = pd.read_csv(path)
    # create nets coordinates 
    df['X_net_left'] = -99 
    df['Y_nett'] = 0 
    df['X_net_rght'] = 99
    # calculate the distance of the shot from both nets
    df['DistanceFromLeftNet'] = ((df["xCoord"] - df["X_net_left"])**2 + (df["yCoord"] - df["Y_nett"])**2)**0.5
    df['DistanceFromRightNet'] =  ((df["xCoord"] - df["X_net_rght"])**2 + (df["yCoord"] - df["Y_nett"])**2)**0.5
    
    #our new rinkside 
    df['new_rinkSide'] = np.where(df['DistanceFromLeftNet'] <df['DistanceFromRightNet'],'right','left')
    #filling the null values of the rinkside with the new values 
    df['rinkSide']= np.where(df['rinkSide'].isna(),df['new_rinkSide'],df['rinkSide'])
    df = df.drop(['new_rinkSide','DistanceFromLeftNet', 'DistanceFromRightNet'], axis =1)
    return df


def shootsDistance (path) -> pd.DataFrame:
    """Return a dataframe with shot distances from the net.
 
    :param path: path of the dataframe
    :type path: String
    
    :rtype: DataFrame
    :return: return a dataframe  
    """
    df = rinkSideMissingValues (path)
    df['shootDistance'] = np.round(np.where(df['rinkSide'] =='right',(((df["xCoord"] - df["X_net_left"])**2 + (df["yCoord"] - df["Y_nett"])**2)**0.5), (((df["xCoord"] - df["X_net_rght"])**2 + (df["yCoord"] - df["Y_nett"])**2)**0.5)))
    df = df.drop(['X_net_left','Y_nett', 'X_net_rght'], axis =1)
    		
    return df

def simple_visualisation_distance (path) -> pd.DataFrame:
    """Return an aggregated dataframe. we count the number of games for each  shot distance and for each event type
 
    :param path: path of the dataframe
    :type path: String
    
    :rtype: DataFrame
    :return: return a dataframe  
    """
    df = shootsDistance(path)
    df1 = df.groupby(['shootDistance', 'eventType'])
    df1= df1.size().reset_index().rename(columns={0: "count"})
    #for a better vizualisation we take off the shoots that were shooted brom before the center
    df1 = df1[df1['shootDistance']<= 100]
    return df1


def simple_visualisation_goalRation (path) -> pd.DataFrame: 
    """Return an aggregated dataframe. we calculate the percnetgae of goals and shoots for each  shot distance.
    :param path: path of the dataframe
    :type path: String
    
    :rtype: DataFrame
    :return: return a dataframe  
    """
    df = shootsDistance(path)
    df = df.groupby(['eventType', 'shootDistance'])
    df= df.size().reset_index().rename(columns={0: "count"})
    df =pd.pivot_table(df, values='count', index=['shootDistance'],
                    columns=['eventType'], aggfunc=sum, fill_value=0).reset_index()
    df['somme'] = df['Goal'] + df['Shot']
    df['Goal']  =  df['Goal']/df['somme']
    df['Shot']  =  df['Shot'] /df['somme']
    df = df[df['shootDistance']<= 100]
    df= df.drop(['somme'], axis=1)
    return df

######################## question 5-3 #######################################

def simple_visualisation_combination (path) -> pd.DataFrame: 
    """Return an aggregated dataframe that combine between the last two functions data
    :type path: String
    
    :rtype: DataFrame
    :return: return a dataframe  
    """
    df = shootsDistance(path)
    df['distanceCluster'] = np.where ( (df['shootDistance']<= 10) & (df['shootDistance']>0) , 1, 
                                     np.where((df['shootDistance']<= 20  ) & ( df['shootDistance']>10),2,
                                             np.where((df['shootDistance']<= 50  ) & ( df['shootDistance']>20),3,
                                                     np.where((df['shootDistance']<= 75  ) & (df['shootDistance']>50 ),4,5))
                                             ))
    df = df.groupby(['eventType', 'shootDistance','shotType','distanceCluster'])
    df= df.size().reset_index().rename(columns={0: "count"})
    df =pd.pivot_table(df, values='count', index=['distanceCluster','shootDistance','shotType'],
                    columns=['eventType'], aggfunc=sum, fill_value=0).reset_index()
    df['somme'] = df['Goal'] + df['Shot']
    df['Goal']  =  df['Goal']/df['somme']
    df['Shot']  =  df['Shot'] /df['somme']
    df = df[df['shootDistance']<= 100]

    df= df.drop(['somme'], axis=1)
    return df