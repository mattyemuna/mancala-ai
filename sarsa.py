#sarsa          MATTHEW EMUNA
import random

class SARSAAgent:
    def __init__(self, alpha=0.001, gamma=0.9, epsilon=0):
        self.Q = {}
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
    
    def chooseBestAction(self, state, legalMoves):
        rand = random.uniform(0, 1)

        if not legalMoves:
            return None
        elif rand <= self.epsilon:
            return random.choice(legalMoves)
        else:
            bestMoves = []
            bestVal = float("-inf")

            for move in legalMoves:
                val = self.Q.get((state, move), 0)
                if val > bestVal:
                    bestVal = val
                    bestMoves = [move]
                elif val == bestVal:
                    bestMoves.append(move)
            
            return random.choice(bestMoves)
        
    def update(self, s, a, r, s_next, a_next):
        if s_next is None:
            target = r
        else:
            target = r + self.gamma * self.Q.get((s_next, a_next), 0)
            
        self.Q[(s, a)] = self.Q.get((s, a), 0) + self.alpha * (target - self.Q.get((s, a), 0))
    
    