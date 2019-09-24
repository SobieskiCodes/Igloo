from flask import Flask, render_template, request
from database import db_session
from models import Racket, Member
from flask_bootstrap import Bootstrap
import pytz
from datetime import datetime
import json

def datetimefilter(value, format="%d/%m/%y %I:%M %p"):
    value = datetime.fromtimestamp(value)
    tz = pytz.timezone('US/Eastern')
    utc = pytz.timezone('UTC')
    value = utc.localize(value, is_dst=None).astimezone(pytz.utc)
    local_dt = value.astimezone(tz)
    return local_dt.strftime(format)


app = Flask(__name__)
app.jinja_env.filters['datetimefilter'] = datetimefilter
app.secret_key = 'dev'
app.config['DEBUG'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstrap = Bootstrap(app)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def index():
    get_rackets = Racket.query.order_by(Racket.Level.desc()).all()
    return render_template('index.html', rackets=get_rackets)


@app.route('/members')
def members():
    get_members = Member.query.order_by(Member.Level.desc()).all()
    return render_template('members.html', members=get_members)


@app.route("/themembers", methods=('GET', 'POST'))
def TheMembers():
    if request.method == "GET":
        test = Member.query.order_by(Member.Level.desc()).all()
        the_dict = {}
        for item in test:
            the_dict[item.TornID] = item.dict_info()
        return the_dict

    if request.method == "POST":
        to_json = json.loads(request.data.decode("utf-8").replace("'", '"'))
        return "done"


@app.route("/therackets", methods=('GET', 'POST'))
def TheRackets():
    if request.method == "GET":
        test = Racket.query.order_by(Racket.Level.desc()).all()
        the_dict = {}
        for item in test:
            the_dict[item.TerritoryName] = item.dict_info()
        return the_dict

    if request.method == "POST":
        to_json = json.loads(request.data.decode("utf-8").replace("'", '"'))
        return "done"


if __name__ == "__main__":
    app.run(host="0.0.0.0")
