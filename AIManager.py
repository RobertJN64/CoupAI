import MachineLearning.GeneticNets as gn
import CoupManager as coup

import copy
import random
import warnings

#region helper functions
def getMax(d):
    hscore = min(d.values()) - 1
    win = "ERROR"
    for key in d:
        if d[key] > hscore:
            win = key
            hscore = d[key]
    return win

def overlap(a, b):
    for i in a:
        if i in b:
            return True
    return False
#endregion

minmax = {'min': 0, 'max': 1}

def newActionNet():
    inputs = {'Duke': minmax, 'Contessa': minmax, 'Assassin': minmax, 'Ambassador': minmax, 'Captain': minmax, #Cards
              'Coins': {'min': 0, 'max': 12}, 'Lives': {'min': 1, 'max': 2}, #local info
              'MCards': {'min': 1, 'max': 2}, 'MCoins': {'min': 0, 'max': 12}} #Max on board
    outputs = {'Income': minmax, 'Aid': minmax, 'Coup': minmax,
               'Steal': minmax, 'Tax': minmax, 'Exchange': minmax, 'Assassinate': minmax} #possible actions
    return gn.Random(inputs, outputs, 1, #only need 1 net
                     2, 10, bias=True, neat=False,
                     activation_func="relu", final_activation_func="relu", log=False)[0][0]

def newResponseNet():
    inputs = {'Duke': minmax, 'Contessa': minmax, 'Assassin': minmax, 'Ambassador': minmax, 'Captain': minmax, #Cards
              'Income': minmax, 'Aid': minmax, 'Tax': minmax, 'Steal': minmax, 'Coup': minmax, 'Exchange': minmax,
              'Assassinate': minmax, 'Block': minmax, #list of actions
              'IDMatch': minmax, #attacked me?
              'Coins': {'min': 0, 'max': 12}, 'Lives': {'min': 1, 'max': 2}, #my info
              'ACards': {'min': 1, 'max': 2}, 'ACoins': {'min': 0, 'max': 12}} #attacker info

    outputs = {'block': minmax, 'challenge': minmax, 'blockChallenge': minmax}
    return gn.Random(inputs, outputs, 1, #only need 1 net
                     2, 10, bias=True, neat=False,
                     activation_func="relu", final_activation_func="relu", log=False)[0][0]

class tableState:
    def __init__(self, lastmove, moveCreator, moveTarget, players):
        self.lastmove = lastmove
        self.moveCreator = moveCreator
        self.moveTarget = moveTarget
        self.rawPlayers = players

    def getStrongestPlayer(self, exclude=None): #TODO - disable strongest targeting
        if exclude is None:
            exclude = []
        hscore = 0
        loc = -1
        for player in self.rawPlayers:
            score = len(player.cards) * 10 + player.coins
            if score > hscore and player.alive and player.id not in exclude:
                loc = player.id
                hscore = score
        if loc == -1:
            warnings.warn("No strong player found!")
        if len(self.rawPlayers[loc].cards) == 0:
            warnings.warn("ERROR! Alive player with no cards?")
        return loc

