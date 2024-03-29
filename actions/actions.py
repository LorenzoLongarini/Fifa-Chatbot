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
from rasa_sdk.events import SlotSet
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

modules = [
    '4-3-3',
    '4-4-2',
    '3-5-2'
]

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
        return "validate_bplayer_form"


    def validate_role(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        
        print(slot_value)
        if slot_value == 'prosegui':
            return {"role": ''}
        else:
            finded = find_values(slot_value, search='player_positions', dispatcher = dispatcher)
            if len(finded) == 0:
                dispatcher.utter_message("Non ho trovato questo ruolo")
                return {"role": None}
            else:
                return {"role": finded}
        
    
    def validate_league(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        
        print(slot_value)
        if slot_value == 'prosegui':
            return {"league": ''}
        else:
            finded = find_values(slot_value, search='league_name', dispatcher = dispatcher)
            if len(finded) == 0:
                dispatcher.utter_message("Non ho trovato un club con questo nome")
                return {"league": None}
            else:
                return {"league": finded}

    def validate_preferred_foot(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        
        print(slot_value)
        if slot_value == 'prosegui':
            return {"preferred_foot": ''}
        else:
            finded = find_values(slot_value, search='preferred_foot', dispatcher = dispatcher)
            if len(finded) == 0:
                dispatcher.utter_message("Inserire Destro o Sinistro")
                return {"preferred_foot": None}
            else:
                return {"preferred_foot": finded}

class StopGetBPlayerForm(Action):
    def name(self) -> Text:
        return "stop_get_bplayer_form"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

    	#Utters message to inform user form has been cancelled
        dispatcher.utter_message(text="Hai interroto la ricerca!")

        #Clears slots
        # return[SlotSet(SlotSet("company_location", None),SlotSet("company_name", None),SlotSet("company_source", None)]
        return[AllSlotsReset()]

class GetBPlayer(Action):
    def name(self) -> Text:
        return "get_bplayer"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        league = tracker.get_slot('league')
        role = tracker.get_slot('role')
        preferred_foot = tracker.get_slot('preferred_foot')
        best_players = df[
            (df['league_name'].str.contains(league, case=False, na=False)) &
            (df['player_positions'].str.contains(role, case=False, na=False)) &
            (df['preferred_foot'].str.contains(preferred_foot, case=False, na=False))
        ].sort_values(by='overall', ascending=False)

        if len(best_players) == 0:
            dispatcher.utter_message("Non ci sono calciatori che rispettano queste condizioni!")
        else:
            best_player = best_players.iloc[0]
            response = (f"Il miglior giocatore è: {best_player['short_name']}, "
                        f"che gioca in {best_player['league_name']} come {best_player['player_positions']},"
                        f"con piede preferito {best_player['preferred_foot']} e overall {best_player['overall']}.")
            dispatcher.utter_message(text=response)
        return []
    
# class GetModule(Action):
#     def name(self) -> Text:
#         return "get_module"

#     def run(self,
#             slot_value: Any,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         res='Seleziona uno dei seguenti moduli: \n'
#         buttons=[]
#         for module in modules:
#             res=res+f' - {module[0]}\n'
#             buttons.append({"module": module[0], "payload": f'/viewBrandProduct{{"brand":"{elem[0]}"}}'})
#         dispatcher.utter_button_message(brd,buttons)


class ResetSlot(Action):

    def name(self):
        return "action_reset_slot"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Ora puoi chiedermi qualcos'altro!")
        return [AllSlotsReset()]
