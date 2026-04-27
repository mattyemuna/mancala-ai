#cicrcular list implement    MATTHEW EMUNA
#linked list but the tail points to the head instead of null
import alphabeta
import sarsa
import sarsa2
import sarsa3
import torch
import pickle


class Node:
    def __init__(self, stones):
         self.stones = stones
         self.next = None

class CircularLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.store1 = None
        self.store2 = None
        self.p1Pits = []
        self.p2Pits = []
        self.winner = None
    
    def addNode(self, newNode):
        current = self.head
        if current == None:
            self.head = newNode
            self.tail = newNode
            newNode.next = self.head
        else:
            self.tail.next = newNode
            self.tail = newNode
            newNode.next = self.head
            
    def getNode(self, index):  
        counter = 0          
        current = self.head 
        while(counter < index):   
            current = current.next 
            counter += 1     
        return current
    
    def getNodeIndex(self, current):
        if current in self.p1Pits:
            for i in range(len(self.p1Pits)):
                if current == self.p1Pits[i]:
                    return i
        else:
            for i in range(len(self.p2Pits)):
                if current == self.p2Pits[i]:
                    return i
                
    def getPlayerStore(self, player):
        return self.store1 if player == 1 else self.store2

    def getOpponentStore(self, player):
        return self.store2 if player == 1 else self.store1

    def getPitList(self, player):
        return self.p1Pits if player == 1 else self.p2Pits
    
    def skip(self, current):
        return current.next.next 
    
    def printList(self):
        def cell(i, w=2):
            return f"[{self.getNode(i).stones:>{w}}]"

        def idx(i, w=2):
            return f" {i:>{w}} "

        indent = " " * 8

        # Top row indices (12 → 7)
        top_indices = "  ".join(idx(i) for i in range(12, 6, -1))
        top_row     = "  ".join(cell(i) for i in range(12, 6, -1))

        # Bottom row indices (0 → 5)
        bottom_row     = "  ".join(cell(i) for i in range(0, 6))
        bottom_indices = "  ".join(idx(i) for i in range(0, 6))

        left_store  = f"P2Store ({self.getNode(13).stones})"
        right_store = f"P1Store ({self.getNode(6).stones})"

        gap = " " * 36

        print()
        print(indent + top_indices)
        print(indent + top_row)
        print(left_store + gap + right_store)
        print(indent + bottom_row)
        print(indent + bottom_indices)
        print()
            
    def makeMove(self, pit_index, player, silentFlag = True):  

        current = self.getNode(pit_index)
        
        opponentStore = self.getOpponentStore(player)
        #check if pit is empty
        if current.stones == 0:
            print("empty pit ------------------- cant make move")  #works
            return
        
        else:
            numStones = current.stones
            current.stones = 0
            while numStones > 0:
               current = current.next
               if current == opponentStore:
                   current = current.next
               current.stones += 1
               numStones -= 1
            
            if not silentFlag:
                print("made move")
            return current #will need very soon for extra turn detection
        
    def handleCapture(self, lastNode, player):  
       
        playerStore = self.getPlayerStore(player)

        if lastNode.stones != 1 or lastNode == playerStore:
            return
        
        if player == 1 and lastNode not in self.p1Pits:
            return
        
        if player == 2 and lastNode not in self.p2Pits:
            return
        
        index = self.getNodeIndex(lastNode)
        oppositeIndex = 5 - index

        if player == 1:
            oppositeNode = self.p2Pits[oppositeIndex]
        else:
            oppositeNode = self.p1Pits[oppositeIndex]
        
        if oppositeNode.stones > 0:
            playerStore.stones += oppositeNode.stones + lastNode.stones
            oppositeNode.stones = 0
            lastNode.stones = 0
    
    def checkGameOver(self, silentFlag = True):
        #check if all the pits in p1Pits are empty
        over1 = 0
        for node in self.p1Pits:
            if node.stones == 0:
                over1 += 1

        #check if all the pits in p2Pits are empty
        over2 = 0
        for node in self.p2Pits:
            if node.stones == 0:
                over2 += 1
        
        if over1 == 6 or over2 == 6:
            self.sweep()
            self.winner = self.checkGameWinner()
            if not silentFlag:
                self.printList()
            return True
        else:
            return False
    
    def sweep(self):   
        for node in self.p1Pits:
            self.store1.stones += node.stones
            node.stones = 0
        
        for node in self.p2Pits:
            self.store2.stones += node.stones
            node.stones = 0
    
    def checkGameWinner(self):
        winner = None
        if self.store1.stones > self.store2.stones:
            winner = 1
        elif self.store1.stones < self.store2.stones:
            winner = 2
        else:
            winner = 3

        return winner
    
    def circToList(self):
        current = self.head
        lll = []
        lll.append(current.stones)
        current = current.next
        while current != self.head:
            lll.append(current.stones)
            current = current.next

        return lll
        
