# rock-paper-scissors
A project to play rock paper scissors using webcam

## TODO
- Detection de la main - OK
- Position des doigts - OK
- Ajouter un algorithme de classification - OK
- Bien documenter le code du package ML
- Capturer une classe neutre pertinente
- Optimiser les résultats de l'algorithme (GridSearch, tester plusieurs algos ...)
- Créer une classe ClassifierManager pour gérer le modèle de ML - OK
- Créer une classe GameManager pour gérer toute la logique du jeu - OK
- Mettre des logs dans tous les managers
- Créer une première version de l'API WebSockets avec fastapi pour le backend
- Créer game.html qui contient le code JS pour faire tourner le jeu en frontend
- Créer une application Django pour la gestion des utilisateurs (ajouter les méthodes __eq__ et __hash__ au model User pour pouvoir utiliser l'utilisateur comme clé du dictionnaire de GameManager._player_events)
- Créer une application Django pour l'affichage des pages
- Créer une application Django pour gérer le machine learning, enregistrer les performances, les nouvelles images et le feedback pour ré-entrainement futur
- Créer une application Django pour gérer le jeu, enregistrer les scores
- Créer une application Django Channels pour l'API websockets
- Créer une application Django pour le dashboard
- Déployer l'application


## Getting started
- Launch `init.sh`
- Launch `uvicorn api:app --reload`
- Go to http://127.0.0.1:8000/


## What init.sh does ?
- Create virtual environment
- Install requirements
- Apply migrations
- Create superuser
- Train the classification model


## Dataset
### Images
Rock Paper Scissors is a dataset containing 2,892 images of diverse hands in Rock/Paper/Scissors poses.
Credits : Laurence Moroney (lmoroney@gmail.com / laurencemoroney.com)
For more info http://www.laurencemoroney.com/rock-paper-scissors-dataset/

I captured a neutral class and added it to the dataset using the `capture_class.py` script and my webcam.

### CSV containing features only
Generated from the image dataset above using the `generate_dataset.py` script.

It contains 6 columns
- "1" : Distance between tip of thumb and wrist
- "2" : Distance between tip of index finger and wrist
- "3" : Distance between tip of middle finger and wrist
- "4" : Distance between tip of ring finger and wrist
- "5" : Distance between tip of little finger and wrist
- "target" : Class to be predicted

### Classes
- "rock"
- "paper"
- "scissors"
- "neutral"
