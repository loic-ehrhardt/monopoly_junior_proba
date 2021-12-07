
import numpy as np
import random

import logging
#logging.basicConfig(format='%(message)s', level=logging.DEBUG)

class Player:
    def __init__(self, number):
        self.number = number
        self.balance = 31 # 5*1 + 4*2 + 3*3 + 1*4 + 1*5
        self.position = 0

    def roll_dice(self):
        dice = random.randint(1, 6)
        self.position += dice
        logging.debug(f"{self!r} rolls {dice}")

    def add_balance(self, balance_change):
        self.balance += balance_change
        if self.balance <= 0:
            raise EndOfGameException()

    def __repr__(self):
        return f"<Player {self.number} (${self.balance})>"

class Card:
    def __init__(self, name, free_stand=None, jump_to=None):
        self.name = name
        self.free_stand = free_stand
        self.jump_to = jump_to

    def __repr__(self):
        return f"<Card {self.name}>"

class Deck:
    def __init__(self):
        self.reset()

    def reset(self):
        self.cards = [
            Card("FREE_STAND_PURPLE", free_stand="purple"),
            Card("FREE_STAND_LIGHT_BLUE", free_stand="light_blue"),
            Card("FREE_STAND_LIGHT_BLUE", free_stand="light_blue"),
            Card("FREE_STAND_MAGENTA", free_stand="magenta"),
            Card("FREE_STAND_ORANGE", free_stand="orange"),
            Card("FREE_STAND_ORANGE", free_stand="orange"),
            Card("FREE_STAND_RED", free_stand="red"),
            Card("FREE_STAND_YELLOW", free_stand="yellow"),
            Card("FREE_STAND_YELLOW", free_stand="yellow"),
            Card("FREE_STAND_GREEN", free_stand="green"),
            Card("FREE_STAND_DARK_BLUE", free_stand="dark_blue"),
            Card("FREE_STAND_DARK_BLUE", free_stand="dark_blue"),
            Card("JUMP_TO_START", jump_to=0),
            Card("JUMP_TO_FIREWORKS", jump_to=7),
            Card("JUMP_TO_PLAYGROUND", jump_to=8),
            Card("JUMP_TO_MAGENTA_1", jump_to=10),
            Card("JUMP_TO_GREEN_TRAIN", jump_to=12),
            Card("JUMP_TO_ORANGE_1", jump_to=13),
            Card("JUMP_TO_RED_1", jump_to=17),
            Card("JUMP_TO_BLUE_TRAIN", jump_to=20),
            Card("JUMP_TO_DOLPHIN_SHOW", jump_to=23),
            Card("JUMP_TO_GREEN_1", jump_to=26),
            Card("JUMP_TO_RED_TRAIN", jump_to=28),
            Card("JUMP_TO_DARK_BLUE_1", jump_to=29)]
        random.shuffle(self.cards)

    def pick(self):
        card = self.cards.pop()
        if len(self.cards) == 0:
            self.reset()
        return card

class Space:
    def __init__(self, name,
            penalty=None, stand=None, cost=None, pick_chance=False,
            replay=False, win_lottery=False, jump_to=None):
        self.name = name
        self.penalty = penalty
        self.stand = stand
        self.stand_group = None
        self.stand_owner = None
        self.cost = cost
        self.pick_chance = pick_chance
        self.replay = replay
        self.win_lottery = win_lottery
        self.jump_to = jump_to

    def __repr__(self):
        return f"<Space {self.name}>"

class StandGroup:
    def __init__(self, stand_1, stand_2):
        (color,) = set([stand_1.stand[0], stand_2.stand[0]])
        assert stand_1.stand[1] != stand_2.stand[1]
        self.color = color
        self.stand_1 = stand_1
        self.stand_2 = stand_2
        for stand in (stand_1, stand_2):
            stand.stand_group = self

