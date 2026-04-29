import torch
import torch.nn as nn
import random
import alphabeta

class MancalaNet(nn.Module):
    def __init__(self):
        super(MancalaNet, self).__init__()
        self.fc1 = nn.Linear(18, 64)  # 14 pit counts + 4 extra features
        self.fc2 = nn.Linear(64, 1)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

class SARSAAgent3:
    def __init__(self, alpha=0.01, gamma=0.9, epsilon=0):
        self.model = MancalaNet()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=alpha)
        self.gamma = gamma
        self.epsilon = epsilon

    def getFeatures(self, state):
        features = list(state)

        # extra turn potential for P2
        my_EMP = 0
        for i in range(7, 13):
            if state[i] == (13 - i):
                my_EMP += 1
        
        # capture potential for P2
        my_CP = 0
        for i in range(7, 13):
            landed = i + state[i]
            if landed > 13:
                landed = landed % 14
            if landed in range(7, 13) and state[landed] == 0:
                opp = 12 - landed
                my_CP += state[opp]
        
        # extra turn potential for P1 (threat)
        opp_EMP = 0
        for i in range(0, 6):
            if state[i] == (6 - i):
                opp_EMP += 1
        
        # capture potential for P1 (threat)
        opp_CP = 0
        for i in range(0, 6):
            landed = i + state[i]
            if landed in range(0, 6) and state[landed] == 0:
                opp = 12 - landed
                opp_CP += state[opp]

        features.append(my_EMP)
        features.append(my_CP)
        features.append(opp_EMP)
        features.append(opp_CP)

        return torch.tensor(features, dtype=torch.float32)
    
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
