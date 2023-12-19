import asyncio
import uuid

from .classifier import ClassifierManager


class Game:
    """
    Game class
    Parameters
    ----------
    :param player1(str): name of the first player
    :param player2(str): name of the second player
    :param max_score(int): maximum score of the game (3 by default)
    """

    classifier = ClassifierManager()

    def __init__(self, player1, player2, max_score=3):

        self._player1 = player1
        self._player2 = player2
        self._max_score = max_score

        self._players_data = {
            player1: {
                "clicked": False,
                "image": None,
                "score": 0,
                "choice": None,
                "event": asyncio.Event(),
            },
            player2: {
                "clicked": False,
                "image": None,
                "score": 0,
                "choice": None,
                "event": asyncio.Event(),
            }
        }
        self._round_data = {
            "winner": None,

            "update": False,
            "update_lock": asyncio.Lock(),
        }

    def __str__(self):
        return f"{self.player1} vs {self.player2}"

    async def update(self):
        async with self.get_round_data("update_lock"):
            if self.get_round_data("update"):
                for player in self._players_data:
                    self.set_player_data(player, "clicked", False)
                    self.set_player_data(player, "image", None)
                    self.set_player_data(player, "event", asyncio.Event())
                    self.set_player_data(player, "choice", None)

                winner = self.get_round_data("winner")
                self.set_round_data("winner", None)
                self.add_point(winner)
                self.set_round_data("update", False)
            else:
                self.set_round_data("update", True)

    def set_player_data(self, player, key, value):
        self._players_data[player][key] = value

    def get_player_data(self, player, key):
        return self._players_data[player].get(key)

    def set_round_data(self, key, value):
        self._round_data[key] = value

    def get_round_data(self, key):
        return self._round_data.get(key)

    def add_point(self, player):
        self.set_player_data(player, "score", self.get_player_data(player, "score") + 1)


    # ==== Attributes properties ====

    @property
    def player1(self):
        return self._player1

    @property
    def player2(self):
        return self._player2

    @property
    def max_score(self):
        return self._max_score

    # ==== Others properties ====

    @property
    def game_winner(self):
        """
        Check the winner of the game
        :return: name of the winner of the game or None if the game is not over
        """
        if self.get_player_data(self.player1, "score") == self.max_score:
            return self.player1
        elif self.get_player_data(self.player2, "score") == self.max_score:
            return self.player2


    @property
    def status(self):
        """
        Check if the game is over
        :return: True if the game is over, False otherwise
        """
        return {
            "player1": {
                "score": self.get_player_data(self.player1, "score"),
                "name": self.player1
            },
            "player2": {
                "score": self.get_player_data(self.player2, "score"),
                "name": self.player2
            },
            "max_score": self.max_score,
            "winner": self.game_winner,
        }

    def get_other_player(self, player):
        if player == self.player1:
            return self.player2
        elif player == self.player2:
            return self.player1
        else:
            raise ValueError("Player not found (get_other_player)")

    async def play_round(self, player, image):
        other_player = self.get_other_player(player)
        prediction = self.classifier.predict(image)
        if prediction == "neutral" or prediction is None:
            return None, False
        else:
            self.set_player_data(player, "image", image)
            self.set_player_data(player, "choice", prediction)
            self.get_player_data(player, "event").set()
            round_played = await self.__determine_round_winner()
            if not round_played:
                await self.get_player_data(other_player, "event").wait()

            winner = self.get_round_data("winner")
            await self.update()
            return winner, True


    async def __determine_round_winner(self):
        """
        Wait the 2 players to play and return the winner of the round
        :return: the winner of the round
        """
        if self.get_round_data("winner") is not None:
            return True
        player_choices = (
            self.get_player_data(self.player1, "choice"),
            # self.get_player_data(self.player2, "choice")
            "scissors"  # TODO : supprimer
        )

        rules = {
            ("rock", "scissors"): self.player1,
            ("scissors", "rock"): self.player2,
            ("scissors", "paper"): self.player1,
            ("paper", "scissors"): self.player2,
            ("paper", "rock"): self.player1,
            ("rock", "paper"): self.player2
        }

        winner = rules.get(player_choices)

        if winner is not None:
            self.set_round_data("winner", winner)
            return True

        return False


class GameManager:
    """
    GameManager class
    """

    DELAY_TO_CAPTURE_IMAGE_IN_SEC = 2

    def __init__(self):
        self._waiting_players = []
        self._games = {}
        self._player_events = {}

    # ==== Private methods ====

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
            raise ValueError("Player not found (get_game_id_by_player)")
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
        if len(self._waiting_players) >= 2:
            player1 = self._waiting_players.pop(0)
            player2 = self._waiting_players.pop(0)
            await self.start_game(player1, player2)
            self._player_events[player1].set()
            self._player_events[player2].set()
            return True
        else:
            return False

    def get_game(self, player):
        game_id = self.__get_game_id_by_player(player)
        return self._games[game_id]

    def get_other_player(self, player):
        game = self.get_game(player)
        return game.get_other_player(player)

    async def add_player_to_queue(self, player):
        if player not in self._waiting_players:
            self._waiting_players.append(player)
            event = asyncio.Event()
            self._player_events[player] = event
            game_created = await self.__match_players()
            if not game_created:
                await event.wait()

            game_id = self.__get_game_id_by_player(player)
            return self.__get_game_status(game_id)

        raise ValueError("Player already in queue or not enough players")

    async def start_game(self, player1, player2):
        """
        Start a new game
        :param player1:
        :param player2:
        :return: (str) unique game id
        """
        try:
            game_id = str(uuid.uuid4())
            game = Game(player1, player2)
            self._games[game_id] = game
            return game_id
        except KeyError:
            raise ValueError("Player not found (start_game)")

    async def play_round(self, player, image):
        print(f"GameManager.play_round(player={player})")
        game_id = self.__get_game_id_by_player(player)
        game = self._games[game_id]
        round_winner, round_played = await game.play_round(player, image)
        print(f"GameManager.play_round(): round_winner: {round_winner}", f"round_played: {round_played}")
        game_status = self.__get_game_status(game_id)
        return round_winner, round_played, game_status
