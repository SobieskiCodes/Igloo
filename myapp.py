from flask import Flask, render_template, request
from database import db_session
from models import Racket, Member
from flask_bootstrap import Bootstrap
import pytz
from datetime import datetime
import json


def datetimefilter(value, theformat="%d/%m/%y %I:%M %p"):
    value = datetime.fromtimestamp(value)
    tz = pytz.timezone('US/Eastern')
    utc = pytz.timezone('UTC')
    value = utc.localize(value, is_dst=None).astimezone(pytz.utc)
    local_dt = value.astimezone(tz)
    return local_dt.strftime(theformat)


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
def themembers():
    if request.method == "GET":
        test = Member.query.order_by(Member.Level.desc()).all()
        the_dict = {}
        for item in test:
            the_dict[item.TornID] = item.dict_info()
        return the_dict

    if request.method == "POST":
        to_json = json.loads(request.data.decode("utf-8").replace("'", '"'))
        #print(to_json)
        for member in to_json:
            refills = 0
            xan = 0
            lsd = 0
            se = 0
            xanthismonth = 0
            last_seen = 'Today'

            if 'days' in to_json[member]['last_action']['relative'] or 'day' in to_json[member]['last_action']['relative']:
                if 'day' in to_json[member]['last_action']['relative']:
                    last_seen = 'Yesterday'
                if 'days' in to_json[member]['last_action']['relative']:
                    last_seen = to_json[member]['last_action']['relative']

            if 'refills' in to_json[member]['personalstats']:
                refills = to_json[member]['personalstats']['refills']

            if 'xantaken' in to_json[member]['personalstats']:
                xan = to_json[member]['personalstats']['xantaken']

            if 'lsdtaken' in to_json[member]['personalstats']:
                lsd = to_json[member]['personalstats']['lsdtaken']

            if 'statenhancersused' in to_json[member]['personalstats']:
                se = to_json[member]['personalstats']['statenhancersused']

            user = Member.query.filter_by(TornID=member).first()
            print(user.Xan)
            if not user:
                test = Member(LastSeen=last_seen, TornID=member, Name=to_json[member]['name'], Rank=to_json[member]['rank'], Level=to_json[member]['level'], Age=to_json[member]['age'], Refills=refills, Xan=xan, XanThisMonth=xanthismonth, LSD=lsd, StatEnhancers=se)
                db_session.add(test)
                db_session.commit()
            if user:
                print(user, xan, user.Xan, user.XanThisMonth)
                if xan != 0:
                    if xan > user.Xan:
                        print(user.XanThisMonth + (xan - user.Xan))
                        xanthismonth = user.XanThisMonth + (xan - user.Xan)
                    if not xan > user.Xan:
                        xanthismonth = user.XanThisMonth

                user.LastSeen = last_seen
                user.Name = to_json[member]['name']
                user.Rank = to_json[member]['rank']
                user.Level = to_json[member]['level']
                user.Age = to_json[member]['age']
                user.Refills = refills
                user.Xan = xan
                user.XanThisMonth = xanthismonth
                user.LSD = lsd
                user.StatEnhancers = se
                db_session.commit()

        return "done"


@app.route("/therackets", methods=('GET', 'POST'))
def therackets():
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
