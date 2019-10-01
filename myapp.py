from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from database import db_session
from models import Racket, Member, WarBase, Settings
from flask_bootstrap import Bootstrap
import pytz
from datetime import datetime
import json
from forms import FactionIDForm
import subprocess
import os

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
api_key = os.environ.get('api_header_key') #this will be a system env that the bot can add to.

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


@app.route('/warbase', methods=['GET', 'POST'])
def thewarbase():
    db_query = Settings.query.order_by(Settings.WarbaseFaction).first()
    the_id = "No faction stored" if not db_query else db_query.WarbaseFaction
    the_form = FactionIDForm(obj=db_query, WarbaseFaction=the_id)
    get_members = WarBase.query.order_by(WarBase.Level.desc()).all()
    if request.method == "POST":
        if the_form.validate_on_submit():
            try:
                get_input = request.form['WarbaseFaction']
                if not db_query:
                    form = Settings(WarbaseFaction=get_input)
                    db_session.add(form)
                    db_session.commit()
                    flash('Saved successfully', 'success')
                if db_query:
                    print(type(db_query.WarbaseFaction))
                    print(type(get_input))
                    if str(db_query.WarbaseFaction) != str(get_input):
                        db_query.WarbaseFaction = get_input
                        all_mems = WarBase.query.order_by(WarBase.Level.desc()).all()
                        for person in all_mems:
                            db_session.delete(person)
                        db_session.commit()
                        get_members = WarBase.query.order_by(WarBase.Level.desc()).all()
            except Exception as e:
                print(e)
                db_session.rollback()
                flash('Error updating faction.', 'danger')

            return render_template('warbase.html', members=get_members, form=the_form)

    if request.method == "GET":
        return render_template('warbase.html', members=get_members, form=the_form)


@app.route('/runupdate', methods=['GET'])
def runupdate():
    if request.method == "GET":
        logging.info('GET /runupdate received')
        db_query = Settings.query.order_by(Settings.WarbaseFaction).first()
        if db_query:
            process = subprocess.Popen(['python', 'updatewarbase.py', f"{db_query.WarbaseFaction}"])
            logging.info('GET /runupdate started')
        return redirect(url_for('thewarbase'))


@app.route("/api/test", methods=['GET'])
def apitest():
    if request.headers.get("X-Api-Key") == api_key:
        logging.info('GET /api/test received')
        return jsonify({"message": "OK"}), 200
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


@app.route("/api/members/reset", methods=['POST'])
def apimembersreset():
    if request.headers.get("X-Api-Key") == api_key:
        if request.method == "POST":
            all_members = Member.query.order_by(Member.XanThisMonth.desc()).all()
            for member in all_members:
                member.XanThisMonth = 0
            db_session.commit()
            the_dict = {}
            for item in all_members:
                the_dict[item.TornID] = item.dict_info()
            logging.info(f'/api/members/reset GET sent {jsonify(the_dict)}')
            return jsonify({"message": f"Reset: {the_dict}"}), 200
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


@app.route("/api/members", methods=['GET', 'PUT'])
def apimembers():
    if request.headers.get("X-Api-Key") == api_key:
        if request.method == "GET":
            logging.info('/api/member GET received')
            all_mems = Member.query.order_by(Member.Level.desc()).all()
            the_dict = {}
            for item in all_mems:
                the_dict[item.TornID] = item.dict_info()
            logging.info(f'/api/member GET sent {jsonify(the_dict)}')
            return jsonify(the_dict), 200

        if request.method == "PUT":
            try:
                logging.info('/api/member PUT received')
                to_json = json.loads(request.data)
            except Exception as e:
                exc = f'{type(e).__name__}: {e}'
                logging.warning(f'/api/member PUT failed to load json {exc}')
                return jsonify(e)

            #print(to_json)
            logging.info('/api/member PUT json passed')
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
                    try:
                        logging.info(f'/api/member PUT adding member {test}')
                        db_session.commit()
                    except Exception as e:
                        logging.warning(f'/api/member PUT adding member {test} failed {e}')
                        db_session.rollback()

                if user:
                    if xan != 0:
                        if xan > user.Xan:
                            user.XanThisMonth = user.XanThisMonth + (xan - user.Xan)

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
                    try:
                        logging.info(f'/api/member PUT updating member {user.Name}')
                        db_session.commit()
                    except Exception as e:
                        logging.warning(f'/api/member PUT updating member {user.Name} failed {e}')
                        db_session.rollback()
            logging.info(f'/api/member PUT completed')
            return "members done", 200
    else:
        logging.warning(f'/api/member PUT unauthorized attempt')
        return jsonify({"message": "ERROR: Unauthorized"}), 401


