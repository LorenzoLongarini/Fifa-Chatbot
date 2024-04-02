# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import pandas as pd
import sys
from fuzzywuzzy import process
from rasa_sdk.events import AllSlotsReset
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

def find_values(input, search, dispatcher):
    matches = process.extract(str(input), df[search].unique(), limit= 5)
    print(matches)
    if len(matches) == 0:     
        return []
    else:
        best_match = matches[0]

        if best_match[1] >= 80:
            return best_match[0]
        else:
            return []

class ValidatePlayerForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_player_form"

    def validate_player(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        
        print(slot_value)
        if slot_value == 'prosegui':
            return {"player": ''}
        else:
            finded = find_values(slot_value, search='long_name', dispatcher = dispatcher)
            if len(finded) == 0:
                dispatcher.utter_message("Non ho trovato questo giocatore")
                return {"player": None}
            else:
                return {"player": finded}
            
class ValidatePlayerImageForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_player_image_form"

    def validate_player_image(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        
        print(slot_value)
        if slot_value == 'prosegui':
            return {"player_image": ''}
        else:
            finded = find_values(slot_value, search='long_name', dispatcher = dispatcher)
            if len(finded) == 0:
                dispatcher.utter_message("Non ho trovato questo giocatore")
                return {"player_image": None}
            else:
                return {"player_image": finded}

    

class GetPlayer(Action):
    def name(self) -> Text:
        return "get_player"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        player = tracker.get_slot('player')
        players = df[(df['long_name'].str.contains(player, case=False, na=False))]

        if len(players) == 0:
            dispatcher.utter_message("Non ci sono calciatori che rispettano queste condizioni!")
        else:
            one_player = players.iloc[0]
            response = f"Il giocatore con nome {one_player['long_name']} ha le seguenti caratteristiche:\n" + "\n".join([f"- Positions: {one_player['player_positions']} \n- Club name: {one_player['club_name']} \n- Overall: {one_player['overall']} \n- Value in euros: {one_player['value_eur']} \n- Age: {one_player['age']}"])
            dispatcher.utter_message(text=response)
        return []


class GetPlayerImage(Action):
    def name(self) -> Text:
        return "get_player_image"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        player = tracker.get_slot('player_image')
        players = df[(df['long_name'].str.contains(player, case=False, na=False))]

        if len(players) == 0:
            dispatcher.utter_message("Non ci sono calciatori che rispettano queste condizioni!")
        else:
            one_player = players.iloc[0]
            response = f"Ecco l'immagine del giocatore con nome {one_player['long_name']}: URL -> {one_player['player_face_url']}\n"
            dispatcher.utter_message(text=response)
        return []
    

class ResetSlot(Action):

    def name(self):
        return "action_reset_slot"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Ora puoi chiedermi qualcos'altro!")
        return [AllSlotsReset()]