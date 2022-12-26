import streamlit as st
import pandas as pd
import json
import numpy as np
from game_client import GameClient
from serving_client import ServingClient
import traceback
import datetime


from comet_ml import API

api_key='BDQ0IvlidYZwCjQubkQCX7cs0' 
api = API(api_key)

gc = GameClient()
sc = ServingClient("serving", port = 8890)
"""
General template for your streamlit app. 
Feel free to experiment with layout and adding functionality!
Just make sure that the required functionality is included as well
"""

st.title("Hockey Visualization App")

with st.sidebar:
    # TODO: Add input for the sidebar
    workspace = st.text_input('Workspace', 'Workspace x') #yasmine
    model = st.text_input('Model', 'Model y') #"model-xgboost-final2"
    version = st.text_input('Version', 'Version z')#"1.0.0"
    if st.button('Get Model'):
        print(workspace)
        print(model)
        print(version)
        sc.download_registry_model(
            workspace=workspace,
            model=model,
            version=version
        )
        st.write('Model Downloaded')
        if 'track_download_model' not in st.session_state and 'previous_track_download_model' not in st.session_state:
            st.session_state['track_download_model'] = 1
            st.session_state['previous_track_download_model'] = 1
        else:
            st.session_state['track_download_model'] += 1

def ping_game_id(game_id):
    with st.container():
        # Keep the game_id in session_state
        if 'game_id' not in st.session_state:
            st.session_state['game_id'] = game_id
        if st.session_state.game_id != game_id and 'track_download_model' not in st.session_state and 'previous_track_download_model' not in st.session_state:
            st.session_state['track_download_model'] = 1
            st.session_state['previous_track_download_model'] = 1
        elif st.session_state.game_id != game_id and 'track_download_model' in st.session_state and 'previous_track_download_model' in st.session_state:
            if st.session_state['track_download_model'] == (st.session_state['previous_track_download_model'] + 1):
                st.session_state.game_id = game_id
                st.session_state['previous_track_download_model'] = st.session_state['track_download_model']
        # Initialization of session variables to track the dataframe length
        # st.session_state preserves the state of the variables between different reruns
        # session_state is the key functionality in streamlit app
        if 'session_tracker' not in st.session_state and 'previous_session_tracker' not in st.session_state:
            st.session_state['session_tracker'] = 0
            st.session_state['previous_session_tracker'] = 0
            # st.write(st.session_state.session_tracker)
            # st.write(st.session_state.previous_session_tracker)
        if st.session_state.game_id != game_id:
            st.session_state['session_tracker'] = 0
            st.session_state['previous_session_tracker'] = 0
            st.write("Model trained on different game id should not predict goal probabilities of different game id. "
                     "Please download the model again and perform prediction for this new game id.")
            # st.write("We have used the 'event type' feature and since this feature does not have all the "
            #          "types used by the previous game id, therefore, you should train your model "
            #          "again with the new events set to get the predictions and avoid Features Mismatch Problem."
            #          "Please stop the application service and retrain your model again on new game id.")
        try:
            
            if st.session_state['game_id'] == game_id:
                # Get the filepath of the recent game_id downloaded json
                #filepath = gc.get_game(game_id=game_id)
                # Get the dataframe, last event, and dataframe_length
                model_df, last_event_df_index, new_dataframe_length = gc.pingGame(game_id)
                #model_df.drop(model_df.columns[len(model_df.columns)-1], axis=1, inplace=True)
                last_event_df = model_df.iloc[-1]
                
            # If the session ran already, then the session_tracker should update with
            # new length that is newly loaded dataframe length - old evaluated dataframe length
            if 'session_tracker' in st.session_state and st.session_state.session_tracker > 0 and st.session_state['game_id'] == game_id:
                # st.write(st.session_state.session_tracker)
                st.session_state['session_tracker'] = new_dataframe_length - st.session_state.session_tracker
                # st.write(st.session_state.session_tracker)
            # If there is zero event for this session the session_tracker will become 0
            # but previous session tracker holds the result of last dataframe length value
            if st.session_state.session_tracker == 0 and st.session_state.previous_session_tracker > 0 and st.session_state['game_id'] == game_id:
                st.write("Displaying same dashboard as previous because there are " + str(st.session_state.session_tracker) + " new events!")
                st.session_state['previous_session_tracker'] = new_dataframe_length - st.session_state.previous_session_tracker
            # If current session and previous session have dataframe length then it has new events
            if st.session_state.session_tracker > 0 and st.session_state.previous_session_tracker > 0 and st.session_state['game_id'] == game_id:
                
                st.write("There are total " + str(st.session_state.session_tracker) + " new events!")
                st.session_state['previous_session_tracker'] = new_dataframe_length - st.session_state.previous_session_tracker
            # If both session and previous session do not have the events then it load is first time for game id
            if st.session_state.session_tracker == 0 and st.session_state.previous_session_tracker == 0 and st.session_state['game_id'] == game_id:
                st.session_state['previous_session_tracker'] = new_dataframe_length
                st.session_state['session_tracker'] = new_dataframe_length
            # If both current session and previous session have values
            # then we should get the dataframe with only new values
            if st.session_state.session_tracker > 0 and st.session_state.previous_session_tracker > 0 and st.session_state['game_id'] == game_id:
                model_df = model_df.copy()
                model_df = model_df.iloc[-st.session_state.session_tracker:]
                new_model_df=model_df.drop(columns=['homeTeam','AwayTeam','Is_goal','teamOfShooter','periodTime','timeLeft','period'])
                #print(new_model_df)
                st.session_state.session_tracker = new_dataframe_length
                st.session_state.previous_session_tracker = new_dataframe_length
            # Current and Previous session values will be equal once we will reach at the state of predicting the model
            # because we set both session variables as same values
            # so that in next run previous session will give us the value of this run
            if st.session_state.session_tracker == st.session_state.previous_session_tracker and st.session_state['game_id'] == game_id:
                print("I am in Streamlit.....")
                preds = sc.predict(new_model_df)
                try:
                    preds= preds.to_json()
                    preds = json.loads(preds)
                
                    #preds = [pred for pred in preds['0'].values()]
                    print(model_df)
                    preds=list(preds["probaIsGoal"].values())
                    model_df["Model Output"] = preds
                    
                    model_df.Is_goal = model_df.Is_goal.astype(str)
                    
                    # Calculating the predict and actual goals probability
                    grouped_prob_df = model_df.where(model_df.Is_goal == "1.0").groupby("teamOfShooter")["Model Output"].agg("sum").round(decimals=2)
                    
                    grouped_goal_df = model_df.where(model_df.Is_goal == "1.0").groupby("teamOfShooter")["Is_goal"].count()
                    
                    grouped_prob_df = pd.DataFrame(grouped_prob_df).transpose()
                    grouped_goal_df = pd.DataFrame(grouped_goal_df).transpose()
                    last_event_df = pd.DataFrame(last_event_df).transpose()
                    last_event_df = last_event_df.reset_index()
                   
                    # If the team did not acquire any goal then put zero goals for that team
                    if len(grouped_prob_df) < 2:
                        if str(model_df.homeTeam[0]) not in grouped_prob_df.columns:
                            grouped_prob_df[model_df.homeTeam[0]] = 0
                        if str(model_df.AwayTeam[0]) not in grouped_prob_df.columns:
                            grouped_prob_df[model_df.AwayTeam[0]] = 0
                    if len(grouped_goal_df) < 2:
                        if str(model_df.homeTeam[0]) not in grouped_goal_df.columns:
                            grouped_goal_df[model_df.homeTeam[0]] = 0
                        if str(model_df.AwayTeam[0]) not in grouped_goal_df.columns:
                            grouped_goal_df[model_df.AwayTeam[0]] = 0
                    last_event_df.period= last_event_df.period[0].astype(str)
                    # Calculating the time left in period
                    #time_remain_df = str(pd.DataFrame(pd.to_datetime("20:00", format="%M:%S")
                                 #- pd.to_datetime(last_event_df["periodTime"], format="%M:%S"))['periodTime'][0])
                    
                    st.subheader("Game " + str(game_id) + ": " + str(model_df.homeTeam[0]) + " vs " + str(model_df.AwayTeam[0]))
                    st.text("Period " + last_event_df.period[0].astype(str)+ " - "+ str(datetime.timedelta(seconds=(last_event_df.timeLeft[0]))) + " left")
                    #st.text("Period " + str(last_event_df.period[0]) + " - "
                        #   + str(model_df.timeLeft + " left"))
                    
                    # Arranging the values in two columns
                    col1, col2 = st.columns(2)
                    col1.metric(label=str(model_df.homeTeam[0]) + " xG(actual)", value=str(grouped_prob_df[model_df.homeTeam[0]][0])+" ("
                                                                                      + str(grouped_goal_df[model_df.homeTeam[0]][0])
                                                                                      + ")",
                    delta=str(float(float(grouped_goal_df[model_df.homeTeam[0]][0])-float(
                                  grouped_prob_df[model_df.homeTeam[0]][0])).__round__(2)))
                    col2.metric(label=str(model_df.AwayTeam[0]) + " xG(actual)",
                              value=str(grouped_prob_df[model_df.AwayTeam[0]][0]) + " ("+ str(grouped_goal_df[model_df.AwayTeam[0]][0])+")",
                              delta=str(float(float(grouped_goal_df[model_df.AwayTeam[0]][0]) - float(
                                  grouped_prob_df[model_df.AwayTeam[0]][0])).__round__(2)))
                    
                    with st.container():
                        # Fetching the entire dataframe
                        st.subheader("Data used for predictions (and predictions)")
                        st.table(model_df)
                except Exception as e:
                    print(e)
                    pass
        except Exception as e:
                st.write("Please turn on your prediction service.")
                print(e)
                print(traceback.format_exc())
                st.session_state['session_tracker'] = 0
                st.session_state['previous_session_tracker'] = 0


with st.container():
    # This is the ping game container consists of the Game ID and button
    game_id = st.text_input('Game ID', '2021020329')
    if st.button('Ping game'):
        ping_game_id(game_id)

    
