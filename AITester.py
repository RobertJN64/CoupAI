import MachineLearning.GeneticNets as gn

def testAI(fname):
    net = gn.loadNets(fname)[0][0]

    while True:
        net.reset()
        ins = {}
        for i in net.expectedInputs:
            ins[i] = float(input("Input " + str(i) + ": "))

        net.receiveInput(ins)
        net.process()
        outs = net.getOutput()

        for out in outs:
            print(out + ": " + str(outs[out]))