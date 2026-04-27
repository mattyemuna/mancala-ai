import random
import alphabeta

class SARSAAgent2:
    def __init__(self, alpha=0.001, gamma=0.9, epsilon=0):
        self.weights = [0.0] * 14
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
    
    def getFeatures(self, state):
        return list(state)
    
    def getQ(self, features):
        newFeatures = []
        for i in range(14):
            newFeatures.append(self.weights[i] * features[i])
        return sum(newFeatures)
    
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
            QVal = self.getQ(features)
            if QVal > bestVal:
                bestVal = QVal
                bestMove = move

        return bestMove
    
    def update(self, features, reward, next_features):
        q_current = self.getQ(features)
        q_next = self.getQ(next_features) if next_features is not None else 0
        error = reward + self.gamma * q_next - q_current
        for i in range(14):
            self.weights[i] += self.alpha * error * features[i]
        








            

