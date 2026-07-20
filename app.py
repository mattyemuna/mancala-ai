"""
Flask server for the Mancala web UI.

Purely a transport layer: all game rules and AI decisions live in circ.py /
alphabeta.py / sarsa3.py via game_adapter.py. This file just exposes them over
HTTP and serves the static frontend.
"""

import os
import uuid

from flask import Flask, jsonify, request, session, send_from_directory

import game_adapter as ga

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.secret_key = os.environ.get("MANCALA_SECRET_KEY", os.urandom(24))

# gid -> GameSession. Fine for a single local dev server (one process, no
# horizontal scaling); a real multi-user deployment would need a shared store.
games = {}


def _get_session():
    gid = session.get("gid")
    if gid is None or gid not in games:
        return None
    return games[gid]


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/new_game", methods=["POST"])
def new_game():
    body = request.get_json(silent=True) or {}
    mode = body.get("mode")
    try:
        g = ga.new_game(mode)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    gid = str(uuid.uuid4())
    games[gid] = g
    session["gid"] = gid
    return jsonify(ga.serialize(g))


@app.route("/api/state", methods=["GET"])
def get_state():
    g = _get_session()
    if g is None:
        return jsonify({"error": "no active game"}), 404
    return jsonify(ga.serialize(g))


@app.route("/api/move", methods=["POST"])
def move():
    g = _get_session()
    if g is None:
        return jsonify({"error": "no active game"}), 404

    body = request.get_json(silent=True) or {}
    pit = body.get("pit")
    if not isinstance(pit, int):
        return jsonify({"error": "pit must be an integer"}), 400

    if g.mode != "pvp" and g.currentPlayer != ga.HUMAN_PLAYER:
        return jsonify({"error": "not the human player's turn"}), 400

    try:
        result = ga.apply_human_move(g, pit)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(result)


@app.route("/api/ai_move", methods=["POST"])
def ai_move():
    g = _get_session()
    if g is None:
        return jsonify({"error": "no active game"}), 404

    if g.mode not in ("ab", "sarsa"):
        return jsonify({"error": "current mode has no AI"}), 400
    if g.currentPlayer != ga.AI_PLAYER:
        return jsonify({"error": "not the AI's turn"}), 400
    if g.gameOver:
        return jsonify({"error": "game is over"}), 400

    try:
        result = ga.apply_ai_move(g)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5050)
