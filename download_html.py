"""Download the HTML files
"""

import urllib
from application import Module
import os

modules = Module.query.all()
files_already = os.listdir(os.path.join("data", "syllabus_html"))

query_departments = ["PSYC", "ANAT", "BIOC", "BIOL", "BIOS", "CELL", "NEUR", "PHAR", "PHOL", "PALS", "PHAY", "ARCL"]

# TODO prevent this from asking for duplicates
urls = [{"code": module.id, "url": module.machine_url} for module in modules if
        module.dept_code in query_departments and module.machine_url is not None]

# Save all the results into files.


def html_output_file(module_code):
    return os.path.join(os.curdir, 'data', 'syllabus_html', module_code + '.html')


for url in urls:
    if url['code'] + '.html' not in files_already:
        print url
        urllib.urlretrieve(url["url"], html_output_file(url["code"]))
