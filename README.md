# Module Directory

Setup required:

Required files: `running_list.xlsx`, `boe_natsci.htm` and `boe_sci.htm`

Run `setup.py`

## Start Flask Webserver

1. `export FLASK_APP=application.py`
2. `flask run`

## Search terms

`module = Module.query.filter_by(id=module_id).first()`

`modules = Module.query.all()`

## Useful things you can do

`df = pandas.read_sql('modules', 'sqlite:///modules.db')`