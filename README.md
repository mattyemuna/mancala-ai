Just a quick reminder: I did Mancala, the original version, played with 48 stones, and a starting board of 4 stones per pit (excluding the two stores).

I started the assignment by designing the PvP version of the game. After much thought, I decided that I would make my board a circular linked list ( a linked list when the tail connects to the head). I did this because I thought it would be so much easier to handle sowing (making moves from pit 14 to pit 1+). I implemented the game logic including but not excluding: making moves, handling extra turns, handling captures, game over checks. Then I had a functioning  PvP game.

I then started to implement alpha-beta pruning. I had to reimplement the logic of the game and set up for alpha-beta pruning by adding some functions like getting a player’s legal moves and a heuristic function. For the heuristic, after much trial and tribulation, I ended up doing a weighted sum of  5 concrete evaluations:
Difference in win potential (state[myStore] / total_stones) (number of pits in a players store/ the number of total stones left in all the pits) 
Difference in Extra Move Potential (number of pits that can get extra turns)
Difference in Capture Potential (number of stones that can be captured)
Difference in Stones (number of stones each player has in their pits)
Number of Stones in the Player’s Last Two Pits
Then I was able to implement alpa-beta pruning, and was able to create two functions that chose the best move from player 1’s perspective and player 2’s as well. This allowed me to make the game PvAlphaBeta (AlphaBeta as player 2). I would win most, but I was making good moves. It’s important to note that AlphaBeta was very strong when it played as player 1 and won most games against me.

I next programmed a reinforcement learning agent using SARSA. My first attempt involved no linear approximation, just entering states into a Qtable. I trained it many times for many episodes. I trained it against itself and AlphaBeta at depths 3 and 4, however the agent was very weak and would make unintelligent moves. I programmed another SARSA agent using linear approximation where I had 14 weights (one for each bin and store). I trained it against itself for 10 million episodes, it was still weak. I trained it against AlphaBeta at depth 3 and 4, for 1000000 episodes and it was stronger, but still not a very strong opponent.

I then resorted to nonlinear weights via a Neural Net. A neural network can learn non-linear patterns — things like "pit 7 having stones is good, BUT only if pit 12 is also loaded." I then ran it against AlphaBeta with depth 3 for 1000000 episodes and then using those weights trained it  against AlphaBeta with depth 7 for around 5000 episodes. At the end of all the training the agent was an above average opponent — able to make intelligent moves often — however not beating me consistently, which is what I am aiming for. 

My last attempt was to change the approximation function for the agent to now include stuff like: my extra move potential, opposition’s extra move potential, my capture potential, opponent’s capture potential. I feed the new weights to my neural net to learn. I then trained it against AlphaBeta at depth 3 for 1000000 epochs, and it performed really well and it was the strongest I’ve had thus far. It would consistently put up a good fight and ultimately win the game.