def gameControl(board):
    player = 1
    gameOver = False

    while not gameOver:
        board.printList() 
        pit = int(input(f"player {player} ------------------- choose pit index: "))
    
        if player == 1 and 0<=pit<=5: 
            lastNode = board.makeMove(pit, player)
        elif player == 2 and 7<=pit<=12:
            lastNode = board.makeMove(pit, player)
        else:
            print("-------cant make this move------")
            continue
        
        if lastNode is None:  #invalid move
            continue  

        board.handleCapture(lastNode, player)

        playerStore = board.getPlayerStore(player)

        if lastNode != playerStore:  #handle extra turn works
            if player == 1:
                player = 2
            else: 
                player = 1
        
        gameOver = board.checkGameOver()
        if gameOver:
            winner = board.checkGameWinner()
            print(f"-------------player{winner} wins-------------")

def gameControl2(board):
    player = 1
    gameOver = False
    depth = 10

    while not gameOver:
        board.printList() 

        if player == 1:
            pit = int(input(f"player {player} ------------------- choose pit index: "))
        else:
            state = board.circToList()
            pit = alphabeta.chooseBestMoveP2(state, depth)
            print(f"Alpha Beta Pruning chooses pit {pit}, at depth {10}")
        
        if player == 1 and 0<=pit<=5: 
            lastNode = board.makeMove(pit, player)
        elif player == 2 and 7<=pit<=12:
            lastNode = board.makeMove(pit, player)
        else:
            print("-------cant make this move------")
            continue
        
        if lastNode is None:  #invalid move
            continue  

        board.handleCapture(lastNode, player)

        playerStore = board.getPlayerStore(player)

        if lastNode != playerStore:  #handle extra turn works
            if player == 1:
                player = 2
            else: 
                player = 1
        
        gameOver = board.checkGameOver()   
        if gameOver:
            winner = board.checkGameWinner()
            print(f"-------------player{winner} wins-------------")

def train1(agent1, agent2, episodes):
    for i in range(episodes):
       
        if i % 10000 == 0:
            print(f"Episode {i} !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ")
            
        board = boardReset()
        player = 1
        gameOver = False


        state = tuple(board.circToList())
        legalMoves1 = alphabeta.getLegalMoves(state, 1)
        action1 = agent1.chooseBestAction(state, legalMoves1)
        legalMoves2 = alphabeta.getLegalMoves(state, 2)
        action2 = agent2.chooseBestAction(state, legalMoves2)

        while not gameOver:
            if player == 1:
                action = action1
            else:
                action = action2

            lastNode = board.makeMove(action, player)
            board.handleCapture(lastNode, player)
            playerStore = board.getPlayerStore(player)

            gameOver = board.checkGameOver()

            if lastNode != playerStore:
                if player == 1:
                    player = 2
                else:
                    player = 1

            if gameOver:
                if board.winner == 1:
                    reward1 = 1
                    reward2 = -1
                elif board.winner == 2:
                    reward1 = -1
                    reward2 = 1
                else:
                    reward1 = 0
                    reward2 = 0
            else:
                score = (board.store1.stones - board.store2.stones) / 48
                reward1 = score
                reward2 = -score

            if not gameOver:
                nextState = tuple(board.circToList())
                nextLegalMoves1 = alphabeta.getLegalMoves(nextState, 1)
                nextAction1 = agent1.chooseBestAction(nextState, nextLegalMoves1)
                nextLegalMoves2 = alphabeta.getLegalMoves(nextState, 2)
                nextAction2 = agent2.chooseBestAction(nextState, nextLegalMoves2)

                if player == 1:
                    agent1.update(state, action1, reward1, nextState, nextAction1)
                else:
                    agent2.update(state, action2, reward2, nextState, nextAction2)

                state = nextState
                action1 = nextAction1
                action2 = nextAction2
            else:
                if player == 1:
                    agent1.update(state, action1, reward1, None, None)
                else:
                    agent2.update(state, action2, reward2, None, None)

    with open("qtable_p1.pkl", "wb") as f:
        pickle.dump(agent1.Q, f)
    with open("qtable_p2.pkl", "wb") as f:
        pickle.dump(agent2.Q, f)

    print("Training complete! Q-tables saved.")

