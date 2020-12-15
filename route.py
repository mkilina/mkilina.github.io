# -*- coding: utf-8 -*- 
from flask import *
#from app import app

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/search')
def search():
    return render_template('search.html', title='Search')

@app.route('/search_morph')
def search_morph():
    return render_template('search_morph.html', title='Search')

@app.route('/collocations')
def collocations():
    return render_template('collocations.html', title='Collocations')

@app.route('/check')
def academicity():
    return render_template('check.html', title='Academicity')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html', title='Analysis')

@app.route('/main')
def main():
    return render_template('main.html', title='About us')

if __name__ == '__main__':
    app.run(debug=True)