"""People Search Engine"""

import os
import sqlite3
import json
import re
from flask import Flask, render_template, request
from forms import PeopleSearchForm

SECRET_KEY = os.urandom(32)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

PATH = "/home/afnan/PeopleSearchApp/SearchApp/"


@app.route('/')
def index():
    """Search Form Function"""
    form = PeopleSearchForm()
    return render_template('search.html', form=form)


@app.route('/search', methods=['GET', 'POST'])
def search_route():
    """Search App Route Function"""
    if request.method == 'POST':
        search = request.form["search"]
        if "'" in search:
            search = search.replace("'", " ")
        search = re.sub('[@_!#$%^&*()<>?/\|}{~:]', ' ', search)
        result = search_table(search)
        return render_template("result.html", result=result)
    else:
        return render_template("result.html", result=None)


@app.route('/createtable')
def create_table_route():
    """Create Table Route Function"""
    result = create_table()
    return render_template("display.html", result=result)


@app.route('/inserttable')
def insert_table_route():
    """Insert Table Route Function"""
    result = insert_table()
    return render_template("display.html", result=result)


def connect_db():
    """Connect to Sqlite Database"""
    data_base = sqlite3.connect(PATH + "people.sqlite")
    return data_base


def search_table(keyword):
    """Search People Function"""
    data_base = connect_db()
    cursor_fn = data_base.cursor()
    query = 'SELECT * FROM people WHERE people MATCH \"{}\"'.format(keyword)
    cursor_fn.execute(query)
    rows = cursor_fn.fetchall()
    result_row = []
    for row in rows:
        result_row.append(row)
    return result_row


def create_table():
    """Create People Table Function"""
    data_base = connect_db()
    data_base.execute('''CREATE VIRTUAL TABLE people using FTS5
            (name UNINDEXED,
            intro UNINDEXED,
            location UNINDEXED,
            job,
            about UNINDEXED,
            education,
            skills,
            url UNINDEXED)''')
    return "Table Created"


def insert_table():
    """Insert Data into People Table Function"""
    data_base = connect_db()
    cursor_fn = data_base.cursor()
    json_data = get_json_from_file()
    for data in json_data:
        data_keys = ','.join(data.keys())
        question_marks = ','.join(list('?'*len(data)))
        vals = tuple(data.values())
        query = "insert into people ({0}) values ({1})".format(data_keys, question_marks)
        cursor_fn.execute(query, vals)
        data_base.commit()
    return "Table Inserted"


def get_json_from_file():
    """Read Json from file Function"""
    json_file = open(PATH + 'people.json',)
    data = json.load(json_file)
    json_file.close()
    return data


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
