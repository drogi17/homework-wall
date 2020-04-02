import os
import json
import datetime
import re
import markdown2
import random

from copy import copy
from flask import Flask, request, render_template, jsonify, send_from_directory, redirect, make_response, session
from modules.sql_request import DataBase
from translation.translation import translation

def random_code():
    chars_code = [  '1','2','3','4','5','6','7','8','9','0',
                    'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
                    'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
                    '!', '%', '%', '^', '&', '*', '(', ')', ':', ';', '=', '_', '-', '$', '?']
    random.shuffle(chars_code)
    return chars_code[:9]

items = {
    'Геометрія': 1,
    'Алгебра': 2,
    'Фізика': 3,
    'Істория України': 4,
    'Всесвітня історія': 5,
    'Хімія': 6,
    'Українська мова': 7,
    'Українська література': 8,
    'Зарубіжна література': 9,
    'Інформатика': 10,
    'Громадянська осв.': 11,
    'Англійська мова': 12,
    'Географія': 13,
    'Мистецтвознавство': 14,
    'Фізична культура': 15,
    'Біологія': 16,
    

}

classes = {
    '11 A': 1,
    '11 Б': 2,
    '10 A': 3,
    '10 Б': 4,
    '9 A': 5,
    '9 Б': 6,
    '9 В': 7,
    '9 Г': 8,
    '9 Д': 9,
}

paralleles = {
    '11 паралель': 10,
    '10 паралель': 11,
    '9 паралель': 12,
}

paralleles_classes = {
    1: 10,
    2: 10, 
    3: 11,
    4: 11,
    5: 12,
    6: 12,
    7: 12,
    8: 12,
    9: 12,
}

basedir = os.path.abspath(os.path.dirname(__file__))
db = DataBase(os.path.join(basedir, 'data/data.db'))
app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'



@app.route('/updates_list', methods=['GET'])
def updates_list():
    text = '''
    __VERSION 9__ <br>
        NONE
    '''
    html_page = markdown2.markdown(text)
    return html_page

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', items=items, translation=translation)


@app.route('/LICENSE', methods=['GET'])
def LICENSE():
    return render_template('LICENSE')


@app.route('/lesson/<lesson>', methods=['GET'])
def lessons(lesson):
    if not session.get('homework_done'):
       session['homework_done'] = {}
    try:
        int(lesson)
    except ValueError:
        return redirect('/')
    if not int(lesson) in list(items.values()):
        return redirect('/')
    if session.get('class') and session.get('class') != '*' and session.get('parallel'):
        data = db.request('''   SELECT users.name, users.email, posts.value, posts.date, posts.class, posts.date_to, posts.lesson, posts.id
                                FROM posts
                                INNER JOIN users ON users.id=posts.user_id
                                WHERE lesson = ? and (posts.class = ? or posts.class = ?)
                                ORDER BY posts.id DESC;''', (lesson, session['parallel'], session['class']))
    else:
        data = db.request('''   SELECT users.name, users.email, posts.value, posts.date, posts.class, posts.date_to, posts.lesson, posts.id
                                FROM posts
                                INNER JOIN users ON users.id=posts.user_id
                                WHERE lesson = ?
                                ORDER BY posts.id DESC;''', (lesson, ))
    classes_homework_form = copy(paralleles)
    classes_homework_form.update(classes)
    return render_template('lesson.html', 
                            data=data, 
                            items=items, 
                            id_items=dict(zip(items.values(), items.keys())),
                            translation=translation, 
                            homework_done=session.get('homework_done'),
                            str=str,
                            classes=dict(zip(classes_homework_form.values(), classes_homework_form.keys())))


@app.route('/my_lessons', methods=['GET'])
def my_lessons():
    if not session.get('homework_done'):
       session['homework_done'] = {}
    if session.get('class') and session.get('class') != '*' and session.get('parallel'):
        data = db.request('''   SELECT users.name, users.email, posts.value, posts.date, posts.class, posts.date_to, posts.lesson, posts.id
                                FROM posts
                                INNER JOIN users ON users.id=posts.user_id
                                WHERE posts.class = ? or posts.class = ?
                                ORDER BY posts.id DESC;''', (session['class'], session['parallel']))
    else:
        data = db.request('''   SELECT users.name, users.email, posts.value, posts.date, posts.class, posts.date_to, posts.lesson, posts.id
                                FROM posts
                                INNER JOIN users ON users.id=posts.user_id
                                ORDER BY posts.id DESC;''')
    classes_homework_form = copy(paralleles)
    classes_homework_form.update(classes)
    return render_template('lesson.html', 
                            data=data, 
                            items=items, 
                            id_items=dict(zip(items.values(), items.keys())),
                            translation=translation, 
                            homework_done=session.get('homework_done'),
                            str=str,
                            classes=dict(zip(classes_homework_form.values(), classes_homework_form.keys())))

@app.route('/homework_form', methods=['POST', 'GET'])
def homework_form():
    if request.method == 'GET':
        classes_homework_form = copy(paralleles)
        classes_homework_form.update(classes)
        return render_template('homework_form.html', 
                                items=items, 
                                classes=classes_homework_form,
                                translation=translation)
    elif request.method == 'POST':
        code = request.form['code']
        sql = """   SELECT id, name, email
                    FROM users
                    WHERE code = ?;"""
        user = db.request(sql, (code, ))
        if not code or not user:
            classes_homework_form = copy(paralleles)
            classes_homework_form.update(classes)
            return render_template('homework_form.html', 
                                    items=items, 
                                    classes=classes_homework_form,
                                    actions=['INCORRECT CODE'],
                                    translation=translation)
        user = user[0]
        if request.form['class'] in paralleles:
            _class = paralleles.get(request.form['class'])
        else:
            _class = classes.get(request.form['class'])
        _date_to_sed = request.form['date_to_send']
        text = request.form['text'].replace('<', '&lt;').replace('>', '&gt;')
        text = markdown2.markdown(text)
        item = items.get(request.form['item'])
        sql = """   INSERT INTO posts (user_id, value, lesson, date, class, date_to)
                    VALUES (?, ?, ?, ?, ?, ?);"""
        db.request(sql, (user[0], text, item, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), _class, _date_to_sed))
        return redirect('homework_form')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'GET':
        return render_template('settings.html', 
                                items=items, 
                                classes_set=classes,
                                translation=translation)
    if request.method == 'POST':
        if request.form['class']:
            if request.form['class'] == '*':
                session['class'] = '*'
            else:
                session['class'] = classes.get(request.form['class'])
                session['parallel'] = paralleles_classes.get(session['class'])
                # print(session['parallel'])
        return render_template('settings.html', 
                                items=items, 
                                classes_set=classes, 
                                actions_ok=['SAVED'],
                                translation=translation)

@app.route('/homework_done', methods=['POST'])
def homework_done():
    if not session.get('homework_done'):
       session['homework_done'] = {}
    new_session_data = session.get('homework_done')
    new_session_data[request.json.get('id')] = request.json.get('status')
    session['homework_done'] = new_session_data
    return ''

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5001)


# @ic_it