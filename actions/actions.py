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
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.events import SlotSet
from rasa_sdk.events import FollowupAction, Restarted
import pandas as pd
import sys
from fuzzywuzzy import process
from rasa_sdk.events import AllSlotsReset
import random
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
    if len(matches) == 0:     
        return []
    else:
        best_match = matches[0]

        if best_match[1] >= 75:
            return best_match[0]
        else:
            return []
        

def find_team_players(player_positions, age, nationality, characteristic, head):
    filtered_df = df[df['player_positions'] == player_positions]
    filtered_df = filtered_df[filtered_df['age'] <= age]
    filtered_df = filtered_df[df['nationality_name'].str.contains(nationality)]
    best_players = filtered_df.sort_values(by=characteristic, ascending=False).head(head)
    return best_players.to_dict('records')


class ActionFindTeam(Action):
    def name(self) -> Text:
        return "find_team_action"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):
        
        team = next(tracker.get_latest_entity_values('team'), None)
        
        if team is not None:
            if len(team) == 0:
                dispatcher.utter_message(text='Esistono più squadre con questo nome, devi essere più specifico. \n Se la squadra ha due nomi, scrivili senza spazi.')
            else:
                finded = find_values(team, search='club_name', dispatcher = dispatcher)
                teams =  df[df['club_name'] == (str(finded))] 
                team_infos = teams[columns].to_dict('records')
                response = f"I giocatori della squadra {team} sono:\n" + "\n".join([f"- {info['club_name']} : {info['long_name']}" for info in team_infos]) 
                dispatcher.utter_message(text=response)
        else:
                dispatcher.utter_message(text='Non ho capito a quale squadra ti riferisci')


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
            response = f"Il giocatore con nome {one_player['long_name']} ha le seguenti caratteristiche:\n" + "\n".join([f"- Ruolo: {one_player['player_positions']} \n- Squadra: {one_player['club_name']} \n- Punteggio complessivo: {one_player['overall']} \n- Valore in euro: {one_player['value_eur']} \n- Età: {one_player['age']}"])
            dispatcher.utter_message(text=response)
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
        
        
        finded = find_values(slot_value, search='long_name', dispatcher = dispatcher)
        if len(finded) == 0 or finded is None:
            dispatcher.utter_message("Non ho trovato questo giocatore")
            return {"player": None}
        else:
            return {"player": finded}
            

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
        
       
        finded = find_values(slot_value, search='long_name', dispatcher = dispatcher)
        if len(finded) == 0 or finded is None:
            dispatcher.utter_message("Non ho trovato questo giocatore")
            return {"player_image": None}
        else:
            return {"player_image": finded}

 
class CompareTwoPlayers(Action):
    def name(self) -> Text:
        return "compare_two_players"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        player_one = tracker.get_slot('player_one')
        player_two = tracker.get_slot('player_two')
        players_one = df[(df['long_name'].str.contains(player_one, case=False, na=False))]
        players_two = df[(df['long_name'].str.contains(player_two, case=False, na=False))]

        if len(players_one) == 0 | len(players_two) == 0:
            dispatcher.utter_message("Non ci sono calciatori che rispettano queste condizioni!")
        else:
            one_player = players_one.iloc[0]
            two_player = players_two.iloc[0]
            #response = f"Ecco l'immagine del giocatore con nome {one_player['long_name']}: URL -> {one_player['player_face_url']}\n"
            response = f"Ecco i due giocatori player_one: {one_player['long_name']} e player_two: {two_player['long_name']}\nVelocità -> {one_player['pace']} vs {two_player['pace']}\nTiro -> {one_player['shooting']} vs {two_player['shooting']}\nPassaggio -> {one_player['passing']} vs {two_player['passing']}\nDribbling -> {one_player['dribbling']} vs {two_player['dribbling']}\nDifesa -> {one_player['defending']} vs {two_player['defending']}\nFisico -> {one_player['physic']} vs {two_player['physic']}\n"
            dispatcher.utter_message(text=response)
        return []

class ValidateComparePlayersForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_compare_players_form"

    def validate_player_one(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        
        if slot_value == 'prosegui':
            return {"player_one": ''}
        else:
            finded = find_values(slot_value, search='long_name', dispatcher = dispatcher)
            if len(finded) == 0:
                dispatcher.utter_message("Non ho trovato questo giocatore")
                return {"player_one": None}
            else:
                return {"player_one": finded}
            
    def validate_player_two(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        
        if slot_value == 'prosegui':
            return {"player_two": ''}
        else:
            finded = find_values(slot_value, search='long_name', dispatcher = dispatcher)
            if len(finded) == 0:
                dispatcher.utter_message("Non ho trovato questo giocatore")
                return {"player_two": None}
            else:
                return {"player_two": finded}


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

        if slot_value == 'prosegui' or slot_value == '':
            return {"league": ''}
        else:
            finded = find_values(slot_value, search='league_name', dispatcher = dispatcher)
            if len(finded) == 0:
                dispatcher.utter_message("Non ho trovato una lega con questo nome")
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


class GetTeam(Action):
    def name(self) -> Text:
        return "get_team"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        module = tracker.get_slot('module')
        age = tracker.get_slot('age')
        age = int(age)
        nationality = tracker.get_slot('nationality')
        characteristic = tracker.get_slot('characteristic')
        if modules[0] in module:
            goalkeepers = find_team_players(player_positions = 'Portiere', age = age, nationality = nationality, characteristic = characteristic, head = 1)
            defenders = find_team_players(player_positions = 'Difensore', age = age, nationality = nationality, characteristic = characteristic, head = 4)
            midfielders = find_team_players(player_positions = 'Centrocampista', age = age, nationality = nationality, characteristic = characteristic, head = 3)
            strikers = find_team_players(player_positions = 'Attaccante', age = age, nationality = nationality, characteristic = characteristic, head = 3)
            if len(goalkeepers) == 0 or len(defenders) < 4 or len(midfielders) < 3 or len(strikers) < 3:
                dispatcher.utter_message("Non è possibile creare una squadra rispettando queste condizioni!")
            else:

                response = f"Portiere: \n"+ f"\n".join([f"{goalkeeper['long_name']}:{goalkeeper['age']}, {goalkeeper['nationality_name']}, {characteristic} : {goalkeeper[characteristic]}" for goalkeeper in goalkeepers]) 
                response += "\nDifensori: \n" + f"\n".join([f"{defender['long_name']}:{defender['age']}, {defender['nationality_name']}, {characteristic} : {defender[characteristic]}" for defender in defenders]) 
                response += "\nCentrocampisti: \n" + f"\n".join([f"{midfielder['long_name']}:{midfielder['age']}, {midfielder['nationality_name']}, {characteristic} : {midfielder[characteristic]}" for midfielder in midfielders]) 
                response += "\nAttaccanti: \n" + f"\n".join([f"{striker['long_name']}:{striker['age']}, {striker['nationality_name']}, {characteristic} : {striker[characteristic]}" for striker in strikers]) 
                dispatcher.utter_message(text=response)

        elif module == modules[1]:

            goalkeepers = find_team_players(player_positions = 'Portiere', age = age, nationality = nationality, characteristic = characteristic, head = 1)
            defenders = find_team_players(player_positions = 'Difensore', age = age, nationality = nationality, characteristic = characteristic, head = 4)
            midfielders = find_team_players(player_positions = 'Centrocampista', age = age, nationality = nationality, characteristic = characteristic, head = 4)
            strikers = find_team_players(player_positions = 'Attaccante', age = age, nationality = nationality, characteristic = characteristic, head = 2)
            if len(goalkeepers) == 0 or len(defenders) < 4 or len(midfielders) < 4 or len(strikers) < 2:
                dispatcher.utter_message("Non è possibile creare una squadra rispettando queste condizioni!")
            else:

                response = f"Portiere: \n"+ f"\n".join([f"{goalkeeper['long_name']}:{goalkeeper['age']}, {goalkeeper['nationality_name']}, {characteristic} : {goalkeeper[characteristic]}" for goalkeeper in goalkeepers]) 
                response += "\nDifensori: \n" + f"\n".join([f"{defender['long_name']}:{defender['age']}, {defender['nationality_name']}, {characteristic} : {defender[characteristic]}" for defender in defenders]) 
                response += "\nCentrocampisti: \n" + f"\n".join([f"{midfielder['long_name']}:{midfielder['age']}, {midfielder['nationality_name']}, {characteristic} : {midfielder[characteristic]}" for midfielder in midfielders]) 
                response += "\nAttaccanti: \n" + f"\n".join([f"{striker['long_name']}:{striker['age']}, {striker['nationality_name']}, {characteristic} : {striker[characteristic]}" for striker in strikers]) 
                dispatcher.utter_message(text=response)
        elif module == modules[2]:

            goalkeepers = find_team_players(player_positions = 'Portiere', age = age, nationality = nationality, characteristic = characteristic, head = 1)
            defenders = find_team_players(player_positions = 'Difensore', age = age, nationality = nationality, characteristic = characteristic, head = 3)
            midfielders = find_team_players(player_positions = 'Centrocampista', age = age, nationality = nationality, characteristic = characteristic, head = 5)
            strikers = find_team_players(player_positions = 'Attaccante', age = age, nationality = nationality, characteristic = characteristic, head = 2)
            if len(goalkeepers) == 0 or len(defenders) < 3 or len(midfielders) < 5 or len(strikers) < 2:
                dispatcher.utter_message("Non è possibile creare una squadra rispettando queste condizioni!")
            else:

                response = f"\nPortiere: \n"+ f"\n".join([f"{goalkeeper['long_name']}:{goalkeeper['age']}, {goalkeeper['nationality_name']}, {characteristic} : {goalkeeper[characteristic]}" for goalkeeper in goalkeepers]) 
                response += "\nDifensori: \n" + f"\n".join([f"{defender['long_name']}:{defender['age']}, {defender['nationality_name']}, {characteristic} : {defender[characteristic]}" for defender in defenders]) 
                response += "\nCentrocampisti: \n" + f"\n".join([f"{midfielder['long_name']}:{midfielder['age']}, {midfielder['nationality_name']}, {characteristic} : {midfielder[characteristic]}" for midfielder in midfielders]) 
                response += "\nAttaccanti: \n" + f"\n".join([f"{striker['long_name']}:{striker['age']}, {striker['nationality_name']}, {characteristic} : {striker[characteristic]}" for striker in strikers]) 
                dispatcher.utter_message(text=response)
        return []

    
class ValidateCreateTeamForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_create_team_form"

    def validate_module(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:


        if slot_value not in modules:
            dispatcher.utter_message(text = f"Devi inserire un modulo valido!")
            return {"module": None}
        else:
            return {"module": slot_value}

    def validate_age(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        
        if slot_value == 'prosegui' or slot_value == '':
            return {"age": df['age'].max()}
        elif not slot_value.isdigit():
            dispatcher.utter_message("Inserisci un valore numerico")
            return {"age": None}
        else:
            return {"age": slot_value}
    
    def validate_nationality(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        
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
      
        if slot_value == 'prosegui' or slot_value == '':
            random_value = random.choice(char)
            return {"characteristic": random_value}
        else:
            finded = process.extract(str(slot_value), char, limit= 1)
            if finded[0][1] > 80:
                return {"characteristic": finded[0][0]}
            else:
                dispatcher.utter_message("Non ho capito, devi inserire \'Overall\' oppure \'Potential\'")
                return {"characteristic": None}


class ResetSlot(Action):

    def name(self):
        return "action_reset_slot"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Ora puoi chiedermi qualcos'altro!")
        return [AllSlotsReset()]
            
