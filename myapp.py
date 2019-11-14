from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_file
from database import db_session
from models import Racket, Member, WarBase, Settings
from flask_bootstrap import Bootstrap
import pytz
from datetime import datetime
import json
from forms import FactionIDForm
import subprocess
import os
import plotly
from werkzeug.utils import secure_filename
import requests
import pandas as pd
from pathlib import Path


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
api_key = os.environ.get('api_header_key')
UPLOAD_FOLDER = './csvs/'
ALLOWED_EXTENSIONS = ['csv']
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def index():
    get_rackets = Racket.query.order_by(Racket.Level.desc()).all()
    return render_template('index.html', rackets=get_rackets)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def make_the_fucking_csv():
    the_list = []
    pys = Path("csvs")
    the_list.append(" ")
    for file in pys.glob("*.csv"):
        file = str(file.name)
        the_list.append(file)
    return the_list


def list_reports():
    the_list = []
    pys = Path("reports")
    the_list.append(" ")
    for file in pys.glob("*.json"):
        file = str(file.name)
        the_list.append(file)
    return the_list


@app.route("/tools", methods=["GET", "POST"])
def thetool():
    if request.method == "GET":
        return render_template('tools.html', beforeform=make_the_fucking_csv(), afterform=make_the_fucking_csv())

    if request.method == "POST":
        if not request.form:
            uploaded_files = request.files.getlist("file")
            for file in uploaded_files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return render_template('tools.html', beforeform=make_the_fucking_csv(), afterform=make_the_fucking_csv())

        if request.form:
            try:
                defbefore = pd.read_csv(f'./csvs/{request.form["BeforeCSV"]}')
                defafter = pd.read_csv(f'./csvs/{request.form["AfterCSV"]}')
                beforeLinkRemove = defbefore.drop(defbefore.columns[[1]], axis=1)
                beforeLinkRemove.columns = ['Player', 'Before']
                afterLinkRemove = defafter.drop(defafter.columns[[1]], axis=1)
                afterLinkRemove.columns = ['Player', 'After']
                new = (
                    pd.concat([beforeLinkRemove, afterLinkRemove[afterLinkRemove.Player.isin(beforeLinkRemove.Player)]],
                              sort=True, axis=1))
                new = new.loc[:, ~new.columns.duplicated()]
                new['Difference'] = new.apply(lambda x: x['After'] - x['Before'], axis=1)
                faction_url = f"https://api.torn.com/faction/?selections=&key={os.environ.get('torn_api_key')}"
                test = requests.get(faction_url)
                members = test.json()
                list_mems = list(members['members'][x]['name'] for x in members['members'])
                new = new[new['Player'].isin(list_mems)]
                new = new[new['Difference'] != 0]
                new.to_csv(r'./csvs/csv3.csv', index=False)
                return send_file('./csvs/csv3.csv', attachment_filename='completed.csv', as_attachment=True)
            except Exception as e:
                logging.error(f'POST /tools {e}')


def build_report(filename):
    with open(f'./reports/{filename}') as json_file:
        data = json.load(json_file)
    x = []
    y = []
    for item in data:
        x.append(data[item].get("Name"))
        y.append(data[item].get("XanThisMonth"))
    the_dict = [dict(x=x, y=y, type='bar')]
    graphs = [
        dict(
            data=the_dict,
            layout=dict(
                title='Report'
            )
        )
    ]
    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    kwargs = [dict(x=list(data.keys()), y=list(item.get("y") for item in data.values()), type="bar")]
    #print(kwargs)
    return ids, graphJSON


