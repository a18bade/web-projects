# from asyncio.windows_events import NULL
from dataclasses import replace
from random import betavariate
from re import search
from urllib import response
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

from dotenv import load_dotenv, find_dotenv
from wtforms import Form, BooleanField, StringField, RadioField, SelectField, validators
from wtforms.fields import DateField
from authlib.integrations.flask_client import OAuth
from urllib.parse import urlencode
import db
import os

ACCEPTABLE_COURSES = ["Acorn Park", "Alimagnet Park", "Bassett Creek", "Bethel University", "Bryant Lake", "Bunker Hills", "Coon Rapids", "Elm Creek Park",
            "Ham Lake", "Hyland Park", "Lochness", "Minnehaha Falls", "Red Oak Park", "River Front", "Sunnyside Park"]

app = Flask(__name__)
app.secret_key = "asdfhjlqnwejlvlasdfwqaero1i139fjwdf"

oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id= os.environ['CLIENT_ID'],
    client_secret= os.environ['CLIENT_SECRET'],
    api_base_url= os.environ['API_BASE_URL'],
    access_token_url= os.environ['ACCESS_TOKEN_URL'],
    authorize_url= os.environ['AUTHORIZE_URL'],
    client_kwargs={
        'scope': 'openid profile email',
    },
)

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'profile' not in session:
      # Redirect to Login page here
      return redirect('/')
    return f(*args, **kwargs)

  return decorated

@app.before_first_request
def initialize():
    db.setup()

def getLoggedInUserInfo():
     if 'profile' not in session:
        return ''
     else:
        profile = session['profile'] 
        user_id = profile['user_id']
        return user_id

def getLoggedInUserNickname():
    if 'profile' not in session:
        return ''
    else:
        profile = session['profile'] 
        nickname = profile['nickname']
        return nickname

@app.route('/')
def main():
    best_player = db.get_best_player()
    most_player = db.get_most_played()
    return render_template('main.html', data=getLoggedInUserInfo(), responses=best_player, most_played=most_player)

@app.route('/dashboard')
def dashboard():
    if 'profile' not in session:
        return render_template('not_loggedin.html')
    else:
        return render_template('dashboard.html',user_name=session['profile']['name'])

# scores ---------------------------------------------
@app.route('/scores', methods=['GET', 'POST'])
def scores(): 
    form = ScoreForm(request.form)
    labels = []
    scores = []
    strokes = []
    if request.method == 'POST' and form.validate():
        responses = db.get_score(order_asc=form.choose_ascending.data,\
            search_by=form.choose_data.data, column=form.choose_field.data)

        if (form.choose_ascending.data == False):
            date_responses = sorted(responses, key=lambda x: x[1], reverse=True)
        else:
            date_responses = sorted(responses, key=lambda x: x[1], reverse=False)

        for i in range(len(date_responses)):
            labels.append(str(date_responses[i][1]))
            scores.append(str(date_responses[i][3]))
            strokes.append(str(date_responses[i][4]))

        return render_template('scores.html', form=form, responses=responses, nickname=getLoggedInUserNickname(), data=getLoggedInUserInfo(),labels=labels,scores=scores,strokes=strokes)
    else:
        responses = db.get_score(order_asc=False, search_by="All", column="Score")
        if (form.choose_ascending.data == False):
            date_responses = sorted(responses, key=lambda x: x[1], reverse=True)
        else:
            date_responses = sorted(responses, key=lambda x: x[1], reverse=False)
        for i in range(len(date_responses)):
            labels.append(str(date_responses[i][1]))
            scores.append(str(date_responses[i][3]))
            strokes.append(str(date_responses[i][4]))
        return render_template('scores.html', form=form, responses=responses, nickname=getLoggedInUserNickname(), data=getLoggedInUserInfo(),labels=labels,scores=scores,strokes=strokes)

@app.route('/play', methods=['GET', 'POST'])
def play():
    if 'profile' in session:
        if request.method == 'POST':
            strokes = request.form['totalStrokesInput']
            if int(strokes) < 0:
                strokes = '0'
            score = request.form['totalScoreInput']
            course = request.form['courseInput']
            if course in ACCEPTABLE_COURSES:
                db.add_new_score(score, strokes, course)
                return redirect(url_for('personal_progress'))    
            else:
                return render_template('play.html', data=getLoggedInUserInfo())                        
        return render_template('play.html', data=getLoggedInUserInfo())
    return  redirect(url_for('login'))      

