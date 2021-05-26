import MachineLearning.GeneticNets as gn
import MachineLearning.GeneticEvolution as ge
import AIManager
import CoupManager
import CoupGraphingTools as graph
import PythonExtended.Logging as l

import matplotlib.pyplot as plt
import random
import sys

currentLogLevel = l.LogLevel.NONE
logger = l.Logger(currentLogLevel)

#region helper functions
def nextTurn(cTurn, playerInfo):
    done = False
    attempts = 0
    turn = cTurn
    while not done and attempts < 50:
        attempts += 1
        turn += 1
        if turn >= len(playerInfo):
            turn = 0
        done = turn < len(playerInfo) and playerInfo[turn].alive
    if attempts >= 50:
        raise Exception("Couldn't find valid turn")
    return turn

def getPlayers(count):
    pList = []
    for i in range(0, count):
        pList.append(AIManager.Player())
    return pList
#endregion
#Game Order
#1. Reset + deal
#--LOOP--
#2. Observe board
#3. Make move
#4. Observe board
#5. Block + challenge
#6. Counter block?
#7. Handle blocks / challenges
#8. Execute move
#9. Check win

def game(players, rawcounter):
    #region Reset + deal
    actions = []
    deck = CoupManager.newDeck()
    currentTurn = -1
    for i in range(0, len(players)):
        cards = [deck.pop(random.randint(0, len(deck)-1)), deck.pop(random.randint(0, len(deck)-1))]
        players[i].setup(cards, i)

    winner = -1
    rounds = 0
    gameOver = False
    #endregion

    logger.print("Game starting", l.LogLevel.Pretty)
    while not gameOver and rounds < 100:
        rounds += 1
        currentTurn = nextTurn(currentTurn, players)
        #region observe board
        players[currentTurn].moveInputs(players)
        #endregion
        #region make move
        move, moveTarget, lie = players[currentTurn].getMove()
        moveCreator = currentTurn
        #endregion
        # region observe board
        for player in players:
            player.observeBoard(move, moveCreator, moveTarget, players)
        # endregion
        #region block + challenge
        block = -1 #no player
        challenge = -1
        for player in players:
            if player.id != currentTurn and player.alive:
                pBlock, pChallenge = player.blockChallenge()
                if pBlock and CoupManager.getMove(move).blockable:
                    block = player.id
                    break
                if pChallenge and CoupManager.getMove(move).challengeable:
                    challenge = player.id
                    break
        #endregion
        #region counter challenge
        if block != -1:
            #region observe board
            players[currentTurn].observeBoard(move, moveCreator, moveTarget, players)
            #endregion
            if players[currentTurn].counterChallenge():
                challenge = players[currentTurn].id
        #endregion
        #region resolve blocks + challenges
        allowMove = True
        if block != -1 and challenge != -1:
            #A player challenged a block
            validCards = CoupManager.getMove(move).blocklist
            if players[block].revealCards(validCards, deck):
                allowMove = False
                players[challenge].revealCards([], deck)

        elif block != -1:
            allowMove = False

        elif challenge != -1:
            validCards = []
            if players[moveCreator].revealCards(validCards, deck):
                players[challenge].revealCards([], deck)
            else:
                allowMove = False
        #endregion
        #region execute move
        if allowMove:
            if move == 'Assassinate' and players[moveTarget].checkLife() == False: #double discard thingy
                pass
            else:
                CoupManager.ExecuteMove(move, moveCreator, moveTarget, players, deck)
        #endregion
        #region checkwin
        alive = 0
        winner = None
        for player in players:
            if player.checkLife():
                alive += 1
                winner = player.id
        if alive == 1:
            gameOver = True
        #endregion
        #region debug print
        actions.append(graph.turnInfo(move, moveCreator + rawcounter, lie, block != -1, challenge != -1, allowMove))

        logger.print("Round: " + str(rounds), l.LogLevel.All)
        logger.print("Turn: " + str(currentTurn), l.LogLevel.All)
        logger.print("Move chosen: " + str(move), l.LogLevel.All)
        logger.print("Move target: " + str(moveTarget), l.LogLevel.All)
        logger.print("Move block attempt: " + str(block), l.LogLevel.All)
        logger.print("Challenge attempts: " + str(challenge), l.LogLevel.All)
        logger.print("Move executed: " + str(allowMove), l.LogLevel.All)
        logger.print("\n", l.LogLevel.All)

        logger.print("Round " + str(rounds) + ", Turn " + str(currentTurn), l.LogLevel.Pretty)
        movestr = "Move: " + str(move)
        if moveTarget != -1:
            movestr += " | Target: " + str(moveTarget)
        pstring = ""
        for player in players:
            pstring += str(player.alive) + " "

        logger.print(movestr, l.LogLevel.Pretty)
        logger.print(pstring, l.LogLevel.Pretty)
        logger.print(str(block) + ", " + str(challenge), l.LogLevel.Pretty)
        logger.print("\n", l.LogLevel.Pretty)
        #endregion

    #region end states
    if gameOver:
        return winner, actions, rounds
    else:
        logger.print("Game terminated. Rounds exceeded 100", l.LogLevel.Pretty)
        return None, actions, rounds
    #endregion

