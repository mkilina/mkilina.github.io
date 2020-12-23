# -*- coding: utf-8 -*- 
from flask import *
from flask_mysqldb import MySQL
import json
import os
#from app import app
from readability import countFRE

app = Flask(__name__)
mysql = MySQL(app)


app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'user1'
app.config['MYSQL_PASSWORD'] = 'qwerty'
app.config['MYSQL_DB'] = 'cat'

app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/search',  methods=['GET', 'POST'])
def search():
    if request.method == "GET":
        return render_template('search.html', title='Search')

    else:
        details = request.form
        search_token = details['search']
        print(search_token)
        cur = mysql.connection.cursor()
        cur.execute(f'''SELECT "freq_all", freq_all, "freq1", freq1 
        from unigrams WHERE unigram = "{search_token}";''')
        row_headers = [x[0] for x in cur.description]
        rv = cur.fetchall()
        json_data = []
        for result in rv:
            json_data.append(dict(zip(row_headers, result)))
        return render_template('db_response.html', response=json.dumps(json_data), token=search_token)

@app.route('/search_morph')
def search_morph():
    return render_template('search_morph.html', title='Search_morph')

@app.route('/base')
def base():
    return render_template('base.html', title='Base')

@app.route('/collocations')
def collocations():
    return render_template('collocations.html', title='Collocations')

@app.route('/check')
def academicity():
    return render_template('check.html', title='Academicity')

@app.route('/analysis')
def analysis():
    filename = os.listdir("student_texts")[0]
    FRE = round(countFRE('student_texts/{0}'.format(filename)), 2)

    labels = ['ECON', 'JUR', 'LING', 'PSYCH', 'HIST', 'SOC', 'YOU']
    values = [76.6, 87.03, 82.17, 78.13, 91.11, 77.95, FRE]
    colors = ['rgba(151,187,205,0.2)', "rgba(151,187,205,0.2)", "rgba(151,187,205,0.2)", "rgba(151,187,205,0.2)", "rgba(151,187,205,0.2)", "rgba(151,187,205,0.2)", "rgba(221,125,173,0.2)"]

    return render_template('analysis.html', title='Analysis', filename=filename, FRE=FRE, max=110, labels=labels, values=values, colors=colors)

@app.route('/main')
def main():
    return render_template('main.html', title='About us')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)