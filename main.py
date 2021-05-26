mode = input("Mode: ")

if mode.lower() in ['t', 'train', 'trainer']:
    import Trainer
    Trainer.run()

elif mode.lower() in ['a', 'ai', 'test']:
    import AITester
    fname = "CoupAIs/round" + str(input("Fname: ")) + "nets"
    AITester.testAI(fname)

elif mode.lower() in ['v', 'i', 'view', 'interactive']:
    import InteractiveViewer
    fname = "CoupAIs/round" + str(input("Fname: ")) + "nets"
    InteractiveViewer.viewAI(fname)

else:
    print("Mode error.")