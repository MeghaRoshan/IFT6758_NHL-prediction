import json
import requests
import pandas as pd
import logging
from ift6758.ift6758.client.serving_client import ServingClient
from ift6758.ift6758.data.loadGameData import PreprocessData

logger = logging.getLogger(__name__)
logger.info(f"Initializing ClientGame ")
s = ServingClient("127.0.0.1", port = 8890)

class GameClient:
    def __init__(self):
        self.tracker = 0
    def update_model_df_length(self):
        self.model_df_length = self.game.shape[0]
    def pingGame (self,gameId ,idx= 0):
        df, last_idx = PreprocessData(gameId, idx)
        x_test = df[['periodSeconds',	'last_period',	'last_eventxCoord',	'last_eventyCoord',	'last_periodSeconds', 'last_Distance_from_net',	'last_Angle_from_net',	'time_from_last_event',	'distance_from_last_event',	'rebound',	'change_in_angle',	'speed']]
        predictions = s.predict(x_test).reset_index().drop(columns ='index')
        df_add = df[['gameID','period','periodTime','teamOfShooter', 'homeTeam','AwayTeam','timeLeft','eventType']].reset_index().drop(columns ='index')
        result =pd.concat([df_add,predictions],axis=1)
        self.update_model_df_length()
        tracker = self.model_df_length
        return result, last_idx, tracker
        
    