@app.route('/reports', methods=['GET', 'POST'])
def displayreports():
    if request.method == "GET":
        return render_template('reports.html', form=list_reports())

    if request.method == "POST":
        build_it = build_report(request.form["Report"])
        ids = build_it[0]
        graphJSON = build_it[1]
        return render_template('reports.html', ids=ids, graphJSON=graphJSON, form=list_reports())


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

            # print(to_json)
            logging.info('/api/member PUT json passed')
            for member in to_json:
                refills = 0
                xan = 0
                lsd = 0
                se = 0
                xanthismonth = 0
                last_seen = 'Today'

                if 'days' in to_json[member]['last_action']['relative'] or 'day' in to_json[member]['last_action'][
                    'relative']:
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
                    test = Member(LastSeen=last_seen, TornID=member, Name=to_json[member]['name'],
                                  Rank=to_json[member]['rank'], Level=to_json[member]['level'],
                                  Age=to_json[member]['age'], Refills=refills, Xan=xan, XanThisMonth=xanthismonth,
                                  LSD=lsd, StatEnhancers=se)
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


@app.route("/api/members/clean", methods=['POST'])
def apimembersclean():
    if request.headers.get("X-Api-Key") == api_key:
        if request.method == "POST":
            try:
                logging.info(f'/api/member/clean POST scrubbing the database')
                all_members = Member.query.order_by(Member.Level.desc()).all()
                get_db = {}
                for item in all_members:
                    get_db[item.TornID] = item.dict_info()
                faction_url = f"https://api.torn.com/faction/?selections=&key={os.environ.get('torn_api_key')}"
                test = requests.get(faction_url)
                get_fac = test.json()['members']
                logging.info(f'/api/members/clean POST get db{get_db}')
                logging.info(f'/api/members/clean POST get fac{get_fac}')
                for x in get_db:
                    if str(x) not in get_fac and str(x) != "107444":  # probably dont wanna delete west...
                        user = Member.query.filter_by(TornID=x).first()
                        db_session.delete(user)
                    db_session.commit()
                logging.info(f'/api/member/clean POST scrubbed')
                return "scrubbing done", 200
            except Exception as e:
                logging.error(f'/api/members/clean POST failed {e}')
                return f"clean members failed: {e}", 500
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


@app.route("/api/members/reset", methods=['POST'])
def apimembersreset():
    if request.headers.get("X-Api-Key") == api_key:
        if request.method == "POST":
            try:
                all_members = Member.query.order_by(Member.XanThisMonth.desc()).all()
                the_dict = {}
                for item in all_members:
                    the_dict[str(item.TornID)] = item.dict_info()
                logging.info(f'/api/members/reset GET sent {jsonify(the_dict)}')
                copy_dict = the_dict.copy()
                today = datetime.today()
                d1 = today.strftime("%b-%d-%Y")
                with open(f'./reports/{d1}.json', 'w', encoding='utf-8') as f:
                    json.dump(copy_dict, f, ensure_ascii=False, indent=4)
                for member in all_members:
                    member.XanThisMonth = 0
                db_session.commit()
                return jsonify({"message": f"Reset: {copy_dict}"}), 200
            except Exception as e:
                logging.info(f'/api/members/reset POST failed {e}')
                db_session.rollback()
    else:
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
                        new_racket = Racket(TerritoryName=racket, RacketName=to_json[racket]['name'],
                                            Reward=to_json[racket]['reward'],
                                            Created=to_json[racket]['created'], Changed=to_json[racket]['changed'],
                                            Owner=to_json[racket]['faction'], OwnerName=to_json[racket]['factionname'],
                                            Level=to_json[racket]['level'])
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

            # print(to_json)
            logging.info('/api/warbase PUT json passed')
            for member in to_json:
                refills = 0
                xan = 0
                lsd = 0
                se = 0
                last_seen = 'Today'

                if 'days' in to_json[member]['last_action']['relative'] or 'day' in to_json[member]['last_action'][
                    'relative']:
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
                    test = WarBase(LastSeen=last_seen, Status=to_json[member]['status'][0], TornID=member,
                                   Name=to_json[member]['name'], Rank=to_json[member]['rank'],
                                   Level=to_json[member]['level'], Age=to_json[member]['age'], Refills=refills, Xan=xan,
                                   LSD=lsd, StatEnhancers=se)
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
