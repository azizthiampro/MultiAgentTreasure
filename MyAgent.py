
import Environment



class MyAgent:


    def __init__(self, id, initX, initY, env:Environment):
        self.id = id
        self.posX = initX
        self.posY = initY
        self.env = env
        self.mailBox = []

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return other.getId() == self.getId()
        return False


    #make the agent moves from (x1,y1) to (x2,y2)
    def move(self,  x1,y1, x2, y2) :
        if x1 == self.posX and y1 == self.posY :
            print("departure position OK")
            if self.env.move(self, x1, y1, x2, y2) :
                self.posX = x2
                self.posY = y2
                print("deplacement OK")
                return 1

        return -1

    #return the id of the agent
    def getId(self):
        return self.id

    #return the position of the agent
    def getPos(self):
        return (self.posX, self.posY)

    # add a message to the agent's mailbox
    def receive(self, idReceiver, textContent):
        self.mailBox.append((idReceiver, textContent))

    #the agent reads a message in her mailbox (FIFO mailbox)
    #return a tuple (id of the sender, message  text content)
    def readMail (self):
        idSender, textContent = self.mailBox.pop(0)
        print("mail received from {} with content {}".format(idSender,textContent))
        return (idSender, textContent)


    #send a message to the agent whose id is idReceiver
    # the content of the message is some text
    def send(self, idReceiver, textContent):
        self.env.send(self.id, idReceiver, textContent)

    # Broadcast the agent's position to all other agents
    def broadcastPosition(self):
        """Broadcast the agent's position to all other agents."""
        for agent_id in self.env.agentSet.keys():
            if agent_id != self.id:  # Don't send the position to itself
                self.send(agent_id, f"POS:{self.getPos()}")

 


    def __str__(self):
        res = self.id + " ("+ str(self.posX) + " , " + str(self.posY) + ")"
        return res