class Board:
    NUM_SPACES = 32

    def __init__(self, num_players=4):
        self.spaces = {
             0: Space("START"),
             1: Space("PURPLE_1", stand=("purple", 1), cost=1),
             2: Space("PURPLE_2", stand=("purple", 2), cost=1),
             3: Space("CHANCE", pick_chance=True),
             4: Space("YELLOW_TRAIN", replay=True),
             5: Space("LIGHT_BLUE_1", stand=("light_blue", 1), cost=2),
             6: Space("LIGHT_BLUE_2", stand=("light_blue", 2), cost=2),
             7: Space("FIREWORKS", penalty=2),
             8: Space("PLAYGROUND"),
             9: Space("CHANCE", pick_chance=True),
            10: Space("MAGENTA_1", stand=("magenta", 1), cost=2),
            11: Space("MAGENTA_2", stand=("magenta", 2), cost=2),
            12: Space("GREEN_TRAIN", replay=True),
            13: Space("ORANGE_1", stand=("orange", 1), cost=3),
            14: Space("ORANGE_2", stand=("orange", 2), cost=3),
            15: Space("CHANCE", pick_chance=True),
            16: Space("LOTTERY", win_lottery=True),
            17: Space("RED_1", stand=("red", 1), cost=3),
            18: Space("RED_2", stand=("red", 2), cost=3),
            19: Space("CHANCE", pick_chance=True),
            20: Space("BLUE_TRAIN", replay=True),
            21: Space("YELLOW_1", stand=("yellow", 1), cost=4),
            22: Space("YELLOW_2", stand=("yellow", 2), cost=4),
            23: Space("DOLPHIN_SHOW", penalty=2),
            24: Space("TRAMWAY_TO_PLAYGROUND", penalty=3, jump_to=8),
            25: Space("CHANCE", pick_chance=True),
            26: Space("GREEN_1", stand=("green", 1), cost=4),
            27: Space("GREEN_2", stand=("green", 2), cost=4),
            28: Space("RED_TRAIN", replay=True),
            29: Space("DARK_BLUE_1", stand=("dark_blue", 1), cost=5),
            30: Space("DARK_BLUE_2", stand=("dark_blue", 2), cost=5),
            31: Space("CHANCE", pick_chance=True)}
        assert len(self.spaces) == self.NUM_SPACES
        self.stand_groups = {
            "purple":     StandGroup( self.spaces[1],  self.spaces[2]),
            "light_blue": StandGroup( self.spaces[5],  self.spaces[6]),
            "magenta":    StandGroup(self.spaces[10], self.spaces[11]),
            "orange":     StandGroup(self.spaces[13], self.spaces[14]),
            "red":        StandGroup(self.spaces[17], self.spaces[18]),
            "yellow":     StandGroup(self.spaces[21], self.spaces[22]),
            "green":      StandGroup(self.spaces[26], self.spaces[27]),
            "dark_blue":  StandGroup(self.spaces[29], self.spaces[30])}
        self.chances_deck = Deck()
        self.num_players = num_players
        self.players = [Player(i) for i in range(num_players)]
        self.current_player = 0
        self.current_lottery = 0
        self.current_turn = 1
        self.balances = []
        self.game_finished = False

    def __repr__(self):
        rv = f"[Turn {self.current_turn}, " \
             f"Next player: {self.current_player}, " \
             f"Lottery: {self.current_lottery}]\n"
        for i in range(self.NUM_SPACES):
            space = self.spaces[i]
            space_str = space.name
            if space.stand is not None:
                if space.stand_owner is not None:
                    space_str += f" [{space.stand_owner.number}]"
                else:
                    space_str += " [.]"
            else:
                space_str += "    "
            rv += f"{space_str: >30} |"
            for player in self.players:
                if player.position == i:
                    rv += f" {player!r}"
            rv += "\n"
        return rv

    def play_until_end(self):
        while not self.game_finished:
            self.step()

    def step(self):
        try:
            self._step()
        except EndOfGameException:
            self.endgame()
        finally:
            logging.debug(repr(self))
        if self.current_turn > 10000:
            # Looks like some games can run forever? Investigate.
            self.endgame()

    def _step(self):
        player = self.players[self.current_player]
        next_player = (self.current_player + 1) % len(self.players)

        player.roll_dice()
        if player.position >= Board.NUM_SPACES:
            player.add_balance(2)
            logging.debug(f"{player!r} starts new turn and gets $2")
            player.position -= Board.NUM_SPACES
            assert player.position < Board.NUM_SPACES
        logging.debug(f"{player!r} is now at "
                      f"{self.spaces[player.position].name}")

        space = self.spaces[player.position]

        if space.pick_chance:
            card = self.chances_deck.pick()
            logging.debug(f"{player!r} picks {card!r}")

            if card.free_stand is not None:
                free_group = self.stand_groups[card.free_stand]
                stand_1_owner = free_group.stand_1.stand_owner
                stand_2_owner = free_group.stand_2.stand_owner
                if stand_1_owner is None and stand_2_owner is None:
                    chosen_stand = random.choice([
                        free_group.stand_1, free_group.stand_2])
                elif stand_1_owner is None:
                    chosen_stand = free_group.stand_1
                elif stand_2_owner is None:
                    chosen_stand = free_group.stand_2
                elif stand_1_owner is stand_2_owner:
                    # Whole group owned by one player: cannot take any stand.
                    chosen_stand = None
                else:
                    candidate_stands = []
                    if stand_1_owner is not player:
                        candidate_stands.append(free_group.stand_1)
                    if stand_2_owner is not player:
                        candidate_stands.append(free_group.stand_2)
                    chosen_stand = random.choice(candidate_stands) \
                                   if len(candidate_stands) > 0 else None
                if chosen_stand is None:
                    logging.debug(f"{player!r} did not acquire any stand")
                else:
                    chosen_stand.stand_owner = player
                    logging.debug(f"{player!r} acquired {chosen_stand.name}")

            if card.jump_to is not None:
                # Copied code; TODO extract
                get_new_turn_reward = \
                    card.jump_to < player.position and card.jump_to != 8
                player.position = card.jump_to
                space = self.spaces[player.position]
                if get_new_turn_reward:
                    player.add_balance(2)
                logging.debug(f"{player!r} jumps to {space.name}"
                    f"{' and receives $2' if get_new_turn_reward else ''}")

        if space.penalty is not None:
            logging.debug(f"{player!r} pays penalty of ${space.penalty}")
            player.add_balance(-space.penalty)
            self.current_lottery += space.penalty
            logging.debug(f"Lottery is now {self.current_lottery}")

        if space.stand is not None:
            if space.stand_owner is None:
                # Acquire stand.
                player.add_balance(-space.cost)
                space.stand_owner = player
                logging.debug(f"{player!r} acquired "
                              f"{space.name} for ${space.cost}")
            elif space.stand_owner is player:
                # Own stand; do nothing.
                pass
            else:
                # Pay stop at other player's stand.
                other_player = space.stand_owner
                cost = space.cost
                group = space.stand_group
                if group.stand_1.stand_owner is other_player \
                        and group.stand_2.stand_owner is other_player:
                    # Other player has all the stands of the group.
                    cost *= 2
                logging.debug(f"{player!r} pays ${cost} to {other_player!r}")
                other_player.add_balance(cost)
                player.add_balance(-cost)

        if space.replay:
            logging.debug(f"{player!r} will play again")
            next_player = self.current_player

        if space.win_lottery:
            logging.debug(f"{player!r} won lottery (${self.current_lottery})")
            player.add_balance(self.current_lottery)
            self.current_lottery = 0

        if space.jump_to is not None:
            # Copied code; TODO extract
            get_new_turn_reward = \
                space.jump_to < player.position and space.penalty is not None
            player.position = space.jump_to
            space = self.spaces[player.position]
            if get_new_turn_reward:
                player.add_balance(2)
            logging.debug(f"{player!r} jumps to {space.name}"
                f"{' and receives $2' if get_new_turn_reward else ''}")

        self.current_player = next_player
        self.current_turn += 1
        self.balances.append([player.balance for player in self.players])

    def endgame(self):
        self.rankings = sorted(self.players, key=lambda player: player.balance)
        self.is_tie = self.rankings[-1].balance == self.rankings[-2].balance
        self.winner = self.rankings[-1]
        self.game_finished = True

