# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import pandas as pd
import sys
from fuzzywuzzy import process
# sys.path.append('../utils')
# from utils.utility import find_words as fw

PATH = 'dataset/male_players_clear.csv'
df = pd.read_csv(PATH)
columns= ['player_id',
'player_face_url',
'fifa_version',
'short_name',
'long_name',
'player_positions',
'overall',
'potential',
'value_eur',
'age',
'height_cm',
'weight_kg',
'league_name',
'league_id',
'club_name',
'club_team_id',
'club_jersey_number',
'nationality_name',
'nationality_id',
'preferred_foot',
'pace',
'shooting',
'passing',
'dribbling',
'defending',
'physic']

def find_team(input, search, dispatcher):
    matches = process.extract(input, df[search].unique(), limit= 5)
    print(matches)
    best_match = matches[0]
    print(best_match)
    if best_match[1] >= 80:
        return best_match[0]
    else:
         dispatcher.utter_message(text='La squadra inserita non esiste')

class ActionFindTeam(Action):
    def name(self) -> Text:
        return "find_team_action"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):
        
        team = next(tracker.get_latest_entity_values('team'), None)
        finded = find_team(team, search='club_name', dispatcher = dispatcher)
        teams =  df[df['club_name'].str.contains(finded, case=False, na=False)]
        
        team_infos = teams[columns].to_dict('records')
        response = f"Le squadre con nome {team} sono:\n" + "\n".join([f"- {info['club_name']} : {info['long_name']}" for info in team_infos]) 
        dispatcher.utter_message(text=response)





# class ActionFindPlayer(Action):

#     def name(self) -> Text:
#         return "find_player_action"

#     def run(self, 
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: DomainDict):
#         player_name = tracker.get_slot('player_name')
#         player_team = tracker.get_slot('player_team')
#         player_age = tracker.get_slot('player_age')
#         # name = next(tracker.get_latest_entity_values('player_name'), None)
#         # name = tracker.get_slot('tipo_prodotto')

#         if not player_name:
#             dispatcher.utter_message(text='Per favore, specifica il nome di un calciatore.')
#             return []
        
#         results = df[df['long_name'].str.contains(player_name, case=False, na=False)]

#         if len(results) > 1:
#             return ["player_name", "player_team", "player_age"]
#         elif len(results) == 1:
#             return ["player_name"]
        
#         if result_long.empty:
#             dispatcher.utter_message(text='Non ci sono calciatori con questo nome')
#         # elif len(result_long) == 1:
#         #     # player = result_long.iloc[0]
#         #     player_infos = result_long[columns].to_dict('records')
#         #     response = f"Il calciatori con nome {name} è:\n" + "\n".join([f"- {result_long['short_name']}, Club: {result_long['club_name']}"])
#         #     dispatcher.utter_message(text=response)
#         else:
#             player_infos = result_long[columns].to_dict('records')
#             response = f"I calciatori con nome {name} sono:\n" + "\n".join([f"- {info['short_name']}, Club: {info['club_name']}" for info in player_infos]) 
#             dispatcher.utter_message(text=response)
        
#         # name = tracker.latest_message['entities'][0]['value']
#         # dispatcher.utter_message(text="Hello World!")
#         # result = df.loc[df['short_name'] == name]

#         # if len(result)==0:
#         #     dispatcher.utter_message('Non ci sono calciatori con questo nome')
#         # else:
#         #     pl = f'I calciatori con nome {name} sono: \n'
#         #     for elem in result:
#         #         if not elem[0] in pl:
#         #             pl=pl+f' - {elem[0]}, '


#         return []

# class ActionGetPlayerAge(Action):
#     def name(self) -> Text:
#         return "action_get_player_age"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
#         name = next(tracker.get_latest_entity_values('player_name'), None)

#         result = df[df['short_name'].str.contains(name, case=False, na=False)]
        
#         if result.empty:
#             dispatcher.utter_message(text='Non ci sono calciatori con questo nome')
#         else:
#             # player_age = result['age'].drop_duplicates().to_dict('records')
#             # first_player_age = result.iloc[0]['age']
#             # dispatcher.utter_message(text=f"L'età del giocatore {name} è {first_player_age}.")
#             player_infos = result[columns].drop_duplicates().to_dict('records')
#             response = f"I calciatori con nome {name} hanno le seguenti eta:\n" + "\n".join([f"- {info['short_name']}, Eta: {info['age']}" for info in player_infos])
#             dispatcher.utter_message(text=response)
        

#         return []

class ActionHelloWorld(Action):
    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Hello World!")
        return []