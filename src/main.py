import typing
from flask import Flask, jsonify, render_template, request

import functions

app = Flask(__name__)


@app.route("/")
def index_route():
    return render_template("index.html")


@app.route("/map")
def map_route():
    return render_template("map.html")


@app.route("/players")
def players_route():
    return render_template("players.html")


@app.route("/sites")
def sites_route():
    return render_template("sites.html")


@app.route("/api/motd")
def api_motd_route():
    try:
        return jsonify(
            functions.MOTD(
                request.args.get("host", ""),
                int(request.args.get("port", "25565")),
            ).get_motd()
        )
    except (ValueError, ConnectionError, TimeoutError):
        return jsonify({})


@app.route("/api/player")
def api_player_route():
    try:
        uuids = request.args.get("uuids").split(",")  # type: ignore
    except (ValueError, AttributeError):
        uuids = []

    try:
        names = request.args.get("names").split(",")  # type: ignore
    except (ValueError, AttributeError):
        names = []

    try:
        return jsonify(functions.Player(uuid=uuids, name=names).get_profiles())
    except AssertionError:
        return jsonify([])


@app.route("/api/players_at_server")
def api_players_at_server_route():
    try:
        motd = (
            functions.MOTD(
                request.args.get("host", ""),
                int(request.args.get("port", "25565")),
            ).get_motd()
            or {"players": []}
        )["players"]

        return jsonify(
            functions.Player(
                uuid=list(map(lambda p: p["id"], motd)),  # type: ignore
                name=list(map(lambda p: p["name"], motd)),  # type: ignore
            ).get_profiles()
        )
    except (ValueError, ConnectionError, TimeoutError, AssertionError):
        return jsonify([])


if __name__ == "__main__":
    app.run(debug=True)
