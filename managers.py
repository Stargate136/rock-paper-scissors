import asyncio
import uuid
from datetime import datetime, timedelta

import numpy as np

from ML.preprocessing import pipeline
from ML.train import train_model


class TimeManager:
    """
    TimeManager class
    """

    @staticmethod
    def now():
        """Returns the current time"""
        return datetime.utcnow()

    @staticmethod
    def timestamp_after_delay(delay_seconds):
        """
        Returns the timestamp after a delay
        :param delay_seconds: number of seconds
        :return: timestamp"""
        current_time = datetime.utcnow()
        delayed_time = current_time + timedelta(seconds=delay_seconds)
        return delayed_time


class ClassifierManager:
    def __init__(self):
        self._model = train_model()

    @property
    def model(self):
        raise AttributeError("You can't access the model directly")

    @model.setter
    def model(self, value):
        raise AttributeError("You can't set the model directly")

    @model.deleter
    def model(self):
        raise AttributeError("You can't delete the model directly")

    @staticmethod
    def __preprocess(image):
        return pipeline(image)

    def predict(self, image):
        features = self.__preprocess(image)
        if not np.isnan(features).any():
            prediction = self._model.predict([features])[0]
            if prediction != "neutral":
                return prediction


class Game:
    """
    Game class
    Parameters
    ----------
    :param player1(str): name of the first player
    :param player2(str): name of the second player
    :param max_score(int): maximum score of the game (3 by default)
    """

    def __init__(self, player1, player2, max_score=3):
        self._player1 = player1
        self._player2 = player2
        self._score = {
            "player1": 0,
            "player2": 0
        }
        self._max_score = max_score

    def __str__(self):
        return f"{self.player1} vs {self.player2}"

    # ==== Attributes properties ====

    @property
    def player1(self):
        return self._player1

    @property
    def player2(self):
        return self._player2

    @property
    def score(self):
        return self._score

    @property
    def max_score(self):
        return self._max_score

    # ==== Others properties ====

    @property
    def winner(self):
        """
        Check the winner of the game
        :return: name of the winner of the game or None if the game is not over
        """
        if self.score["player1"] == self.max_score:
            return self.player1
        elif self.score["player2"] == self.max_score:
            return self.player2

    @property
    def status(self):
        """
        Check if the game is over
        :return: True if the game is over, False otherwise
        """
        return {
            "player1": self.player1,
            "player2": self.player2,
            "score": self.score,
            "max_score": self.max_score,
            "winner": self.winner,
        }
    # ==== Public methods ====

    def play_round(self, player1, player2):
        """
        Play a round of the game
        :param player1: Values can be 'rock', 'paper' or 'scissors'
        :param player2: Values can be 'rock', 'paper' or 'scissors'
        :return: name of the winner of the round
        """
        if player1 == "rock" and player2 == "scissors":
            winner = "player1"
        elif player1 == "scissors" and player2 == "rock":
            winner = "player2"
        elif player1 == "scissors" and player2 == "paper":
            winner = "player1"
        elif player1 == "paper" and player2 == "scissors":
            winner = "player2"
        elif player1 == "paper" and player2 == "rock":
            winner = "player1"
        elif player1 == "rock" and player2 == "paper":
            winner = "player2"
        else:
            return "Equality"

        self._score[winner] += 1
        return getattr(self, winner)


class GameManager:
    """
    GameManager class
    """
    def __init__(self):
        self._clf = ClassifierManager()
        self._waiting_players = []
        self._games = {}
        self._player_events = {}

    # ==== Private methods ====

    @staticmethod
    def __generate_game_id():
        """
        Generate a unique game id
        :return: (str) unique game id
        """
        return str(uuid.uuid4())

    def __get_game_id_by_player(self, player):
        """
        Get the game id of a player
        :param player:
        :return: (str) unique game id
        """
        game_id = next(
            (
                game_id for game_id, game in self._games.items()
                if player in (game.player1, game.player2)
            ), None
        )
        if game_id is None:
            raise ValueError("Player not found")
        return game_id

    def __get_game_status(self, game_id):
        """
        Get the status of a game
        :param game_id: unique game id
        :return: (dict) Information about the game
        """
        try:
            game = self._games[game_id]
        except KeyError:
            raise ValueError("Game not found")
        return {
            "id": game_id,
            **game.status
        }

    async def __match_players(self):
        """
        Match the players in the queue and start new games if there are enough players
        :return: None
        """
        while len(self._waiting_players) >= 2:
            player1 = self._waiting_players.pop(0)
            player2 = self._waiting_players.pop(0)
            game_id = self.start_game(player1, player2)
            print(f"Game {game_id} started between {player1} and {player2}")

            # Signale aux joueurs qu'ils ont rejoint une partie
            self._player_events[player1].set()
            self._player_events[player2].set()

    # ==== Public methods ====

    async def add_player_to_queue(self, player):
        """
        Add a player to the queue and wait for him to join a game
        :param player:
        :return: game_id
        """
        if player not in self._waiting_players:
            self._waiting_players.append(player)
            event = asyncio.Event()
            self._player_events[player] = event

            asyncio.ensure_future(self.__match_players())

            # Attend que le joueur rejoigne une partie
            await event.wait()

            # Récupère le game_id de la partie du joueur
            game_id = self.__get_game_id_by_player(player)
            return game_id

        raise ValueError("Player already in queue")

    async def start_game(self, player1, player2):
        """
        Start a new game
        :param player1:
        :param player2:
        :return: (str) unique game id
        """
        try:
            if player1 in self._waiting_players and player2 in self._waiting_players:
                game_id = self.__generate_game_id()
                game = Game(player1, player2)
                self._games[game_id] = game
                self._waiting_players.remove(player1)
                self._waiting_players.remove(player2)
                return game_id
        except KeyError:
            raise ValueError("Player not found")

    async def play_round(self, game_id, player1, player2):
        """
        Play a round of the game
        :param game_id: unique game id
        :param player1:
        :param player2:
        :return: (tuple) (winner, status) where winner is the player wins the round and status is the status of the game
        """
        try:
            pred_player1 = self._clf.predict(player1)
            pred_player2 = self._clf.predict(player2)
            if pred_player1 == "neutral" or pred_player2 == "neutral":
                return None, self.__get_game_status(game_id)
            round_winner = self._games[game_id].play_round(pred_player1, pred_player2)
            return round_winner, self.__get_game_status(game_id)
        except KeyError:
            raise ValueError("Game not found")
