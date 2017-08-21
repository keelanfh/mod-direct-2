"""Adds URLs to the data, based on the URL_Rules.xlsx file
"""
import pandas
import re
from application import Module, db


class URLRule(object):
    """URLRule object, with method to return URL based on rule"""

    def __init__(self, info):
        self.name = info.URL_Rule
        self.Regex = info.Regex
        self.URL = info.URL
        self.Code_Req = info.Code_Req

    # Return a URL based on the substitution rules set out in the sheet
    def generate_url(self, module):
        if self.Code_Req == 'lower':
            output_string = module.lower_code
        elif self.Code_Req == 'nums':
            output_string = module.num_code
        elif self.Code_Req == 'upper':
            output_string = module.id
        elif self.Code_Req == 'thing[5]':
            output_string = module.id[5]
        else:
            output_string = ""
        return self.URL.replace("%s", output_string)


module_list = Module.query.all()

human_url_rules = [URLRule(x) for x in pandas.read_excel('URL_Rules.xlsx', 'Human').itertuples()]

for module in module_list:
    for rule in human_url_rules:
        # If the regex matches, make the
        m = re.match(rule.Regex, module.id)
        if m:
            module.url = rule.generate_url(module)

machine_url_rules = [URLRule(x) for x in pandas.read_excel('URL_Rules.xlsx', 'Machine').itertuples()]

for module in module_list:
    for rule in machine_url_rules:
        # If the regex matches, make the
        m = re.match(rule.Regex, module.id)
        if m:
            module.machine_url = rule.generate_url(module)

db.session.commit()
