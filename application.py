import re

import bleach
from flask import Flask, render_template, Markup, url_for, redirect
from flask.ext.restless import APIManager
from flask_sqlalchemy import SQLAlchemy

from models import Module

app = Flask(__name__)

# Flask-SQLAlchemy
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///modules.db"
app.config["SQLALCHEMY_ECHO"] = True

db = SQLAlchemy(app)


def module_row(module_id):
    module_id = module_id.upper()
    module = Module.query.filter_by(id=module_id).first()
    if module is None:
        return None
    return module


@app.route("/")
def index():
    modules = Module.query.all()
    return render_template("index.html", modules=modules)


@app.route("/module/<module_id>")
def module_page(module_id):
    module = module_row(module_id)
    if module is None:
        return redirect(url_for(".index"))
    else:
        return render_template("module.html", module=module)


@app.route("/module/<module_id>/<goto>")
def syllabus(module_id, goto):
    fields = {"timetable": "timetable_url", "moodle": "moodle_url", "reading-list": "readinglist_url",
              "syllabus": "url"}
    module = module_row(module_id)
    if module is None:
        return redirect(url_for(".index"))
    else:
        try:
            if getattr(module, fields[goto]) is not None:
                return redirect(getattr(module, fields[goto]))
        except KeyError:
            return redirect(url_for(".index"))
        return redirect(url_for(".index"))


manager = APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(Module, exclude_columns=['_machine_url'], methods=['GET'])


@app.template_filter('htmlformat')
def html_format(string):
    if string is None:
        return None
    string = bleach.clean(string)
    string = re.sub(r"([A-Z]{4})(?:\s|[1246])*([GM0-9][0-9]{2}[MP0-9](?:\b|[ABCIW]))",
                    r'<a href="/module/\1\2">\1\2</a>', string)
    string = re.sub(r"\n", r'<br/>', string)
    return Markup(string)
