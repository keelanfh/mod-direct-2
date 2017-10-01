from scrapy.selector import Selector
import os, re
from application import Module, db

socsci = os.path.join("data", "boe_sci.htm")
natsci = os.path.join("data", "boe_natsci.htm")

for x in [socsci, natsci]:
    with open(x) as f:
        text = f.read()
        s = Selector(text=text)

    rows = s.xpath("//ol/ol/table/tbody/tr")
    for row in rows:
        cells = row.xpath("td")
        rowtext = [x.xpath("text()").extract()[0] if x.xpath("text()").extract() else u"0" for x in cells]
        if rowtext:
            if re.match(r"[A-Z]{4}[0-9]{4}", rowtext[0]):
                print rowtext
                module = Module.query.filter_by(id=rowtext[0]).first()
                if module:
                    module.students_2016 = rowtext[2]
                    module.students_2015 = rowtext[3]
                    module.students_2014 = rowtext[4]

db.session.commit()