class EndOfGameException(Exception):
    pass

class GameSamples:
    def __init__(self, num_players=3, num_games=10000):
        self.num_players = num_players
        self.num_games = num_games

        winners = []
        turns = []
        for i in range(1, num_games + 1):
            if i % 100 == 0:
                print(f"game {i} / {num_games}")
            b = Board(num_players=num_players)
            b.play_until_end()
            winners.append(b.winner.number)
            turns.append(b.current_turn)
        self.winners = np.array(winners)
        self.turns = np.array(turns)

    def plot_win_probability(self):
        import matplotlib.pyplot as plt
        win_prob = np.bincount(self.winners) / self.num_games
        # https://nobelis.eu/photis/Estimat/Paramlois/bernoulli_estim.html:
        stderr = np.sqrt(win_prob * (1 - win_prob) / self.num_games)
        #plt.figure()
        plt.bar(np.arange(self.num_players) + 1, 100 * win_prob,
            yerr=100 * stderr, ecolor="r")
        plt.xticks(np.arange(self.num_players) + 1)
        for (i, (w, s)) in enumerate(zip(win_prob, stderr)):
            plt.text(i + 1, 100 * w + 1, f"${100*w:.2f} \\pm {100*s:.2f}$",
                ha="center")
        plt.xlabel("Player start order")
        plt.ylabel("Win probability [%]")
        plt.grid(True)

    def plot_game_duration(self):
        import matplotlib.pyplot as plt
        plt.figure()
        bc = np.bincount(self.turns)
        plt.plot(np.arange(bc.size), bc)
        plt.xlabel("Game duration (turns)")
        plt.grid(True)

        plt.twinx()
        sorted_turns = np.sort(self.turns)
        plt.plot(sorted_turns, np.linspace(0, 1, self.num_games),
                 color="tab:orange")
