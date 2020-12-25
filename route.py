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
from sqlalchemy.sql.schema import BLANK_SCHEMA
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import secrets
from flask import render_template, request, redirect, url_for, flash
from flask.helpers import make_response
from flask_wtf import form
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from flask_login import current_user
from wtforms import StringField, PasswordField
from wtforms.fields.simple import SubmitField
from wtforms.validators import InputRequired, Email, ValidationError
from wtforms.widgets.core import CheckboxInput
from flask_login import UserMixin
from datetime import datetime


app = Flask(__name__)
mysql = MySQL(app)
squlitedb = SQLAlchemy(app)
Login_Manager = LoginManager()
Login_Manager.init_app(app)
Login_Manager.login_view = 'login'

@Login_Manager.user_loader
def load_user(user_id):
    return UserInfo.query.get(int(user_id))

app.config['SECRET_KEY'] = 'dmvndshjvbsdvjhvjvgfuy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'user1'
app.config['MYSQL_PASSWORD'] = 'qwerty'
app.config['MYSQL_DB'] = 'cat'
app.config['TEMPLATES_AUTO_RELOAD'] = True


class LoginForm(FlaskForm):

    username = StringField('Username', validators=[InputRequired('Имя пользователя требуется.')])
    password = PasswordField('Password', validators=[InputRequired('Необходим пароль.')])

    def validate_username(self, username):
        user = UserInfo.query.filter_by(username=username.data).first()
        if not user:
            raise ValidationError('Неверное имя пользователя.')


class RegisterForm(FlaskForm):

    fullname = StringField('Полное имя', validators=[InputRequired('Полное имя требуется.')])
    username = StringField('Имя пользователя', validators=[InputRequired('Имя пользователя требуется для.')])
    password = PasswordField('пароль', validators=[InputRequired('пароль требуется для.')])
    password1 = PasswordField('Подтвердить пароль', validators=[InputRequired('Подтвердить пароль требуется для.')])
    email = StringField('Эл. адрес', validators=[InputRequired(), Email(message='Эл. адрес требуется для.')])

    def validate_username(self, username):
        user = UserInfo.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('A user is already exists with this username!!!')

    def validate_email(self, email):
        email = UserInfo.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('A user is already exists with this Email!!!')


class profileForm(FlaskForm):

    fullname = StringField('Полное имя', validators=[InputRequired('Полное имя требуется.')])
    username = StringField('Имя пользователя', validators=[InputRequired('Имя пользователя требуется для.')])
    email = StringField('Эл. адрес', validators=[InputRequired(), Email(message='Эл. адрес требуется для.')])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update Profile')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = UserInfo.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('A user is already exists with this username!!!')

    def validate_email(self, email):
        if email.data != current_user.email:
            email = UserInfo.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError('A user is already exists with this Email!!!')


class UserInfo(UserMixin, squlitedb.Model):
    id = squlitedb.Column(squlitedb.Integer, primary_key = True)
    account = squlitedb.Column(squlitedb.DateTime, nullable=False, default=datetime.utcnow)
    fullname = squlitedb.Column(squlitedb.String(200))
    username = squlitedb.Column(squlitedb.String(100), unique = True)
    password = squlitedb.Column(squlitedb.String(100))
    email = squlitedb.Column(squlitedb.String(100))
    profileImage = squlitedb.Column(squlitedb.String(20), nullable=False, default='default-profile-pic.jpeg')


    def __init__(self, username, password, email, fullname):
        self.username = username
        self.password = password
        self.email = email
        self.fullname = fullname

    def __repr__(self):
        return self.username


class userUploadForm(squlitedb.Model):
    id = squlitedb.Column(squlitedb.Integer, primary_key = True)
    date_posted = squlitedb.Column(squlitedb.DateTime, nullable=False, default=datetime.utcnow)
    author = squlitedb.Column(squlitedb.String(20), nullable=False)
    content = squlitedb.Column(squlitedb.Text, nullable=False)
    comment = squlitedb.Column(squlitedb.Text, nullable=False)

    def __repr__(self):
        return 'Posted By' + str(self.author)


