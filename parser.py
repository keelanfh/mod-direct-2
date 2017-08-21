"""Program to parse web pages/PDFs/etc
Currently modifies the module list for that module, saves back to modules.json
"""
from scrapy.selector import Selector
# from pdfextract import convert_pdf_to_txt
# from collections import deque
import os
from application import Module, db


class ParseError(Exception):
    pass


def html_output_file(module_code):
    return os.path.join(os.curdir, 'data', 'syllabus_html', module_code + '.html')


# Function to parse the page for a given module
def parse(module_id):
    # TODO sort this out, it's messy. Might require object creation or something.
    if module_id[:4] == 'GEOG':

        module = Module.query.filter_by(id=module_id).first()

        output_dict = {}
        with open(html_output_file(module_id), 'r') as f:
            text = f.read()
            s = Selector(text=text)

            # Select all the paragraphs
            paragraphs = s.xpath('//p')
            for para in paragraphs:
                try:
                    # Deal with cases where an error is returned
                    if para.xpath('b/text()').extract()[0][:5] == "Sorry":
                        # TODO re-implement this later
                        # module_list.loc[module_id, "url_parsed"] = False
                        return
                    # There should only be one text element in each bold element.
                    assert len(para.xpath('b/text()').extract()) <= 1
                    # Key should be the first element in there.
                    key = para.xpath('b/text()').extract()[0]
                    # Remove all extraneous rubbish, just put newlines between the text.
                    value = "\n\n".join([x.strip() for x in para.xpath('text()').extract() if x.strip() != ""])
                    # Set the value back in the DF
                    output_dict[key] = value
                # Can't remember what this error was to deal with
                except IndexError:
                    pass
                except AssertionError:
                    print para.xpath('b/text()').extract()
                    raise AssertionError()
            module.url_parsed = True

    else:
        return

    # if module_id[:4] == "MATH":
    #     text = convert_pdf_to_txt(pdf_output_file(module_id))
    #     text = text.split("\n")
    #     assert text[0][:4] == module_id[4:]
    #     print text
    #
    #     keys = deque()
    #     results = {}
    #     for line in text[1:]:
    #         if line[-1:] == ":":
    #             keys.append(line[:-1])
    #             # print line, "appended"
    #
    #         elif len(keys) != 0 and ":" not in line and line.strip() != "":
    #             # print keys
    #             # print line
    #             key = keys.popleft()
    #             results[key] = line
    #
    #         elif len(keys) == 0 and ":" not in line and line.strip() != "":
    #             print key, line
    #
    #     print results

    keymap = {"Available to Affilitate Students": "text_available_affiliate",
              "Available to External Students": "text_available_external",
              "Brief Course Description": "description",
              "Course Aims": "aims",
              "Course Content": "content",
              "Course Website": "course_website",
              "Financial contributions": "financial_contribs",
              "Form of Assessment": "assessment_method",
              "Method of Teaching": "teaching_method",
              "People": "people",
              "Pre-requisites": "prereqs",
              "Reading": "reading",
              "Programme Term Running": "term",
              "Programme Year Running": "programme_year",
              "Unit Value": None,
              "Academic Year": None
              }

    if "Course Aims" in output_dict and "Learning Outcomes" in output_dict:
        output_dict["Course Aims"] = "\n".join([output_dict["Learning Outcomes"]])
        del output_dict["Learning Outcomes"]

    for k in output_dict.keys():
        try:
            if keymap[k] is not None:
                setattr(module, keymap[k], output_dict[k])
            del output_dict[k]
        except KeyError:
            raise ParseError("Behaviour not defined for key " + k)
    try:
        assert output_dict == {}
    except AssertionError:
        raise ParseError("Behaviour not defined for keys ", output_dict.keys())


for x in os.listdir('data/syllabus_html'):
    parse(x.split('.')[0])

db.session.commit()
