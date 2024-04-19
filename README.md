# Fifa-Chatbot
La repository "Fifa-Chatbot" è un progetto innovativo che combina il mondo del gioco del calcio con l'intelligenza artificiale per offrire un'esperienza interattiva agli appassionati di FIFA. EA Sport It's in the game!


1. Create venv:
```
python3 -m venv ./venv
```

2. Activate:
```
.\venv\Scripts\activate
```

3. Install requirements:
```
pip install requirements.txt
```

4. Download dataset:
```
https://www.kaggle.com/datasets/stefanoleone992/fifa-23-complete-player-dataset?resource=download&select=male_players.csv
```

5. Run: 
```
clear.ipynb in ./utils
```

6. Create credentials.yml file

7. Run:
```
rasa train
```

8. Run:
```
ngrok http 5005
``` 
and put uri in credentials.yml

9. Run:
```
rasa run actions
```
in another terminal

10. Run: 
```
rasa run 
```
in another terminal

11. Open Telegram

12. Enjoy