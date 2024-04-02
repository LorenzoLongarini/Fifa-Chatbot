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
from rasa_sdk.events import FollowupAction
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

char = [
    "overall",
    "potential"
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
        if slot_value == 'prosegui' or slot_value == '':
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
        if slot_value == 'prosegui' or slot_value == '':
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
        if slot_value == 'prosegui' or slot_value == '':
            return {"preferred_foot": ''}
        else:
            finded = find_values(slot_value, search='preferred_foot', dispatcher = dispatcher)
            if len(finded) == 0:
                dispatcher.utter_message("Inserire Destro o Sinistro")
                return {"preferred_foot": None}
            else:
                {"preferred_foot": finded}
                return [FollowupAction("get_bplayer")]

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
    
class GetModule(Action):
    def name(self) -> Text:
        return "get_module"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        res='Seleziona uno dei seguenti moduli: \n'
        buttons=[]
        for module in modules:
            res += f' - {module}\n'
            buttons.append({
                "module": module,
                "payload": f'/select_module{{"module":"{module}"}}'
                })
            
        dispatcher.utter_button_message(text = res, buttons = buttons)
        print(res, buttons)
        return []
    

class ValidateCreateTeamForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_create_team_form"


    def validate_age(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        
        print(slot_value)
        if slot_value == 'prosegui' or slot_value == '':
            return {"age": ''}
        elif not slot_value.isdigit():
            dispatcher.utter_message("Inserisci un valore numerico")
        else:
            return {"age": slot_value}
    
    def validate_nationality(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        
        print(slot_value)
        if slot_value == 'prosegui' or slot_value == '':
            return {"nationality": ''}
        else:
            finded = find_values(slot_value, search='nationality_name', dispatcher = dispatcher)
            if len(finded) == 0:
                dispatcher.utter_message("Non ho trovato questa nazionalità")
                return {"nationality": None}
            else:
                return {"nationality": finded}

    def validate_characteristic(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        
        print(slot_value)
        if slot_value == 'prosegui' or slot_value == '':
            return {"characteristic": ''}
        else:
            finded = process.extract(str(slot_value), char, limit= 1)
            print(finded)
            if finded[0][1] > 80:
                return {"characteristic": finded[0]}
            else:
                dispatcher.utter_message("Non ho capito, devi inserire \'Overall\' oppure \'Potential\'")
                return {"characteristic": None}

class StopCreateTeamForm(Action):
    def name(self) -> Text:
        return "stop_create_team_form"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

    	#Utters message to inform user form has been cancelled
        dispatcher.utter_message(text="Hai interroto la ricerca!")

        #Clears slots
        return[AllSlotsReset()]

def find_team_players(player_positions, age, nationality, characteristic, head):
    best_players = df[
            (df['player_positions'].str.contains(player_positions, case=False, na=False)) &
            (df['age'].str.contains(age, case=False, na=False)) &
            (df['nationality'].str.contains(nationality, case=False, na=False)) &
            (df['characteristic'].str.contains(characteristic, case=False, na=False))
        ].sort_values(by='overall', ascending=False).head(head)
    return best_players


class GetTeam(Action):
    def name(self) -> Text:
        return "get_team"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        module = tracker.get_slot('module')
        print("ciao",module)
        age = tracker.get_slot('age')
        nationality = tracker.get_slot('nationality')
        characteristic = tracker.get_slot('characteristic')
        if module == modules[0]:
            goalkeeper = find_team_players(player_positions = 'Portiere', age = age, nationality = nationality, characteristic = characteristic, head = 1)
            defenders = find_team_players(player_positions = 'Difensore', age = age, nationality = nationality, characteristic = characteristic, head = 4)
            midfielders = find_team_players(player_positions = 'Centrocampista', age = age, nationality = nationality, characteristic = characteristic, head = 3)
            strikers = find_team_players(player_positions = 'Attaccante', age = age, nationality = nationality, characteristic = characteristic, head = 3)
            if len(goalkeeper == 0) or len(defenders < 4) or len(midfielders < 3) or len(strikers < 3):
                dispatcher.utter_message("Non è possibile creare una squadra rispettando queste condizioni!")
            else:
                response = f"Portiere: \n{goalkeeper['long_name']}:{goalkeeper['age']}, {goalkeeper['nationality']}, {goalkeeper['characteristic']}"
                response += "Difensori: \n" + f"\n".join([f"{defender['long_name']}:{defender['age']}, {defender['nationality']}, {defender['characteristic']}" for defender in defenders]) 
                response += "Centrocampisti: \n" + f"\n".join([f"{midfielder['long_name']}:{midfielder['age']}, {midfielder['nationality']}, {midfielder['characteristic']}" for midfielder in midfielders]) 
                response += "Attaccanti: \n" + f"\n".join([f"{striker['long_name']}:{striker['age']}, {striker['nationality']}, {striker['characteristic']}" for striker in strikers]) 
                dispatcher.utter_message(text=response)

        elif module == modules[1]:
            goalkeeper = find_team_players(player_positions = 'Portiere', age = age, nationality = nationality, characteristic = characteristic, head = 1)
            defenders = find_team_players(player_positions = 'Difensore', age = age, nationality = nationality, characteristic = characteristic, head = 4)
            midfielders = find_team_players(player_positions = 'Centrocampista', age = age, nationality = nationality, characteristic = characteristic, head = 4)
            strikers = find_team_players(player_positions = 'Attaccante', age = age, nationality = nationality, characteristic = characteristic, head = 2)
            if len(goalkeeper == 0) or len(defenders < 4) or len(midfielders < 4) or len(strikers < 2):
                dispatcher.utter_message("Non è possibile creare una squadra rispettando queste condizioni!")
            else:
                response = f"Portiere: \n{goalkeeper['long_name']}:{goalkeeper['age']}, {goalkeeper['nationality']}, {goalkeeper['characteristic']}"
                response += "Difensori: \n" + f"\n".join([f"{defender['long_name']}:{defender['age']}, {defender['nationality']}, {defender['characteristic']}" for defender in defenders]) 
                response += "Centrocampisti: \n" + f"\n".join([f"{midfielder['long_name']}:{midfielder['age']}, {midfielder['nationality']}, {midfielder['characteristic']}" for midfielder in midfielders]) 
                response += "Attaccanti: \n" + f"\n".join([f"{striker['long_name']}:{striker['age']}, {striker['nationality']}, {striker['characteristic']}" for striker in strikers]) 
                dispatcher.utter_message(text=response)
        elif module == modules[2]:
            goalkeeper = find_team_players(player_positions = 'Portiere', age = age, nationality = nationality, characteristic = characteristic, head = 1)
            defenders = find_team_players(player_positions = 'Difensore', age = age, nationality = nationality, characteristic = characteristic, head = 3)
            midfielders = find_team_players(player_positions = 'Centrocampista', age = age, nationality = nationality, characteristic = characteristic, head = 5)
            strikers = find_team_players(player_positions = 'Attaccante', age = age, nationality = nationality, characteristic = characteristic, head = 2)
            if len(goalkeeper == 0) or len(defenders < 3) or len(midfielders < 5) or len(strikers < 2):
                dispatcher.utter_message("Non è possibile creare una squadra rispettando queste condizioni!")
            else:
                response = f"Portiere: \n{goalkeeper['long_name']}:{goalkeeper['age']}, {goalkeeper['nationality']}, {goalkeeper['characteristic']}"
                response += "Difensori: \n" + f"\n".join([f"{defender['long_name']}:{defender['age']}, {defender['nationality']}, {defender['characteristic']}" for defender in defenders]) 
                response += "Centrocampisti: \n" + f"\n".join([f"{midfielder['long_name']}:{midfielder['age']}, {midfielder['nationality']}, {midfielder['characteristic']}" for midfielder in midfielders]) 
                response += "Attaccanti: \n" + f"\n".join([f"{striker['long_name']}:{striker['age']}, {striker['nationality']}, {striker['characteristic']}" for striker in strikers]) 
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
