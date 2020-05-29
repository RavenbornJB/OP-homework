from flask import Flask, render_template, redirect, request, url_for
from scripts.game_adt import GameList
import json


app = Flask(__name__)
app.config.update(SECRET_KEY='my_email_password', SEND_FILE_MAX_AGE_DEFAULT=0)
with open("data/games.json") as f:
    game_json = json.load(f)


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")


@app.route("/quiz", methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        data = request.form

        # Get age, if not integer, redirect to wrong_age.
        age = data.get("age")
        if not age.isdigit():
            return redirect(url_for("wrong_age"))
        else:
            age = 2020 - int(age)

        # Get lists of genres, themes, game_modes, and platforms.
        genres = data.getlist("genres")
        themes = data.getlist("themes")
        game_modes = data.getlist("game_modes")
        platforms = data.getlist("platforms")

        # Get years, if not both integers or first bigger than second, redirect to wrong_year.
        year_range = [data.get("year1"), data.get("year2")]
        if year_range[0] == "": year_range[0] = '1984'
        if year_range[1] == "": year_range[1] = '2019'
        if (not (year_range[0].isdigit() and year_range[1].isdigit())
                or int(year_range[0]) > int(year_range[1])
                or int(year_range[0]) > 2019 or int(year_range[1]) < 1984):
            return redirect(url_for("wrong_year"))
        else:
            year_range = list(map(int, year_range))

        # Finally, use the information to score the games
        # from my data/games.json database
        game_list = GameList(game_json)
        top_games = game_list.score(genres, themes, game_modes, platforms, year_range, age)

        return render_template("top_games.html", top_games=top_games)
    return render_template("quiz.html")


@app.route("/wrong_age", methods=['GET', 'POST'])
def wrong_age():
    if request.method == 'POST':
        return redirect(url_for("quiz"))
    return render_template("wrong_age.html")


@app.route("/wrong_year", methods=['GET', 'POST'])
def wrong_year():
    if request.method == 'POST':
        return redirect(url_for("quiz"))
    return render_template("wrong_year.html")


@app.route("/game", methods=['GET', 'POST'])
def game():
    req_game_slug = request.args.get('g', None)
    game_list = GameList(game_json)
    req_game = game_list.sloc(req_game_slug)
    return render_template("game.html", game=req_game)


@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_game = request.form.get("search-game")
        game_list = GameList(game_json)
        games = [game_ for game_ in game_list if search_game in game_.name]
        return render_template("search.html", search_string=search_game, search_result=games)


if __name__ == '__main__':
    app.run()
