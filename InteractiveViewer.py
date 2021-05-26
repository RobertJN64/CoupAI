import PythonExtended.Pygame as pyg
import MachineLearning.GeneticNets as gn
import pygame
from time import sleep

def viewAI(fname):
    pygame.init()
    screen = pyg.createScreen(800, 600, "AI Interactive Viewer: COUP AI")
    buttons = pyg.ButtonManager()

    net = gn.loadNets(fname)[0][0]

    coins = 5
    cards = 2
    mcoins = 5
    mcards = 2

    #region character buttons
    x = 50
    y = 400
    width = 100
    height = 50
    dukeButton = pyg.Button(x, y, width, height, (50,50,50), (200,200,0), "Duke", (0,0,0), 15, True)
    x += 125
    buttons.addButton(dukeButton)
    contessaButton = pyg.Button(x, y, width, height, (50, 50, 50), (200, 200, 0), "Contessa", (0, 0, 0), 15, True)
    x += 125
    buttons.addButton(contessaButton)
    assassinButton = pyg.Button(x, y, width, height, (50, 50, 50), (200, 200, 0), "Assassin", (0, 0, 0), 15, True)
    x += 125
    buttons.addButton(assassinButton)
    captainButton = pyg.Button(x, y, width, height, (50, 50, 50), (200, 200, 0), "Captain", (0, 0, 0), 15, True)
    x += 125
    buttons.addButton(captainButton)
    ambassadorButton = pyg.Button(x, y, width, height, (50, 50, 50), (200, 200, 0), "Contessa", (0, 0, 0), 15, True)
    x += 125
    buttons.addButton(ambassadorButton)
    #endregion

    oldState = {}
    done = False
    while not done:
        screen.fill((200,200,200))


        buttons.draw(screen)
        pygame.display.update()

        # region events
        events = pygame.event.get()
        buttons.resetEvents()
        for event in events:
            buttons.recieveEvent(event)
        # endregion

        newState = buttons.getEvents()
        if newState != oldState:
            net.reset()
            ins = {"Duke": int(dukeButton.state),
                   "Contessa": int(contessaButton.state),
                   "Ambassador": int(ambassadorButton.state),
                   "Captain": int(captainButton.state),
                   "Assassin": int(assassinButton.state),
                   "Coins": coins,
                   "MCoins": mcoins,
                   "Lives": cards,
                   "MCards": mcards}
            print(ins)
            net.receiveInput(ins)
            outs = net.getOutput()
            print(outs)
        oldState = newState

        # region exit loop
        if pyg.checkClose(events):
            pygame.quit()
            done = True
        # endregion
        sleep(0.01)


