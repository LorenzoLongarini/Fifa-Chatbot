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

PATH = 'dataset/male_player_clear.csv'
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


class ActionFindPlayer(Action):

    def name(self) -> Text:
        return "find_player_action"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):
        name = tracker.get_slot('player_name')  # Assicurati di estrarre correttamente l'entità
        result = df[df['short_name'].str.contains(name, case=False, na=False)]
        
        if result.empty:
            dispatcher.utter_message(text='Non ci sono calciatori con questo nome')
        else:
            player_infos = result[columns].drop_duplicates().to_dict('records')
            response = f"I calciatori con nome {name} sono:\n" + "\n".join([f"- {info['short_name']}, Club: {info['club_name']}" for info in player_infos])
            dispatcher.utter_message(text=response)
        
        # name = tracker.latest_message['entities'][0]['value']
        # dispatcher.utter_message(text="Hello World!")
        # result = df.loc[df['short_name'] == name]

        # if len(result)==0:
        #     dispatcher.utter_message('Non ci sono calciatori con questo nome')
        # else:
        #     pl = f'I calciatori con nome {name} sono: \n'
        #     for elem in result:
        #         if not elem[0] in pl:
        #             pl=pl+f' - {elem[0]}, '


        return []

class ActionHelloWorld(Action):
    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Hello World!")
        return []