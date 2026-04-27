# alpha beta pruning      MATTHEW EMUNA

def getLegalMoves(state, player):

    if player == 1:
        state = state[:6]
        add = 0
    else:
        state = state[7:13]
        add = 7
    
    lm = []
    for pit in range(len(state)): 
        if state[pit] > 0:
            lm.append(pit + add)

    return lm

def applyMove(state, player, pit):

    newState = state[:]
    numStones = newState[pit]
    newState[pit] = 0
    currentPit = pit + 1

    if player == 1:
        oppStore = 13
        myStore = 6
        myPits = range(0, 6)

    else:
        oppStore = 6
        myStore = 13
        myPits = range(7, 13)
       
    lastPit = None

    while(numStones > 0):
        if currentPit > 13:
            currentPit = 0

        if currentPit == oppStore:
            currentPit +=1
            continue
        else:
            newState[currentPit] += 1 
            numStones -= 1
            lastPit = currentPit
        
        currentPit +=1
    
    #checkCapture
    if (lastPit in myPits) and (newState[lastPit] == 1):
        opp = 12 - lastPit
        if newState[opp] > 0:
            newState[myStore] += newState[opp] + newState[lastPit]
            newState[opp] = 0
            newState[lastPit] = 0
    
    #check gameover
    gameOver = False
    count1 = 0
    for i in range(0,6):
        if newState[i] == 0:
            count1 +=1
    
    count2 = 0
    for i in range(7, 13):
        if newState[i] == 0:
            count2 += 1
    
    if count1 == 6 or count2 == 6:
        gameOver = True
    
    #sweep 
    if gameOver:
        for i in range(0,6):
            newState[6] += newState[i]
            newState[i] = 0
        for i in range(7,13):
            newState[13] += newState[i]
            newState[i] = 0

    #lands in pit
    if lastPit == myStore:
        return (newState, player)
    else:
        if player == 1:
            return (newState, 2)
        else:
            return (newState, 1)

def evaluateState(state, player):

    if player == 1:
        myStore = 6
        oppStore = 13
        myRange = range(0, 6)
        oppRange = range(7, 13)
        getOpp = lambda i: 12 - i
        extraDist = lambda i: 6 - i
        oppExtraDist = lambda i: 13 - i
        
    else:
        myStore = 13
        oppStore = 6
        myRange = range(7, 13)
        oppRange = range(0, 6)
        getOpp = lambda i: 12 - i
        extraDist = lambda i: 13 - i
        oppExtraDist = lambda i: 6 - i

    total_stones = 0    #for total number of stones
    my_EMP = 0   # extra move potential
    opp_EMP = 0
    my_CP = 0    # capture potential
    opp_CP = 0
    my_SLTP = 0 # stones in last two pits   
    my_stones = 0   
    opp_stones = 0

    for i in myRange:
        stones = state[i]
        my_stones += stones
        total_stones += stones 

        if stones == extraDist(i):
            my_EMP += 1 
        

        currentPit = i
        num = stones

        while num > 0:
            currentPit += 1
            if currentPit > 13:
                currentPit = 0
            if currentPit == oppStore:
                continue
            num -= 1

        landed = currentPit

        if landed in myRange and state[landed] == 0:
            my_CP += state[getOpp(landed)]
        
        if (max(myRange) - i) <= 2:
            my_SLTP += stones
        
    for i in oppRange:
        stones = state[i]
        opp_stones += stones
        total_stones += stones 

        if stones == oppExtraDist(i):
            opp_EMP += 1

        currentPit = i
        num = stones

        while num > 0:
            currentPit += 1
            if currentPit > 13:
                currentPit = 0
            if currentPit == myStore:
                continue
            num -= 1

        landed = currentPit

        if landed in oppRange and state[landed] == 0:
            opp_CP += state[getOpp(landed)]


    my_WP = state[myStore] / total_stones 
    opp_WP = state[oppStore] / total_stones

    if my_SLTP >= 12:
        my_SLTP = 1
    else:
        my_SLTP = -1

    diff_WP = my_WP - opp_WP
    diff_EMP = my_EMP - opp_EMP
    diif_CP = my_CP - opp_CP
    diff_stones = my_stones - opp_stones


    W1 = 0.3
    W2 = 0.5
    W3 = 0.6
    W4 = 0.2
    W5 = -0.05

    score = (diff_WP * W1) + (diff_EMP * W2) + (diif_CP * W3) + (diff_stones * W4) + (my_SLTP * W5)

    return score



def alphabeta(state, depth, alpha, beta, player):

    #base case


     # game is over, just return store difference
    if sum(state[0:6]) == 0 or sum(state[7:13]) == 0:
        return state[6] - state[13]

    if depth == 0:
       return evaluateState(state, 1)
    
    moves = getLegalMoves(state, player)

    if not moves:
        return evaluateState(state, 1)
    
    #MAX NODE
    if player == 1:

        value = -10000

        for move in moves:
            childState, nextPlayer = applyMove(state, player, move)
            childVal = alphabeta(childState, depth-1, alpha, beta, nextPlayer)
            
            value = max(value, childVal)

            alpha = max(alpha, value)

            if alpha >= beta:
                break
        
        return value
    
    if player == 2:

        value = 10000

        for move in moves:
            childState, nextPlayer = applyMove(state, player, move)
            childVal = alphabeta(childState, depth-1, alpha, beta, nextPlayer)

            value = min(value, childVal)

            beta = min(beta, value) 

            if beta <= alpha:
                break
        
        return value
    
def chooseBestMoveP2(state, depth):

    lm = getLegalMoves(state, 2)
    alpha = float("-inf")
    beta = float("inf")
    bestMove = None
    bestScore = float("inf")

    for move in lm:
        child_state, next_player = applyMove(state, 2, move)
        child_value = alphabeta(child_state, depth-1, alpha, beta, next_player)

        print("move", move, "-> score", child_value)

        if child_value < bestScore:
            bestScore = child_value
            bestMove = move
        
        beta = min(beta, bestScore)  

    print("BEST MOVE:", bestMove, "score:", bestScore)
    return bestMove

def chooseBestMoveP1(state, depth):

    state = list(state)
    lm = getLegalMoves(state, 1)
    alpha = float("-inf")
    beta = float("inf")
    bestMove = None
    bestScore = float("-inf")

    for move in lm:
        child_state, next_player = applyMove(state, 1, move)
        child_value = alphabeta(child_state, depth-1, alpha, beta, next_player)

        if child_value > bestScore:
            bestScore = child_value
            bestMove = move
        
        alpha = max(alpha, bestScore)

    return bestMove





        

        








        





    

        













