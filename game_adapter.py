"""
Thin translation layer between circ.py's CircularLinkedList board and a JSON API.

This module does not reimplement any Mancala rules or AI decision logic — it only
calls into circ.py / alphabeta.py / sarsa3.py (the existing, working game logic)
and serializes the results into plain dicts the frontend can render and animate.
"""

import contextlib
import io

import torch

import circ
import alphabeta
import sarsa3

AB_DEPTH = 10
HUMAN_PLAYER = 1
AI_PLAYER = 2

P1_PITS = range(0, 6)
P2_PITS = range(7, 13)
ALL_PITS = list(P1_PITS) + list(P2_PITS)

# SARSA3 (neural net) agent is loaded once at import time; inference is ~1ms/move.
_sarsa_agent = sarsa3.SARSAAgent3()
_sarsa_agent.model.load_state_dict(torch.load("model.pth", map_location="cpu"))
_sarsa_agent.model.eval()


class GameSession:
    def __init__(self, mode):
        self.mode = mode  # "pvp" | "ab" | "sarsa"
        self.board = circ.boardReset()
        self.currentPlayer = 1
        self.gameOver = False


def new_game(mode):
    if mode not in ("pvp", "ab", "sarsa"):
        raise ValueError(f"unknown mode: {mode}")
    return GameSession(mode)


def _legal_moves(board, player):
    state = board.circToList()
    return alphabeta.getLegalMoves(state, player)


def serialize(session):
    board = session.board
    pits = board.circToList()
    legal = [] if session.gameOver else _legal_moves(board, session.currentPlayer)

    return {
        "mode": session.mode,
        "pits": pits,
        "p1Store": pits[6],
        "p2Store": pits[13],
        "currentPlayer": session.currentPlayer,
        "humanPlayer": HUMAN_PLAYER,
        "aiPlayer": AI_PLAYER,
        "legalMoves": legal,
        "gameOver": session.gameOver,
        "winner": board.winner,  # None | 1 | 2 | 3 (3 = tie)
    }


def _execute_move(session, pit, player):
    """Runs one move through the authoritative board logic and packages an
    ordered list of animation steps describing exactly what happened."""
    board = session.board

    if player != session.currentPlayer or session.gameOver:
        raise ValueError("not this player's turn")
    if player == HUMAN_PLAYER and pit not in P1_PITS:
        raise ValueError("illegal pit for player 1")
    if player == AI_PLAYER and pit not in P2_PITS:
        raise ValueError("illegal pit for player 2")
    if board.getNode(pit).stones == 0:
        raise ValueError("pit is empty")

    lastNode = board.makeMove(pit, player, silentFlag=True)
    if lastNode is None:
        raise ValueError("illegal move")

    steps = [{"type": "sow", "pitIndex": idx} for idx in board.lastMoveTrace]

    board.handleCapture(lastNode, player)
    if board.lastCapture is not None:
        c = board.lastCapture
        steps.append({
            "type": "capture",
            "pitIndex": c["pitIndex"],
            "oppositeIndex": c["oppositeIndex"],
            "storeIndex": c["storeIndex"],
            "amount": c["pitStones"] + c["oppositeStones"],
        })

    playerStore = board.getPlayerStore(player)
    extraTurn = (lastNode is playerStore)

    # snapshot pit contents before checkGameOver's internal sweep() clears them,
    # so we can animate the end-of-game sweep into each store.
    preSweep = {i: board.getNode(i).stones for i in ALL_PITS}

    gameOver = board.checkGameOver(silentFlag=True)
    if gameOver:
        for i in ALL_PITS:
            amount = preSweep[i]
            if amount > 0:
                storeIndex = 6 if i in P1_PITS else 13
                steps.append({
                    "type": "sweep",
                    "pitIndex": i,
                    "storeIndex": storeIndex,
                    "amount": amount,
                })

    session.gameOver = gameOver
    if not gameOver:
        session.currentPlayer = player if extraTurn else (2 if player == 1 else 1)

    return {
        "steps": steps,
        "sourcePit": pit,
        "extraTurn": extraTurn and not gameOver,
        "state": serialize(session),
    }


def apply_human_move(session, pit):
    return _execute_move(session, pit, session.currentPlayer)


def compute_ai_move(session):
    """Returns the pit index the AI wants to play, without executing it."""
    board = session.board
    state = board.circToList()
    legal = alphabeta.getLegalMoves(state, AI_PLAYER)
    if not legal:
        return None

    if session.mode == "ab":
        with contextlib.redirect_stdout(io.StringIO()):
            return alphabeta.chooseBestMoveP2(state, AB_DEPTH)
    elif session.mode == "sarsa":
        return _sarsa_agent.chooseBestAction(tuple(state), legal, AI_PLAYER)
    else:
        raise ValueError(f"mode {session.mode} has no AI")


def apply_ai_move(session):
    pit = compute_ai_move(session)
    if pit is None:
        raise ValueError("AI has no legal moves")
    return _execute_move(session, pit, AI_PLAYER)
