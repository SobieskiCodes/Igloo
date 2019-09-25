from flask import Flask, render_template, request, jsonify
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
api_key = "802e3a09-f0bf-4536-b30d-37629d490c99" #this will be a system env that the bot can add to.

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


@app.route("/api/test", methods=['GET'])
def apitest():
    if request.headers.get("X-Api-Key") == api_key:
        return jsonify({"message": "OK: Authorized"}), 200
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


@app.route("/api/members/reset", methods=['POST'])
def apimembersreset():
    if request.headers.get("X-Api-Key") == api_key:
        if request.method == "POST":
            all_members = Member.query.order_by(Member.Level.desc()).all()
            for member in all_members:
                member.XanThisMonth = 0
            db_session.commit()
            return "all set", 200
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


@app.route("/api/members", methods=['GET', 'PUT'])
def apimembers():
    if request.headers.get("X-Api-Key") == api_key:
        if request.method == "GET":
            all_mems = Member.query.order_by(Member.Level.desc()).all()
            the_dict = {}
            for item in all_mems:
                the_dict[item.TornID] = item.dict_info()
            return jsonify(the_dict), 200

        if request.method == "PUT":
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
                if not user:
                    test = Member(LastSeen=last_seen, TornID=member, Name=to_json[member]['name'], Rank=to_json[member]['rank'], Level=to_json[member]['level'], Age=to_json[member]['age'], Refills=refills, Xan=xan, XanThisMonth=xanthismonth, LSD=lsd, StatEnhancers=se)
                    db_session.add(test)
                    db_session.commit()
                if user:
                    if xan != 0:
                        if xan > user.Xan:
                            user.XanThisMonth = user.XanThisMonth + (xan - user.Xan)
                            print(user, user.XanThisMonth)

                    user.LastSeen = last_seen
                    user.Name = to_json[member]['name']
                    user.Rank = to_json[member]['rank']
                    user.Level = to_json[member]['level']
                    user.Age = to_json[member]['age']
                    user.Refills = refills
                    user.Xan = xan
                    user.XanThisMonth = user.XanThisMonth
                    user.LSD = lsd
                    user.StatEnhancers = se
                    db_session.commit()
            return "members done", 200
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


@app.route("/api/rackets", methods=['GET', 'PUT'])
def apirackets():
    if request.headers.get("X-Api-Key") == api_key:
        if request.method == "GET":
            get_rackets = Racket.query.order_by(Racket.Level.desc()).all()
            the_dict = {}
            for item in get_rackets:
                the_dict[item.TerritoryName] = item.dict_info()
            return jsonify(the_dict), 200

        if request.headers.get("X-Api-Key") == api_key:
            if request.method == "PUT":
                to_json = json.loads(request.data.decode("utf-8").replace("'", '"'))
                input_list = [racket for racket in to_json]
                the_rackets = Racket.query.order_by(Racket.Level.desc()).all()
                db_list = [racket.TerritoryName for racket in the_rackets]
                for racket in db_list:
                    if racket not in input_list:
                        racket_to_remove = Racket.query.filter_by(TerritoryName=racket).first()
                        db_session.delete(racket_to_remove)
                    if racket in input_list:
                        racket_to_update = Racket.query.filter_by(TerritoryName=racket).first()
                        racket_to_update.RacketName = to_json[racket]['name']
                        racket_to_update.Reward = to_json[racket]['reward']
                        racket_to_update.Changed = to_json[racket]['changed']
                        racket_to_update.Owner = to_json[racket]['faction']
                        racket_to_update.OwnerName = to_json[racket]['factionname']
                        racket_to_update.Level = to_json[racket]['level']
                db_session.commit()
                for racket in input_list:
                    if racket not in db_list:
                        new_racket = Racket(TerritoryName=racket, RacketName=to_json[racket]['name'], Reward=to_json[racket]['reward'],
                                      Created=to_json[racket]['created'], Changed=to_json[racket]['changed'],
                                      Owner=to_json[racket]['faction'], OwnerName=to_json[racket]['factionname'], Level=to_json[racket]['level'])
                        db_session.add(new_racket)
                        db_session.commit()
                return "rackets done", 200
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


if __name__ == "__main__":
    app.run(host="0.0.0.0")