def gameSeries(players, count, fig, rawcounter):
    actions = []
    turnCounts = []
    scores = [0] * (len(players) + 1)
    for i in range(0, count):
        fig.canvas.flush_events()
        winner, acts, turns = game(players, rawcounter)
        turnCounts.append(turns)
        actions = actions + acts
        if winner is None:
            scores[len(players)] += 1
        else:
            scores[winner] += 1
    sys.stdout.write("\r")
    return scores, actions, turnCounts

def tournament(players, gcount, fig, gen): #TODO - better tournament style
    actionDB = []
    turnDB = []
    scores = [0] * len(players)
    for i in range(0, len(players), 4):
        sys.stdout.write("\r" + "Generation: " + str(gen) + " - " + str(i*100/len(players)) + "%")

        tPlayers = players[i:i+4]
        tScores, actions, turnCounts = gameSeries(tPlayers, gcount, fig, i)
        actionDB += actions
        turnDB += turnCounts
        scores[i:i+4] = tScores[0:4]

    pscores = list(zip(players, scores))
    topPlayers = sorted(pscores, key= lambda x: x[1], reverse=True)[0:4]
    bestPlayers, tScores = zip(*topPlayers)

    tScores, actions, turnCounts = gameSeries(bestPlayers, gcount, fig, len(players))
    actionDB = actionDB + actions
    turnDB += turnCounts

    for i in range(0, len(bestPlayers)):
        player = bestPlayers[i]
        index = players.index(player)
        scores[index] += tScores[i]

    return scores, actionDB, turnDB

def run():
    nPlayers = 20
    evoTable = ge.getEvo(nPlayers)
    gens = 50
    gpt = 10 #games per tournament
    saveInterval = 5

    plt.ion()
    plt.show()
    fig = plt.figure()

    players = getPlayers(nPlayers)
    GM = graph.GraphManager(list(players[0].actionNet.outputs.keys()), fig)

    player = players[0]
    for i in range(0, gens):
        scores, ActionDB, turnCounts = tournament(players, gpt, fig, i)
        GM.updateGraphs(ActionDB, scores.index(max(scores)), turnCounts)

        newPlayers = []
        player = players[scores.index(max(scores))]
        if i%saveInterval == 0:
            gn.saveNets([player.actionNet], "CoupAIs/round" + str(i) + "nets", "coupbot", 1.0, log=False)
        for j in range(0, len(evoTable)):
            player = players[scores.index(max(scores))]
            scores[scores.index(max(scores))] = -1
            newPlayers.append(player)
            for x in range(0, evoTable[j]-1):
                newPlayers.append(player.evolvedCopy(3))

        players = newPlayers


    gn.saveNets([player.actionNet], "CoupAIs/FINAL", "coupbot", 1.0, log=False)
    logger.printTimestamp("Training finished after ")
    logger.save("logfile.txt")

    plt.ioff()
    plt.show()