# -*- coding: utf-8 -*- 
from flask import *
from flask_mysqldb import MySQL
import json
import os
from file_manager import *
import spelling
import constants
#from app import app
from readability import countFRE, uniqueWords

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

@app.route('/render_upload_file', methods=['GET'])
def render_upload_file():
    return render_template('upload_and_spellcheck.html')

@app.route('/upload_file', methods=['POST'])
def upload_file():
    file = request.files['file']
    file_id = save_file_first_time_and_get_id(file)
    if not is_encoding_supported(file_id):
        return 'Сохраните файл в кодировке utf-8', 400
    elif not are_paragraphs_correct(file_id):
        return 'Разделите длинные абзацы на несколько', 400
    else:
        return jsonify({'file_id': file_id})

@app.route('/get_spelling_problems/<file_id>', methods=['GET'])
def get_spelling_data(file_id):
    text = get_last_version(file_id)
    spellchecker = spelling.SpellChecker()
    problems = spellchecker.check_spelling(text)['problems']
    return jsonify({'spelling_problems': problems})

@app.route('/correct_spelling', methods=['POST'])
def correct_spelling():
    file_id = request.json['file_id']
    text = get_last_version(file_id)
    user_corrections = request.json['problems_with_corrections']
    corrected_text = spelling.make_changes(text, user_corrections)
    save_next_version(corrected_text, file_id)
    return jsonify({'success':True})

@app.route('/possible_aspects', methods=['GET'])
def possible_aspects():
    ##Переписать функцию, если будут аспекты, которые доступны не всегда
    return jsonify({'possible_aspects': constants.ASPECTS})

@app.route('/get_statistics/<file_id>', methods=['GET'])
def get_statistics(file_id):
    text = get_last_version(file_id)
    readability_score = countFRE(text)
    total, unique = uniqueWords(text)
    return jsonify({'readability_score': readability_score, 
                    'total_words': total,
                    'unique_words': unique})

@app.route('/send_last_version/<file_id>', methods=['GET'])
def send_last_version(file_id):
    text = get_last_version(file_id)
    return jsonify({'text': text})

@app.route('/save_edited_text', methods=['POST'])
def save_edited_text():
    data = request.get_json()
    print('/save_edited_text request_data.file_id:')
    print(data['file_id'])
    text = data['text']
    file_id = data['file_id']
    save_next_version(text, file_id)
    return jsonify({'success':True})

@app.route('/aspects_checking', methods=['POST']) 
def aspects_checking():
    data = request.get_json()
    print('/aspects_checking request_data:')
    print(data)
    file_id = data['file_id'] 
    text = get_last_version(file_id)  
    chosen_aspects = data['chosen_aspects']
    print(chosen_aspects)
    problems = {}
    for chosen_aspect in chosen_aspects:
        checking_function = constants.ASPECT2FUNCTION[chosen_aspect]
        problems[chosen_aspect] = checking_function(text)
    print('problems:', problems)
    return jsonify({'problems':problems, 'text': text})

@app.route('/analysis')
def analysis():
    return render_template('analysis.html', title='Analysis')

@app.route('/main')
def main():
    return render_template('main.html', title='About us')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)