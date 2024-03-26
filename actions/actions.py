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
from rasa_sdk.forms import FormValidationAction
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

def find_values(input, search, dispatcher):
    matches = process.extract(str(input), df[search].unique(), limit= 5)
    print(matches)
    if len(matches) == 0:     
        return dispatcher.utter_message(text='La squadra inserita non esiste')
    else:
        best_match = matches[0]

        if best_match[1] >= 80:
            return best_match[0]
        else:
            dispatcher.utter_message(text='La percentual è bassa')

class ActionFindTeam(Action):
    def name(self) -> Text:
        return "find_team_action"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):
        
        team = next(tracker.get_latest_entity_values('team'), None)
        if team is not None:
            finded = find_values(team, search='club_name', dispatcher = dispatcher)
            teams =  df[df['club_name'] == (str(finded))] 
            team_infos = teams[columns].to_dict('records')
            response = f"Le squadre con nome {team} sono:\n" + "\n".join([f"- {info['club_name']} : {info['long_name']}" for info in team_infos]) 
            dispatcher.utter_message(text=response)
        else:
            dispatcher.utter_message(text='Non ho capito a quale squadra ti riferisci')


class ValidateSearchBPlayerForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_search_bplayer_form"

    def validate_team(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        

        finded = find_values(slot_value, search='club_name', dispatcher = dispatcher)
        if len(finded) != 0:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"league": finded}
        else:
            dispatcher.utter_message("Non ho trovato un club con questo nome")
            return {"league": None}

    def validate_role(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        

        finded = find_values(slot_value, search='player_positions', dispatcher = dispatcher)
        if len(finded) != 0:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"role": finded}
        else:
            dispatcher.utter_message("Non ho trovato questo ruolo")
            return {"role": None}
        
    def validate_foot(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        

        finded = find_values(slot_value, search='preferred_foot', dispatcher = dispatcher)
        if len(finded) != 0:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"preferred_foot": finded}
        else:
            dispatcher.utter_message("Devi inserire Right o Left")
            return {"preferred_foot": None}

class GetBPlayer(Action):
    def name(self) -> Text:
        return "get_bplayer"

    def run(self,
            #slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        league = tracker.get_slot('league')
        role = tracker.get_slot('role')
        preferred_foot = tracker.get_slot('preferred_foot')
        best_player =  df[(df['club_name'] == str(league)) & (df['player_positions'] == str(role)) & (df['preferred_foot'] == str(preferred_foot))] 

        if len(best_player) == 0:
            dispatcher.utter_message("Non ci sono calciatori che rispettano queste condizioni!")
        else:
            response = f"Il miglior giocatore è :\n" + "\n".join([f"- {info['club_name']} : {info['long_name']}" for info in best_player]) 
            dispatcher.utter_message(text=response)

class ActionHelloWorld(Action):
    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Hello World!")
        return []