@app.route("/api/rackets", methods=['GET', 'PUT'])
def apirackets():
    if request.headers.get("X-Api-Key") == api_key:
        if request.method == "GET":
            logging.info('/api/racket GET received')
            get_rackets = Racket.query.order_by(Racket.Level.desc()).all()
            the_dict = {}
            for item in get_rackets:
                the_dict[item.TerritoryName] = item.dict_info()
            return jsonify(the_dict), 200

        if request.headers.get("X-Api-Key") == api_key:
            if request.method == "PUT":
                logging.info('/api/racket PUT received')
                to_json = json.loads(request.data)
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
                try:
                    logging.info(f'/api/rackets PUT updating rackets')
                    db_session.commit()
                except Exception as e:
                    logging.warning(f'/api/rackets PUT updating rackets failed {e}')
                    db_session.rollback()
                for racket in input_list:
                    if racket not in db_list:
                        new_racket = Racket(TerritoryName=racket, RacketName=to_json[racket]['name'], Reward=to_json[racket]['reward'],
                                      Created=to_json[racket]['created'], Changed=to_json[racket]['changed'],
                                      Owner=to_json[racket]['faction'], OwnerName=to_json[racket]['factionname'], Level=to_json[racket]['level'])
                        db_session.add(new_racket)
                        try:
                            logging.info(f'/api/rackets PUT updating rackets')
                            db_session.commit()
                        except Exception as e:
                            logging.info(f'/api/rackets PUT updating rackets failed {e}')
                            db_session.rollback()
                return "rackets done", 200
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


@app.route("/api/warbase", methods=['GET', 'PUT'])
def apiwarbase():
    if request.headers.get("X-Api-Key") == api_key:
        if request.method == "GET":
            logging.info('/api/warbase GET received')
            all_mems = WarBase.query.order_by(WarBase.Level.desc()).all()
            the_dict = {}
            for item in all_mems:
                the_dict[item.TornID] = item.dict_info()
            logging.info(f'/api/warbase GET sent {jsonify(the_dict)}')
            return jsonify(the_dict), 200

        if request.method == "PUT":
            try:
                logging.info('/api/warbase PUT received')
                to_json = json.loads(request.data)
            except Exception as e:
                exc = f'{type(e).__name__}: {e}'
                logging.warning(f'/api/warbase PUT failed to load json {exc}')
                return jsonify(e)

            #print(to_json)
            logging.info('/api/warbase PUT json passed')
            for member in to_json:
                refills = 0
                xan = 0
                lsd = 0
                se = 0
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

                user = WarBase.query.filter_by(TornID=member).first()
                if not user:
                    test = WarBase(LastSeen=last_seen, Status=to_json[member]['status'][0], TornID=member, Name=to_json[member]['name'], Rank=to_json[member]['rank'], Level=to_json[member]['level'], Age=to_json[member]['age'], Refills=refills, Xan=xan, LSD=lsd, StatEnhancers=se)
                    db_session.add(test)
                    try:
                        logging.info(f'/api/warbase PUT adding member {test.Name}')
                        db_session.commit()
                    except Exception as e:
                        logging.warning(f'/api/warbase PUT adding member {test} failed {e}')
                        db_session.rollback()

                if user:
                    user.LastSeen = last_seen
                    user.Status = to_json[member]['status'][0]
                    user.Name = to_json[member]['name']
                    user.Rank = to_json[member]['rank']
                    user.Level = to_json[member]['level']
                    user.Age = to_json[member]['age']
                    user.Refills = refills
                    user.Xan = xan
                    user.LSD = lsd
                    user.StatEnhancers = se
                    try:
                        logging.info(f'/api/warbase PUT updating member {user.Name}')
                        db_session.commit()
                    except Exception as e:
                        logging.warning(f'/api/warbase PUT updating member {user.Name} failed {e}')
                        db_session.rollback()
            logging.info(f'/api/warbase PUT completed')



class Log:
    def __init__(self, file_name: str):
        self.file_name = file_name

    def info(self, message: str):
        self._write(f':INFO: {message}')

    def error(self, message: str):
        self._write(f':ERROR: {message}')

    def warning(self, message: str):
        self._write(f':WARNING: {message}')

    def critical(self, message: str):
        self._write(f':CRITICAL: {message}')

    def _write(self, message: str):
        with open(self.file_name, 'a') as file:
            file.write(f'logging {message} \n')


logging = Log('./test.log')
logging.info('starting up')
if __name__ == "__main__":
    app.run(host="0.0.0.0")
