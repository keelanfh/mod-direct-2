"""Download the HTML files
"""

import urllib
from application import Module
import os

modules = Module.querdatay.all()
# TODO prevent this from asking for duplicates
urls = [{"code": module.id, "url": module.machine_url} for module in modules if module.dept_code == "GEOG"]

headers = {'Content-Type': 'application/x-www-form-urlencoded'}
results = []


# Save all the results into files.

def html_output_file(module_code):
    return os.path.join(os.curdir, 'data', 'syllabus_html', module_code + '.html')


for url in urls:
    urllib.urlretrieve(url["url"], html_output_file(url["code"]))
    break
