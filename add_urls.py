"""Adds URLs to the data, based on the URL_Rules.xlsx file
"""
import re
from application import Module, db
import csv


class URLRule(object):
    """URLRule object, with method to return URL based on rule"""

    def __init__(self, info):
        self.name = info["URL_Rule"]
        self.Regex = info["Regex"]
        self.URL = info["URL"]
        self.Code_Req = info["Code_Req"]

    # Return a URL based on the substitution rules set out in the sheet
    def generate_url(self, module):
        if self.Code_Req == 'lower':
            output_string = module.lower_code
        elif self.Code_Req == 'nums':
            output_string = module.num_code
        elif self.Code_Req == 'upper':
            output_string = module.id
        elif self.Code_Req == 'thing[5]':
            output_string = module.id[4]
        else:
            output_string = ""
        return self.URL.replace("%s", output_string)


def add_urls():
    module_list = Module.query.all()

    with open("Human_URL_Rules.csv", 'r') as f:
        dr = csv.DictReader(f)
        rules = [x for x in dr]

    human_url_rules = [URLRule(x) for x in rules]

    for module in module_list:
        for rule in human_url_rules:
            # If the regex matches, make the
            m = re.match(rule.Regex, module.id)
            if m:
                module.url = rule.generate_url(module)

    with open("Machine_URL_Rules.csv", 'r') as f:
        dr = csv.DictReader(f)
        rules = [x for x in dr]

    machine_url_rules = [URLRule(x) for x in rules]

    for module in module_list:
        for rule in machine_url_rules:
            # If the regex matches, make the
            m = re.match(rule.Regex, module.id)
            if m:
                module.machine_url = rule.generate_url(module)

    db.session.commit()
