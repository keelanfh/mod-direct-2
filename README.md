# mod-direct-2


Setup required:

1. run `export FLASK_APP=application.py`
2. run `flask run`
3. Flask is now running at given address

To add the data to the database:

`from application import *`

`import_from_running_list()`

Run `add_urls.py`

Run `download_html.py` if necessary

Run `parser.py`

## Search terms

`module = Module.query.filter_by(id=module_id).first()`

`modules = Module.query.all()`

## Useful things you can do

`df = pandas.read_sql('modules', 'sqlite:///modules.db')`