# login ---------------------------------------------
@app.route('/callback')
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'nickname': userinfo['nickname'],
        'email': userinfo['email'],
        'picture': userinfo['picture']
    
    }
    if 'profile' in session:
        nickname = userinfo['nickname']
        email = userinfo['email']
        db.add_user(nickname, email)
    return redirect(url_for('personal_progress'))

@app.route('/login')
def login():  
    return auth0.authorize_redirect(redirect_uri=url_for('callback_handling', _external = True))

@app.route('/logoutCallback')
def logout_callback_handling():
    return redirect(url_for('main'))

@app.route('/logout')
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('logout_callback_handling', _external=True), 'client_id': os.environ['CLIENT_ID']}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

# signup ---------------------------------------------
@app.route('/signup', methods=["GET", "POST"])
def post_signup():
    return render_template('signup.html')

# delete_score ---------------------------------------------
@app.route('/delete_score/<score_id>', methods = ["GET"])
def delete_score(score_id):
    db.delete_score(session['profile']['nickname'], score_id)
    return redirect(url_for('personal_progress'))

# edit_score ---------------------------------------------
@app.route('/edit_score/<score_id>', methods = ["GET"])
def edit_score(score_id):
    userData = db.get_score_by_id(score_id)
    userData = userData[0]
    ## To set the default time, change to string
    userData[0] = str(userData[1]).split()[0]
    userData[1] = str(userData[1]).split()[1]
    return render_template("update_score.html", userData=userData, courses=ACCEPTABLE_COURSES)

# update_score ---------------------------------------------
@app.route('/update_score/<score_id>', methods = ["GET", "POST"])
def get_update_score(score_id):
    updateData = {}
    if request.method == 'POST':
        updateData['date'] = request.form.get('date')
        updateData['time'] = request.form.get('time')
        updateData['course'] = request.form.get('course')
        updateData['score'] = request.form.get('score')
        updateData['strokes'] = request.form.get('strokes')
        db.update_score(session['profile']['nickname'], updateData, score_id)
        return redirect(url_for('personal_progress'))
    else:
        return render_template("update_score.html")

@app.route('/personal_progress', methods = ["GET", "POST"])
def personal_progress():
    result = db.get_user_data()
    form = personalProgressForm(request.form)
    scores = db.get_scores()
    dates = db.get_dates()
    strokes = db.get_strokes()
    if request.method == 'POST':
        course=form.choose_course.data
        dates=form.pick_date.data
        if (course == 'All' and dates is None):
            dates = db.get_dates()
            return render_template('personal_progress.html', data=getLoggedInUserInfo(), result=result, form=form,scores=scores,dates=dates,strokes=strokes)

        search_result = db.personal_progress_search(course, dates)
        scores = []
        strokes = []
        dates = []
        for result in search_result:
            dates.append(result[0])
            scores.append(result[2])
            strokes.append(result[3])
        return render_template('personal_progress.html', data=getLoggedInUserInfo(), search_result=search_result,form=form,scores=scores,dates=dates,strokes=strokes)
    else: 
        return render_template('personal_progress.html', data=getLoggedInUserInfo(), result=result, form=form,scores=scores,dates=dates,strokes=strokes)

# post_test ---------------------------------------------

@app.route('/post_test', methods=['GET', 'POST'])
def post_test():
    # form = SurveyForm(request.form)
    if request.method == 'POST' and form.validate():
        # db.add_response()          
        return render_template('scores.html')
    return render_template('scores.html')


STATES_AVAILABLE = [ '*Choose State*','Minnesota', 'More States to Come!']
COURSES_AVAILABLE = [ '*Choose State*']

class PlayForm(Form):
    choose_state = SelectField('Choose State', choices=STATES_AVAILABLE)
    choose_course = SelectField('Choose Course', choices=COURSES_AVAILABLE)

COLUMNS_AVAILABLE = ['Username', 'Date', 'Course', 'Score', 'Strokes']

class ScoreForm(Form):
    choose_field = SelectField('Choose Column', choices=COLUMNS_AVAILABLE)
    choose_data = StringField('Search by', [validators.Length(min=0, max=25)])
    choose_ascending = BooleanField('Ascending')

COLUMNS_AVAILABLE = [ "All", "Acorn Park", "Alimagnet Park", "Bassett Creek", "Bethel University", "Bryant Lake", "Bunker Hills", "Coon Rapids", "Elm Creek Park",
            "Ham Lake", "Hyland Park", "Lochness", "Minnehaha Falls", "Red Oak Park", "River Front", "Sunnyside Park"]

class personalProgressForm(Form):
    choose_course = SelectField('Search by course:', choices=COLUMNS_AVAILABLE)
    pick_date = DateField('DatePicker', format='%Y-%m-%d')


  




