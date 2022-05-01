from flask import Flask, render_template, request, jsonify
app = Flask(__name__)
import db

@app.before_first_request
def initialize():
    db.setup()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/thanks')
def thanks():
    return render_template("thanks.html")

@app.route('/decline')
def decline():
    return render_template("decline.html")

@app.route('/survey', methods=["GET"])
def get_survey():
    return render_template('survey.html')

@app.route('/survey', methods=["POST"])
def post_survey():

    favorite_movie = request.form.get("fill_in")
    favorite_movie_genre = request.form.get("favorite_genre")
    aspect = request.form.get("aspect")
    watched_uncharted = request.form.get("watched_uncharted")
    favorite_info_about_uncharted = request.form.get("conditional_answer")
    db.add_response(favorite_movie,favorite_movie_genre,aspect,watched_uncharted,favorite_info_about_uncharted)
    return render_template('thanks.html')

@app.route('/api/results')
def api_results():
    isReverse = request.args.get('reverse')
    if isReverse == "true":
        isReverse = False
    else:
        isReverse = True
    
    results = db.api_results(isReverse)
    # return jsonify(results)
    #   for result in results:
    #     result = jsonify(results)
    return render_template('api_results.html', results=results)


