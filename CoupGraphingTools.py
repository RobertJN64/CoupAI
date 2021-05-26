class turnInfo:
    def __init__(self, move, playerID, lie, block, challenge, moveExecuted):
        self.move = move
        self.playerID = playerID
        self.lie = lie
        self.block = block
        self.challenge = challenge
        self.moveExecuted = moveExecuted
        self.counterChallenge = block and challenge

class GraphManager:
    def __init__(self, availableActions, fig):
        self.fig = fig
        self.actionPlot = self.fig.add_subplot(2,2,1)
        self.WinActionPlot = self.fig.add_subplot(2,2,3)
        self.lbcPlot = self.fig.add_subplot(2,2,2)
        self.turnCountPlot = self.fig.add_subplot(2,2,4)

        self.lbcPoints = [[],[],[],[],[]]

        self.availableActions = availableActions
        self.actionPercs = []
        self.WinActPercs = []
        self.TurnCounts = []
        for a in range(0, len(self.availableActions)):
            self.actionPercs.append([])
            self.WinActPercs.append([])


    def updateGraphs(self, actionDB, winnerid, turnCounts):
        self.lbcPlot.clear()

        total = len(actionDB)
        lies = 0
        blocks = 0
        challenges = 0
        executedMoves = 0
        counterChallenge = 0

        for tInfo in actionDB:
            lies += int(tInfo.lie)
            blocks += int(tInfo.block)
            challenges += int(tInfo.challenge)
            executedMoves += int(tInfo.moveExecuted)
            counterChallenge += int(tInfo.counterChallenge)

        lies = lies * 100 / total
        blocks = blocks * 100 / total
        challenges = challenges * 100 / total
        executedMoves = executedMoves * 100 / total
        counterChallenge = counterChallenge * 100 / total

        self.lbcPoints[0].append(lies)
        self.lbcPoints[1].append(blocks)
        self.lbcPoints[2].append(challenges)
        self.lbcPoints[3].append(executedMoves)
        self.lbcPoints[4].append(counterChallenge)

        self.lbcPlot.plot(self.lbcPoints[0], c="red", label="lies")
        self.lbcPlot.plot(self.lbcPoints[1], c="orange", label="blocks")
        self.lbcPlot.plot(self.lbcPoints[2], c="yellow", label="challenges")
        self.lbcPlot.plot(self.lbcPoints[3], c="blue", label="completed moves")
        self.lbcPlot.plot(self.lbcPoints[4], c="black", label="challenged blocks")
        self.lbcPlot.set_xlabel("Generations")
        self.lbcPlot.set_ylabel("Action %")
        self.lbcPlot.set_title("LBC Plot")
        self.lbcPlot.set_ylim(0, 100)
        self.lbcPlot.legend(loc="upper left")

        self.actionPlot.clear()
        self.actionPlot.set_xlabel("Generation")
        self.actionPlot.set_ylabel("Action %")
        self.actionPlot.set_title("All Action %")

        actionCounts = []
        for a in range(0, len(self.availableActions)):
            actionCounts.append(0)

        for tInfo in actionDB:
            actionCounts[self.availableActions.index(tInfo.move)] += 1

        for i in range(0, len(self.availableActions)):
            self.actionPercs[i].append(actionCounts[i]*100/total)


        self.actionPlot.stackplot(range(0, len(self.actionPercs[0])), self.actionPercs, labels=self.availableActions)
        self.actionPlot.legend(loc='upper left')

        self.WinActionPlot.clear()
        self.WinActionPlot.set_xlabel("Generation")
        self.WinActionPlot.set_ylabel("Action %")
        self.WinActionPlot.set_title("Winner Action %")

        actionCounts = []
        for a in range(0, len(self.availableActions)):
            actionCounts.append(0)

        total = 0
        for tInfo in actionDB:
            total += int(tInfo.playerID == winnerid)
            if tInfo.playerID == winnerid:
                actionCounts[self.availableActions.index(tInfo.move)] += 1

        for i in range(0, len(self.availableActions)):
            self.WinActPercs[i].append(actionCounts[i] * 100 / total)

        self.WinActionPlot.stackplot(range(0, len(self.WinActPercs[0])), self.WinActPercs, labels=self.availableActions)
        self.WinActionPlot.legend(loc='upper left')

        self.fig.tight_layout()

        self.turnCountPlot.clear()
        self.turnCountPlot.set_xlabel("Generations")
        self.turnCountPlot.set_ylabel("Avg Turns")
        self.turnCountPlot.set_ylim(0,100)
        self.turnCountPlot.set_title("Turn Counts")

        self.TurnCounts.append(sum(turnCounts)/len(turnCounts))

        self.turnCountPlot.plot(range(0, len(self.TurnCounts)), self.TurnCounts)