class Player:
    def __init__(self, mirror=None):
        if mirror is not None:
            self.actionNet = copy.deepcopy(mirror.actionNet)
            self.responseNet = copy.deepcopy(mirror.responseNet)
            self.cards = []
            self.rCards = []
            self.alive = True
            self.id = -1
            self.coins = 0
            self.tableState = tableState("nomove", -1, -1, [])
        else:
            self.actionNet = newActionNet()
            self.actionNet.evolve(5)
            self.responseNet = newResponseNet()
            self.responseNet.evolve(5)
            self.cards = []
            self.rCards = []
            self.alive = True
            self.id = -1
            self.coins = 0
            self.tableState = tableState("nomove", -1, -1, [])

    def setup(self, cards, ID):
        self.alive = True
        self.cards = cards
        self.rCards = []
        self.id = ID
        self.coins = 2

    def evolve(self, evoRate):
        """Evolves the nets of the current player. DESTRUCTIVE ACTION"""
        self.actionNet.evolve(evoRate)
        self.responseNet.evolve(evoRate)

    def evolvedCopy(self, evoRate):
        """Returns an new player similar to the current one"""
        nPlayer = Player(mirror=self)
        nPlayer.evolve(evoRate)
        return nPlayer

    def checkLife(self):
        if len(self.cards) == 0:
            self.alive = False
        return self.alive

    def moveInputs(self, players):
        self.tableState = tableState("nomove error", -1, -1, players)
        splayer = self.tableState.rawPlayers[self.tableState.getStrongestPlayer(exclude=[self.id])]
        ins = {'Duke': int("Duke" in self.cards),
               'Contessa': int("Contessa" in self.cards),
               'Assassin': int("Assassin" in self.cards),
               'Ambassador': int("Ambassador" in self.cards),
               'Captain': int("Captain" in self.cards),
               'Coins': self.coins, 'Lives': len(self.cards),
               'MCards': len(splayer.cards),
               'MCoins': splayer.coins}
        self.actionNet.reset()
        self.actionNet.receiveInput(ins)

    def getMove(self):
        if self.coins >= 10:
            return "Coup", self.tableState.getStrongestPlayer(exclude=[self.id]), False

        self.actionNet.process()
        outs = self.actionNet.getOutput()

        outs["Exchange"] = outs["Exchange"]

        validMove = False
        move = "nomove error"
        while not validMove:
            move = getMax(outs)
            validMove = True
            if move == "Coup" and self.coins < 7:
                validMove = False
            if move == "Assassinate" and self.coins < 3:
                validMove = False
            if move == "Steal" and self.tableState.rawPlayers[self.tableState.getStrongestPlayer(exclude=[self.id])].coins < 2:
                validMove = False
            outs[move] = -2


        target = -1
        if move in ["Assassinate", "Coup", "Steal"]:
            target = self.tableState.getStrongestPlayer(exclude=[self.id])

        lie = True
        vCharacters = coup.getMove(move).character
        if not vCharacters:
            lie = False
        else:
            for card in self.cards:
                if card in vCharacters:
                    lie = False

        return move, target, lie

    def observeBoard(self, move, moveCreator, moveTarget, players):
        self.tableState = tableState(move, moveCreator, moveTarget, players)

        ins = {'Duke': int("Duke" in self.cards),
               'Contessa': int("Contessa" in self.cards),
               'Assassin': int("Assassin" in self.cards),
               'Ambassador': int("Ambassador" in self.cards),
               'Captain': int("Captain" in self.cards),
               'Coins': self.coins,
               'Lives': len(self.cards),
               'Income': int(move=="Income"),
               'Aid': int(move=="Aid"),
               'Tax': int(move=="Tax"),
               'Steal': int(move=="Steal"),
               'Coup': int(move=="Steal"),
               'Exchange': int(move=="Exchange"),
               'Assassinate': int(move=="Assassinate"),
               'Block': int(move == "Block"),
               'IDMatch': int(self.id == moveTarget),
               'ACards': len(self.tableState.rawPlayers[self.tableState.moveCreator].cards),
               'ACoins': self.tableState.rawPlayers[self.tableState.moveCreator].coins}

        self.responseNet.reset()
        self.responseNet.receiveInput(ins)

    def blockChallenge(self):
        #check for easy block
        if (self.tableState.moveTarget == self.id and
            overlap(coup.getMove(self.tableState.lastmove).blocklist, self.cards)):
            return True, False #block

        self.responseNet.process()
        outs = self.responseNet.getOutput()
        block =  outs['block'] > 0.5 and outs['challenge'] < outs['block']
        challenge = outs['challenge'] > 0.5 and outs['block'] < outs['challenge']
        return block, challenge

    def counterChallenge(self):
        self.responseNet.process()
        outs = self.responseNet.getOutput()
        return outs["blockChallenge"] > 0

    def revealCards(self, validCards, deck):
            for card in validCards:
                if card in self.cards:
                    self.cards.remove(card)
                    deck.append(card)
                    self.cards.append(deck[random.randint(0, len(deck)-1)])
                    return True

            self.rCards.append(self.cards.pop(0))
            return False