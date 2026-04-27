import torch
import torch.nn as nn
import random
import alphabeta

class MancalaNet(nn.Module):
    def __init__(self):
        super(MancalaNet, self).__init__()
        self.fc1 = nn.Linear(14, 64)  # input layer -> hidden layer
        self.fc2 = nn.Linear(64, 1)   # hidden layer -> output
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))   # activation function
        x = self.fc2(x)
        return x

class SARSAAgent3:
    def __init__(self, alpha = 0.01, gamma = 0.9, epsilon = 0):
        self.model = MancalaNet()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=alpha)
        self.gamma = gamma
        self.epsilon = epsilon

    def getFeatures(self, state):
        return torch.tensor(list(state), dtype=torch.float32)
    
    def getQ(self, features):
        return self.model(features)
    
    def chooseBestAction(self, state, legalMoves, player):
        rand = random.uniform(0, 1)

        if not legalMoves:
            return None
    
        if rand <= self.epsilon:
            return random.choice(legalMoves)
        
        bestVal = float("-inf")
        bestMove = None

        for move in legalMoves:
            next_state, next_player = alphabeta.applyMove(list(state), player, move) 
            features = self.getFeatures(next_state)
            QVal = self.getQ(features).detach().item()
            if QVal > bestVal:
                bestVal = QVal
                bestMove = move
        
        return bestMove
    
    def update(self, features, reward, next_features):
        q_current = self.getQ(features)
        if next_features is not None:
            q_next = self.getQ(next_features).detach()
        else:
            q_next = torch.tensor(0.0)
        target = torch.tensor(reward + self.gamma * q_next.item(), dtype=torch.float32)
        loss = (target - q_current) ** 2
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
