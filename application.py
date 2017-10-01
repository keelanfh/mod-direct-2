from flask import Flask, render_template, Markup, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask.ext.restless import APIManager
import pandas
import re
import bleach

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
    students_2016 = db.Column(db.Integer)
    students_2015 = db.Column(db.Integer)
    students_2014 = db.Column(db.Integer)

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
        if self._machine_url is None:
            return self.url
        else:
            return self._machine_url

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

    @property
    def timetable_url(self):
        return "https://timetable.ucl.ac.uk/tt/moduleTimet.do?firstReq=Y&moduleId=" + self.id

    def update_urls(self):
        self._moodle_url = self.moodle_url
        self._exams_url = self.exams_url
        self._readinglist_url = self.readinglist_url

    @property
    def level_pretty(self):
        if self.level == "ADV":
            return "Advanced"
        if self.level == "INTER":
            return "Intermediate"
        if self.level == "FIRST":
            return "First"

    @staticmethod
    def yesno_to_boolean(text):

        # TODO change this - it shouldn't raise an error.

        trues = ["Yes", "yes", "Check with organiser that places are available.",
                 "Module numbers will be capped at 120 students",
                 "Contact organiser for availability of places.", "Contact the course organiser",
                 "Contact module organiser Professor Evans", "Contact organizer to check suitability.",
                 "Contact module organiser", "POSS 2", "Very limited number of places",
                 "Contact organizer to check availability.", "Affiliate students with relevant background.",
                 "The maximum number of places on the course is 120.", "Contact module organiser for more details.",
                 "Contact organiser for details.", "For more details contact module organiser.",
                 "Contact module organiser.", "Preference may be given to those with A level chem",
                 "Usually Human Sciences and Natural Sciences only",
                 "Not without pre-requisites and approval, see above",
                 "Only with appropriate background and approval (see",
                 "With prerequisittes and approval (see notes)",
                 "Module numbers will be capped at 100 students",
                 "Available to 3rd year students on any UCL programm"]
        falses = ["No", "no", "Not available as an option.", "This module is not available as an option.",
                  "iBSc Neuroscience, Physiology, Phys/Phar students", "Year 3 & intercalated BSc Neuroscience student",
                  "This module is not usually available as an electiv", "This module is unavailable as an elective.",
                  "This version is for Term 1 Affiliate students only",
                  "Only open to affiliate students here for Term 1 on",
                  "no (only for Psychology students)", "for Term 1 Affiliate students only",
                  "only for Term 1 Affiliate Students", "Only Term 1 Affiliates",
                  "Term 1 Affiliate students only", "for Term 1 Affiliate Students only",
                  "for Term 1/Full-Year Psychology Affiliates", "for Term 2/Full-Year Psychology Affiliates",
                  "for Term 2/Full-Year Psychology Affiliates only"]
        nones = ["This module is mandatory.", "15376", "N/A", "Only open to selected programmes (see note)",
                 "Only open to selected programmes (see notes", "Only available to particular programmes (see notes",
                 "Only open to specific programmes(see notes)", "Only open to specific programmes (see notes)"]
        if text is None:
            return None
        text = text.strip()
        if text in trues:
            return True
        elif text in falses:
            return False
        elif text in nones:
            return None
        else:
            raise NotImplementedError(text + " has no defined mapping to a boolean.")

    @staticmethod
    def boolean_to_yesno(boolean):
        if boolean is None:
            return None
        elif boolean:
            return "Yes"
        else:
            return "No"

    @property
    def text_available_affiliate(self):
        return self.boolean_to_yesno(self.available_affiliate)

    @text_available_affiliate.setter
    def text_available_affiliate(self, text):
        self.available_affiliate = self.yesno_to_boolean(text)

    @property
    def text_available_external(self):
        return self.boolean_to_yesno(self.available_external)

    @text_available_external.setter
    def text_available_external(self, text):
        self.available_external = self.yesno_to_boolean(text)

    @property
    def desc_short(self):
        """Shortens the description. If the description is over 250 chars, it will cut it down to 250,
         strip to the last space and add an ellipsis."""
        if len(self.description) >= 250:
            desc = self.description[:250]
            desc = desc.rsplit(" ", 1)[0] + "..."
            return desc
        return self.description

    @property
    def students_average(self):
        y = [x for x in [self.students_2016, self.students_2015, self.students_2014] if x]
        try:
            return (sum(y)//len(y))
        except ZeroDivisionError:
            return 0


def module_row(module_id):
    module_id = module_id.upper()
    module = Module.query.filter_by(id=module_id).first()
    if module is None:
        return None
    return module


@app.route("/")
def index():
    rows = Module.query.all()
    return render_template("index.html", modules=rows)


@app.route("/module/<module_id>")
def module_page(module_id):
    module = module_row(module_id)
    if module is None:
        return redirect(url_for(".index"))
    else:
        return render_template("module.html", module=module)


@app.route("/module/<module_id>/<goto>")
def syllabus(module_id, goto):
    module = module_row(module_id)
    if module is None:
        return redirect(url_for(".index"))
    elif goto == "timetable":
        return redirect(module.timetable_url)
    elif goto == "moodle":
        return redirect(module.moodle_url)
    elif goto == "reading-list":
        return redirect(module.readinglist_url)
    elif goto == "syllabus":
        return redirect(module.url)
    else:
        return redirect(url_for(".index"))


manager = APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(Module, exclude_columns=['_machine_url'], methods=['GET'])


@app.template_filter('htmlformat')
def html_format(string):
    if string is None:
        return None
    string = bleach.clean(string)
    string = re.sub(r"([A-Z]{4})\s*([0-9]{4})", r'<a href="/module/\1\2">\1\2</a>', string)
    string = re.sub(r"\n", r'<br/>', string)
    return Markup(string)