@app.route('/register', methods=['GET','POST'])
def register():
    user = current_user.is_authenticated
    if user:
        return redirect(url_for('profile'))

    registerForm = RegisterForm()

    if registerForm.validate_on_submit():
        if request.form['password'] == request.form['password1']:
            hashPassword = generate_password_hash(registerForm.password.data, method='sha256')
            password = hashPassword
            NewRegister = UserInfo(fullname=registerForm.fullname.data ,username=registerForm.username.data, password=password, email=registerForm.email.data)
            squlitedb.session.add(NewRegister)
            squlitedb.session.commit()
            flash('Registration was successfull')
            return redirect(url_for('login'))
        
        else:
            flash('Password Dose not Match')
            return redirect(url_for('register'))

    else:
        return render_template('user/register.html', title='register', form=registerForm)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        user = UserInfo.query.filter_by(username = loginForm.username.data).first()
        if user and check_password_hash(user.password, loginForm.password.data):
            login_user(user)
            next_url = request.args.get("next")
            print(next_url)
            return redirect(next_url) if next_url else redirect(url_for('profile'))

        else:
            flash('Неправильный пароль.')
            return redirect(url_for('login'))

    return render_template('user/login.html', title='Login', form=loginForm)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#Image Function For Profile

def saveProfilePicture(picture):
    randomHex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(picture.filename)
    picture_fn = randomHex + f_ext
    picture_path = os.path.join(app.root_path, 'static/media/profile_picture/', picture_fn)
    picture.save(picture_path)
    return picture_fn

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    profileUpdateform = profileForm()
    if profileUpdateform.validate_on_submit():
        if profileUpdateform.picture.data:
            picture = saveProfilePicture(profileUpdateform.picture.data)
            current_user.profileImage = picture
        current_user.username = profileUpdateform.username.data
        current_user.email = profileUpdateform.email.data
        current_user.fullname = profileUpdateform.fullname.data
        squlitedb.session.commit()
        flash('Your account is updated!')
        return redirect(url_for('profile'))

    elif request.method == 'GET':
        profileUpdateform.fullname.data = current_user.fullname
        profileUpdateform.username.data = current_user.username
        profileUpdateform.email.data = current_user.email

    proImage = url_for('static', filename='media/profile_picture/'+ current_user.profileImage)
    return render_template('user/profile.html', title='profile', proImage=proImage, form=profileUpdateform)


@app.route('/upload', methods=['GET','POST'])
@login_required
def upload():
    if request.method == 'POST':
        authorUser = request.form['user']
        contentUser = request.form['content']
        commentUser = request.form['comment']
        newContentUpload = userUploadForm(author=authorUser, content=contentUser, comment=commentUser)
        squlitedb.session.add(newContentUpload)
        squlitedb.session.commit()
        flash('Your content is updated!')
        return redirect(url_for('upload'))
    
    else:
        return render_template('user/upload.html')


@app.route('/edit-content/<int:id>', methods=['GET','POST'])
@login_required
def edit(id):
    editContent = userUploadForm.query.get_or_404(id)
    if request.method == 'POST':
        authorEdit = request.form['user']
        contentEdit = request.form['content']
        commentEdit = request.form['comment']
        newEdit = userUploadForm(author=authorEdit, content=contentEdit, comment=commentEdit)
        squlitedb.session.add(newEdit)
        squlitedb.session.commit()
        flash('Your content is updated!')
        return redirect(url_for('upload'))
    return render_template('user/edit.html', edits=editContent)

@app.route('/view-content/<int:id>')
@login_required
def view(id):
    viewContent = userUploadForm.query.get_or_404(id)
    return render_template('user/view.html', views=viewContent)

@app.route('/history', methods=['GET','POST'])
@login_required
def history():
    allHistory = userUploadForm.query.order_by(userUploadForm.id).all()
    return render_template('user/history.html', histories=allHistory)

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
    if 'file' not in request.files:
        return 'Файл не был отправлен', 400
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
