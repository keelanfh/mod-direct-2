"""Program to parse web pages/PDFs/etc
Currently modifies the module list for that module, saves back to modules.json
"""
# from pdfextract import convert_pdf_to_txt
# from collections import deque
import os
import re

from scrapy.selector import Selector

from application import Module, db


class ParseError(Exception):
    pass


def html_output_file(module_code):
    return os.path.join(os.curdir, 'data', 'syllabus_html', module_code + '.html')


# Function to parse the page for a given module
def parse(module_id):
    module = Module.query.filter_by(id=module_id).first()
    output_dict = {}

    # TODO sort this out, it's messy. Might require object creation or something.
    if module.dept_code == 'GEOG':
        # TODO remove this

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
                    print(para.xpath('b/text()').extract())
                    raise AssertionError()
            module.url_parsed = True

    elif module.dept_code in ["PSYC", "ANAT", "BIOC", "BIOL", "BIOS", "CELL", "NEUR", "PHAR", "PHOL", "PALS", "PHAY"]:

        with open(html_output_file(module_id), 'r') as f:
            text = f.read()
            s = Selector(text=text)

        paragraphs = s.xpath('//tr')
        for para in paragraphs:
            print(para.xpath('.//text()').extract())
            extracted = para.xpath('.//text()').extract()
            if len(extracted) == 2:
                output_dict[extracted[0].replace(":", "")] = extracted[1]

    elif module.dept_code == "ARCL":

        with open(html_output_file(module_id), 'r') as f:
            text = f.read()
            s = Selector(text=text)

        description = s.xpath('//div[@id="col3"]//p//text()').extract()
        print(description)
        description = re.sub(r"\s+", r" ", description[0].strip())
        print(description)
        output_dict["Brief Course Description"] = description

    elif module.dept_code == "BASC":
        # Potentially this might need fixing - not sure if this is true for all of these...

        with open(html_output_file(module_id), 'r') as f:
            text = f.read()
            s = Selector(text=text)

        description = "\n".join([x.replace("\n", " ") for x in s.xpath('//*[@id="tab-1"]/div/p/text()').extract()])
        print(description)
        module.description = description
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

    # TODO move this off into a CSV

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
              "Module organiser (provisional)": "people",
              "Module assessment": "assessment_method",
              "Taking this module as an option?": "text_available_external",
              "Module prerequisites": "prereqs",
              "Module outline": "description",
              "Module aims": "aims",
              "Notes": "notes",

              # The following information is already available from the Running List/elsewhere
              "Unit Value": None,
              "Academic Year": None,
              "Module code": None,
              "Title": None,
              "Credit value": None,
              "Module timetable": None,

              # The following information is not currently being used
              "Division": None,
              "Organiser's location": None,

              # Will probably pull this from UCL API
              "Organiser's email": None,
              "Available for students in Year(s)": None,

              # The following should probably be integrated somehow
              "Module objectives": None,
              "Key skills provided by module": None,
              "Last updated": None,

              # Substitute for Moodle link? Would require a little database refactoring
              "Link to virtual learning environment (registered students only)": None
              }

    if "Course Aims" in output_dict and "Learning Outcomes" in output_dict:
        output_dict["Course Aims"] = "\n".join([output_dict["Learning Outcomes"]])
        del output_dict["Learning Outcomes"]

    for k, v in output_dict.items():
        try:
            if keymap[k] is not None:
                if output_dict[k].strip() == "":
                    setattr(module, keymap[k], None)
                else:
                    setattr(module, keymap[k], output_dict[k])
        except KeyError:
            raise ParseError("Behaviour not defined for key " + k)


def parse_all():
    for x in os.listdir('data/syllabus_html'):
        parse(x.split('.')[0])

    db.session.commit()


#
# if __name__ == "__main__":
#     parse_all()

parse("BASC1001")
db.session.commit()
