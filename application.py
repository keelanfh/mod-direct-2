from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
import pandas
import re

app = Flask(__name__)

# Flask-SQLAlchemy
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///modules.db"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)


class Module(db.Model):
    __tablename__ = "modules"
    id = db.Column(db.Text, primary_key=True)
    title = db.Column(db.Text)
    level = db.Column(db.Text)
    value = db.Column(db.Float)
    description = db.Column(db.Text)
    programme_year = db.Column(db.Integer)
    teaching_method = db.Column(db.Text)
    reading = db.Column(db.Text)
    term = db.Column(db.Integer)
    assessment_method = db.Column(db.Text)
    available_external = db.Column(db.Boolean)
    available_affiliate = db.Column(db.Boolean)
    aims = db.Column(db.Text)
    content = db.Column(db.Text)
    people = db.Column(db.Text)
    course_website = db.Column(db.Text)
    prereqs = db.Column(db.Text)
    financial_contribs = db.Column(db.Text)
    url = db.Column(db.Text)
    _machine_url = db.Column(db.Text)

    def __init__(self, code, title, level, value):
        self.id = code.upper()
        self.title = title
        self.level = level
        self.value = value

    # Return department code
    @property
    def dept_code(self):
        return self.id[:4]

    # Return only the numbers in the module code
    @property
    def num_code(self):
        return "".join(x for x in self.id if x.isdigit())

    # Return lowercase item
    @property
    def lower_code(self):
        return self.id.lower()

    # Return the URL to machine-readable data.
    # Return human-readable URL if that is not present.
    @property
    def machine_url(self):
        try:
            return self._machine_url
        except AttributeError:
            try:
                return self.url
            except AttributeError:
                return None

    @machine_url.setter
    def machine_url(self, url):
        self._machine_url = url

    @property
    def moodle_url(self):
        return "https://moodle.ucl.ac.uk/course/search.php?search=" + self.id

    @property
    def exams_url(self):
        return "http://ucl-primo.hosted.exlibrisgroup.com/primo_library/libweb/action/search.do?ct=facet&fctN=facet_rtype&fctV=exam_papers&rfnGrp=1&rfnGrpCounter=1&frbg=&fn=search&indx=1&dscnt=0&scp.scps=scope%3A(UCL)%2Cprimo_central_multiple_fe&vid=UCL_VU1&mode=Basic&ct=search&srt=rank&tab=local&vl(freeText0)=" + self.id + "&dum=true"

    @property
    def readinglist_url(self):
        return "http://readinglists.ucl.ac.uk/search.html?q=" + self.id

    def update_urls(self):
        self._moodle_url = self.moodle_url
        self._exams_url = self.exams_url
        self._readinglist_url = self.readinglist_url

    @property
    def html_description(self):
        return make_html(self.description)

    @property
    def html_prereqs(self):
        return make_html(self.prereqs)

    @property
    def html_teaching_method(self):
        return make_html(self.teaching_method)

    @property
    def level_pretty(self):
        if self.level == "ADV":
            return "Advanced"
        if self.level == "INTER":
            return "Intermediate"
        if self.level == "FIRST":
            return "First"

    def yesno_to_boolean(self, text):
        if text == "Yes":
            return True
        elif text == "No":
            return False
        else:
            return None

    @property
    def set_available_affiliate(self):
        raise NotImplementedError()

    @set_available_affiliate.setter
    def set_available_affiliate(self, text):
        self.available_affiliate = self.yesno_to_boolean(text)

    @property
    def set_available_external(self):
        raise NotImplementedError()

    @set_available_external.setter
    def set_available_external(self, text):
        self.available_external = self.yesno_to_boolean(text)


@app.route("/")
def index():
    rows = Module.query.all()
    return render_template("index.html", modules=rows)


@app.route("/module/<module_id>")
def module(module_id):
    module_id = module_id.upper()
    module = Module.query.filter_by(id=module_id).first()
    return render_template("module.html", module=module)


def import_from_running_list():
    # Open excel file with the list of modules
    module_list = pandas.read_excel('data/running_list.xlsx')

    # Create a Module object containing this information, then output to dict
    for x in module_list.itertuples():
        module = Module(code=x.Code, title=x.Title, level=x.Level, value=x.Value)
        db.session.add(module)
    db.session.commit()


def make_html(result):
    if result is None:
        return None
    # Hyperlink all Geography links
    result = re.sub(r"(GEOG)\s*([0-9]{4})", r'<a href="/module/\1\2">\1\2</a>', result)
    return re.sub(r"\n", r'<br/>', result)
