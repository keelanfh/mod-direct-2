import os
import urllib.error
import urllib.request

import pandas
from scrapy.selector import Selector

from add_urls import add_urls
from application import *
from parser import parse_all


def import_from_running_list():
    # Open excel file with the list of modules
    module_list = pandas.read_excel('data/running_list.xlsx')

    # Create a Module object containing this information, then output to dict
    for x in module_list.itertuples():
        module = Module(code=x.Code, title=x.Title, level=x.Level, value=x.Value)
        db.session.add(module)
    db.session.commit()


def download_html():
    modules = Module.query.all()

    if "syllabus_html" not in os.listdir("data"):
        os.mkdir(os.path.join("data", "syllabus_html"))

    files_already = os.listdir(os.path.join("data", "syllabus_html"))

    query_departments = ["PSYC", "ANAT", "BIOC", "BIOL", "BIOS", "CELL", "NEUR", "PHAR", "PHOL", "PALS", "PHAY", "ARCL"]

    # TODO prevent this from asking for duplicates (not an issue with current departments)
    urls = [{"code": module.id, "url": module.machine_url} for module in modules if
            module.dept_code in query_departments and module.machine_url is not None]

    # Save all the results into files.

    def html_output_file(module_code):
        return os.path.join(os.curdir, 'data', 'syllabus_html', module_code + '.html')

    for url in urls:
        if url['code'] + '.html' not in files_already:
            print(url)
            try:
                urllib.request.urlretrieve(url["url"], html_output_file(url["code"]))
            except urllib.error.HTTPError:
                pass

def add_examboard_data():
    socsci = os.path.join("data", "boe_sci.htm")
    natsci = os.path.join("data", "boe_natsci.htm")

    for x in [socsci, natsci]:
        with open(x) as f:
            text = f.read()
            s = Selector(text=text)

        rows = s.xpath("//ol/ol/table/tbody/tr")
        for row in rows:
            cells = row.xpath("td")
            rowtext = [x.xpath("text()").extract()[0] if x.xpath("text()").extract() else "0" for x in cells]
            if rowtext:
                if re.match(r"[A-Z]{4}[0-9]{4}", rowtext[0]):
                    print(rowtext)
                    module = Module.query.filter_by(id=rowtext[0]).first()
                    if module:
                        module.students_2016 = rowtext[2]
                        module.students_2015 = rowtext[3]
                        module.students_2014 = rowtext[4]

    db.session.commit()


if __name__ == "__main__":
    # Create database
    db.create_all()

    # Populate database
    import_from_running_list()
    add_examboard_data()

    # Add data from web scraping
    add_urls()
    download_html()
    parse_all()
    download_html()
