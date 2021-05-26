import random

class Move:
    def __init__(self, name, character, blocklist):
        self.name = name
        self.challengeable = len(character) > 0
        self.character = character
        self.blockable = len(blocklist) > 0
        self.blocklist = blocklist

moves = [Move("Income", [], []),
         Move("Aid", [], ["Duke"]),
         Move("Tax", ["Duke"], []),
         Move("Steal", ["Captain"], ["Captain", "Ambassador"]),
         Move("Exchange", ["Ambassador"], []),
         Move("Assassinate", ["Assassin"], ["Contessa"]),
         Move("Coup", [], [])]

def getMove(name):
    for move in moves:
        if move.name == name:
            return move
    print("ERROR Move " + name + " not found. (Error in getmove)")
    return None

def newDeck():
    #Each card appears 3x times
    cards = ["Duke", "Captain", "Assassin", "Contessa", "Ambassador"]
    return cards * 3

def ExecuteMove(move, creator, target, players, deck):
    if move == "Income":
        players[creator].coins += 1

    elif move == "Aid":
        players[creator].coins += 2

    elif move == "Tax":
        players[creator].coins += 3

    elif move == "Steal":
        players[creator].coins += 2
        players[target].coins -= 2

    elif move == "Exchange":
        count = len(players[creator].cards)
        deck += players[creator].cards
        players[creator].cards = []
        for i in range(0, count):
            players[creator].cards.append(deck[random.randint(0, len(deck) - 1)])

    elif move == "Assassinate":
        players[creator].coins -= 3
        players[target].revealCards([], deck)

    elif move == "Coup":
        players[creator].coins -= 7
        players[target].revealCards([], deck)

    else:
        print("ERROR: Move " + move + " not found. (Error in execute move).")