def train2(agent, episodes, depth):
    for i in range(episodes):
        board = boardReset()
        player = 1
        gameOver = False

        if i % 100000 == 0:
            print(f"EPISODE {i} !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        state = None
        action = None
        legalMoves = None

        while not gameOver:
            if player == 1:
                stateList = board.circToList()
                move = alphabeta.chooseBestMoveP1(stateList, depth)
            else:
                state = tuple(board.circToList())
                legalMoves = alphabeta.getLegalMoves(state, 2)
                action = agent.chooseBestAction(state, legalMoves)
                move = action

            lastNode = board.makeMove(move, player)
            board.handleCapture(lastNode, player)
            playerStore = board.getPlayerStore(player)
            gameOver = board.checkGameOver()

            if lastNode != playerStore:
                if player == 1:
                    player = 2
                else:
                    player = 1

            if player == 1 and state is not None:  # just finished player 2's move
                if gameOver:
                    if board.winner == 2:
                        reward = 1
                    elif board.winner == 3:
                        reward = 0
                    else:
                        reward = -1
                    agent.update(state, action, reward, None, None)
                else:
                    capture_threat = 0
                    for j in range(6):
                        if board.p2Pits[j].stones == 0:
                            opposite = board.p1Pits[5 - j].stones
                            capture_threat += opposite
                    reward = (board.store2.stones - board.store1.stones - capture_threat) / 48

                    nextState = tuple(board.circToList())
                    nextLegalMoves = alphabeta.getLegalMoves(nextState, 2)
                    nextAction = agent.chooseBestAction(nextState, nextLegalMoves)
                    agent.update(state, action, reward, nextState, nextAction)

    with open("qtable_p2.pkl", "wb") as f:
        pickle.dump(agent.Q, f)


    print("Training complete! Q-table saved.")

def train3(agent, episodes):
    for i in range(episodes):
        board = boardReset()
        player = 1
        gameOver = False

        if i % 1000000 == 0:
            print(f"EPISODE {i}")

        state = tuple(board.circToList())
        legalMoves = alphabeta.getLegalMoves(state, player)
        action = agent.chooseBestAction(state, legalMoves, player)
        if action is None:
            continue
        features = agent.getFeatures(alphabeta.applyMove(list(state), player, action)[0])

        while not gameOver:
            lastNode = board.makeMove(action, player)
            board.handleCapture(lastNode, player)
            playerStore = board.getPlayerStore(player)
            
            gameOver = board.checkGameOver()

            if lastNode != playerStore:  
                if player == 1:
                    player = 2
                else: 
                    player = 1

            if gameOver:
                if board.winner == player:
                    reward = 1
                elif board.winner == 3:
                    reward = 0
                else:
                    reward = -1
            else:
                capture_threat = 0
                for j in range(6):
                    if board.p2Pits[j].stones == 0:
                        opposite = board.p1Pits[5 - j].stones
                        capture_threat += opposite
                reward = (board.store2.stones - board.store1.stones - capture_threat) / 48

            if not gameOver:
                nextState = tuple(board.circToList())
                nextLegalMoves = alphabeta.getLegalMoves(nextState, player)
                nextAction = agent.chooseBestAction(nextState, nextLegalMoves, player)
                
                if nextAction is None:
                    break

                next_features = agent.getFeatures(alphabeta.applyMove(list(nextState), player, nextAction)[0])

                if player == 2:
                    agent.update(features, reward, next_features)

                state = nextState
                action = nextAction
                features = next_features
            else:
                if player == 2:
                    agent.update(features, reward, None)

    with open("weights.pkl", "wb") as f:
        pickle.dump(agent.weights, f)
    
    print("Training complete! Weights saved.")


def train4(agent, episodes):
    for i in range(episodes):
        board = boardReset()
        player = 1
        gameOver = False

        if i % 1000 == 0:
            print(f"EPISODE {i}")

        state = tuple(board.circToList())
        action = alphabeta.chooseBestMoveP1(list(state), 6)
        if action is None:
            continue
        features = agent.getFeatures(alphabeta.applyMove(list(state), player, action)[0])
        while not gameOver:
            lastNode = board.makeMove(action, player)
            board.handleCapture(lastNode, player)
            playerStore = board.getPlayerStore(player)
            
            gameOver = board.checkGameOver()

            if lastNode != playerStore:  
                if player == 1:
                    player = 2
                else: 
                    player = 1

            if gameOver:
                if board.winner == player:
                    reward = 1
                elif board.winner == 3:
                    reward = 0
                else:
                    reward = -1
            else:
                capture_threat = 0
                for j in range(6):
                    if board.p2Pits[j].stones == 0:
                        opposite = board.p1Pits[5 - j].stones
                        capture_threat += opposite
                reward = (board.store2.stones - board.store1.stones - capture_threat) / 48

            if not gameOver:
                nextState = tuple(board.circToList())
                nextLegalMoves = alphabeta.getLegalMoves(nextState, player)
                
                if player == 1:
                    nextAction = alphabeta.chooseBestMoveP1(list(nextState), 6)
                else:
                    nextAction = agent.chooseBestAction(nextState, nextLegalMoves, player)
                
                if nextAction is None:
                    break

                next_features = agent.getFeatures(alphabeta.applyMove(list(nextState), player, nextAction)[0])

                if player == 2:
                    agent.update(features, reward, next_features)

                state = nextState
                action = nextAction
                features = next_features
            else:
                if player == 2:
                    agent.update(features, reward, None)

    torch.save(agent.model.state_dict(), "model.pth")
    print("Training complete! Model saved.")


def gameControl3(board):
    player = 1
    gameOver = False
    agent = sarsa.SARSAAgent()
    with open("qtable_p2.pkl", "rb") as f:
        agent.Q = pickle.load(f)

    while not gameOver:
        board.printList() 

        if player == 1:
            pit = int(input(f"player {player} ------------------- choose pit index: "))
        else:
            state = board.circToList()
            legalMoves = alphabeta.getLegalMoves(state, player)
            state = tuple(board.circToList())
            pit = agent.chooseBestAction(state, legalMoves)
            print(f"SARSA chooses pit {pit}")
        
        if player == 1 and 0<=pit<=5: 
            lastNode = board.makeMove(pit, player)
        elif player == 2 and 7<=pit<=12:
            lastNode = board.makeMove(pit, player)
        else:
            print("-------cant make this move------")
            continue
        
        if lastNode is None:  #invalid move
            continue  

        board.handleCapture(lastNode, player)

        playerStore = board.getPlayerStore(player)

        if lastNode != playerStore:  #handle extra turn works
            if player == 1:
                player = 2
            else: 
                player = 1
        
        gameOver = board.checkGameOver()   
        if gameOver:
            winner = board.checkGameWinner()
            print(f"-------------player{winner} wins-------------")


def gameControl4(board):
    player = 1
    gameOver = False
    agent = sarsa2.SARSAAgent2()
    with open("weights.pkl", "rb") as f:
        agent.weights = pickle.load(f)
    
    print("weights:", agent.weights)

    while not gameOver:
        board.printList() 

        if player == 1:
            pit = int(input(f"player {player} ------------------- choose pit index: "))
        else:
            state = board.circToList()
            legalMoves = alphabeta.getLegalMoves(state, player)
            pit = agent.chooseBestAction(state, legalMoves, player)
            if pit is None:
                print("SARSA2 has no legal moves")
                break
            print(f"SARSA2 chooses pit {pit}")
        
        if player == 1 and 0<=pit<=5: 
            lastNode = board.makeMove(pit, player)
        elif player == 2 and 7<=pit<=12:
            lastNode = board.makeMove(pit, player)
        else:
            print("-------cant make this move------")
            continue
        
        if lastNode is None:
            continue  

        board.handleCapture(lastNode, player)

        playerStore = board.getPlayerStore(player)

        if lastNode != playerStore:
            if player == 1:
                player = 2
            else: 
                player = 1
        
        gameOver = board.checkGameOver()   
        if gameOver:
            winner = board.checkGameWinner()
            print(f"-------------player{winner} wins-------------")

def gameControl5(board):
    player = 1
    gameOver = False
    agent = sarsa3.SARSAAgent3()
    agent.model.load_state_dict(torch.load("model.pth"))
    agent.model.eval()

    while not gameOver:
        board.printList() 

        if player == 1:
            pit = int(input(f"player {player} ------------------- choose pit index: "))
        else:
            state = board.circToList()
            legalMoves = alphabeta.getLegalMoves(state, player)
            pit = agent.chooseBestAction(state, legalMoves, player)
            if pit is None:
                print("SARSA3 has no legal moves")
                break
            print(f"SARSA3 chooses pit {pit}")
        
        if player == 1 and 0<=pit<=5: 
            lastNode = board.makeMove(pit, player)
        elif player == 2 and 7<=pit<=12:
            lastNode = board.makeMove(pit, player)
        else:
            print("-------cant make this move------")
            continue
        
        if lastNode is None:
            continue  

        board.handleCapture(lastNode, player)

        playerStore = board.getPlayerStore(player)

        if lastNode != playerStore:
            if player == 1:
                player = 2
            else: 
                player = 1
        
        gameOver = board.checkGameOver()   
        if gameOver:
            winner = board.checkGameWinner()
            print(f"-------------player{winner} wins-------------")


def boardReset():

    board = CircularLinkedList()

    board.addNode(Node(4)) #pits 1-6
    board.p1Pits.append(board.tail)
    board.addNode(Node(4))
    board.p1Pits.append(board.tail)
    board.addNode(Node(4))
    board.p1Pits.append(board.tail)
    board.addNode(Node(4))
    board.p1Pits.append(board.tail)
    board.addNode(Node(4))
    board.p1Pits.append(board.tail)
    board.addNode(Node(4))
    board.p1Pits.append(board.tail)

    board.addNode(Node(0)) #store 1

    board.addNode(Node(4)) #pits 8-13
    board.p2Pits.append(board.tail)
    board.addNode(Node(4))
    board.p2Pits.append(board.tail)
    board.addNode(Node(4))
    board.p2Pits.append(board.tail)
    board.addNode(Node(4))
    board.p2Pits.append(board.tail)
    board.addNode(Node(4))
    board.p2Pits.append(board.tail)
    board.addNode(Node(4))
    board.p2Pits.append(board.tail)

    board.addNode(Node(0)) #store 2

    board.store1 = board.getNode(6)
    board.store2 = board.getNode(13)

    return board

# board = boardReset()
# gameControl2(board)

# agent = sarsa.SARSAAgent()
# train2(agent, episodes=250000, depth=3)

# agent1 = sarsa.SARSAAgent()
# agent2 = sarsa.SARSAAgent()
# train3(agent1, agent2, episodes=1000000)

# agent = sarsa2.SARSAAgent2()
# train3(agent, 10000000)

agent = sarsa3.SARSAAgent3()
agent.model.load_state_dict(torch.load("model.pth"))
train4(agent, 5000)

board = boardReset()
gameControl5(board)

