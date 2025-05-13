from flask import Flask
from flask import render_template, request, make_response, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError
import sqlite3
from pprint import pprint
from security import Security
from routes import Route
from http import cookies
from datetime import time, datetime


security = Security()

class LoginForm(FlaskForm):
    email = StringField('Адрес ел. Почты', validators=[DataRequired()])
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', [
        DataRequired(),
        EqualTo('confirm', message='Пароли должны совпадать')
    ])
    confirm = PasswordField('Повторите пароль')
    submit = SubmitField('Зарегистрироваться')

    def validate_username(form, field):
        print(52)
        con = sqlite3.connect(f'static/sqLite3/{TABLE}.db')
        cur = con.cursor()
        usernames = [i[0] for i in cur.execute('''SELECT username FROM accounts''').fetchall()]
        print(usernames)
        if field.data in usernames:
            print('fuck ebat')
            raise ValidationError('this username is already exists')
        con.close()

    def validate_email(form, field):
        con = sqlite3.connect(f'static/sqLite3/{TABLE}.db')
        cur = con.cursor()
        emails = [i[0] for i in cur.execute('''SELECT email FROM accounts''').fetchall()]
        if field.data in emails:
            raise ValidationError('this email is already exists')
        con.close()


class AutoForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', [DataRequired()])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(form, field):
        con = sqlite3.connect(f'static/sqLite3/{TABLE}.db')
        cur = con.cursor()
        usernames = [i[0] for i in cur.execute('''SELECT username FROM accounts''').fetchall()]
        con.close()
        print('tung tung tung sahur >:')
        print('tung tung tung sahur >:')
        print('tung tung tung sahur >:')
        print('tung tung tung sahur >:')
        print('tung tung tung sahur >:')
        print(field.data)
        print('tung tung tung sahur >:')
        print('tung tung tung sahur >:')
        print(usernames)
        print('tung tung tung sahur >:')
        print('tung tung tung sahur >:')
        print('tung tung tung sahur >:')
        if field.data not in usernames:
            raise ValidationError('this username is not exists')

    def validate_password(form, field):
        username = form.username.data
        if not security.check_password_by_username(field.data, username):
            raise ValidationError('username or password is wrong')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

TABLE = 'data'
DYNAMIC_SOLT_TABLE = 'security_data'


def theme_master(response):
    if 'theme' not in request.cookies:
        response.set_cookie('theme', 'light', max_age=60*60*24*2)


def new_account(con, email, username, password):
    cur = con.cursor()
    max_id = cur.execute('''SELECT MAX(id) FROM accounts''').fetchone()[0]
    if max_id is None:
        new_id = 1
    else:
        new_id = max_id + 1
    hash_data = security.generate_hash(password, new_id)
    cur.execute(f'INSERT INTO accounts(id,email,username,password_hash)'
                f' VALUES({new_id},\'{email}\',\'{username}\',\'{hash_data}\')')
    con.commit()
    return str(new_id)


def get_account_info(con, account_id):
    cur = con.cursor()
    username, email = cur.execute('''SELECT username,email FROM accounts WHERE id=?''', (account_id,)).fetchone()
    routes_id = cur.execute('''SELECT id FROM routes WHERE creator_id=?''', (account_id,)).fetchall()
    res = {
        'username': username,
        'email': email,
        'routes_id': routes_id
    }
    pprint(res)
    return res


def get_account_id(con, username):
    cur = con.cursor()
    account_id = cur.execute('''SELECT id FROM accounts WHERE username=?''', (username,)).fetchone()[0]
    return str(account_id)


@app.route('/')
@app.route('/Home')
def title():
    account_id = request.cookies.get('account_id')
    if not account_id or account_id == '-1':
        temp = 'Registration'
    else:
        temp = 'Profile'
    res = make_response(render_template('title.html', title='Welcome', autorization=temp))
    theme_master(res)
    return res

@app.route('/Info')
def get_info():
    account_id = request.cookies.get('account_id')
    if not account_id or account_id == '-1':
        temp = 'Registration'
    else:
        temp = 'Profile'
    res = make_response(render_template('information.html', title='Information', autorization=temp))
    theme_master(res)
    return res

@app.route('/Registration', methods=['GET', 'POST'])
def registration():
    con = sqlite3.connect(f'static/sqLite3/{TABLE}.db')

    form = LoginForm()
    if form.validate_on_submit():
        res = make_response(redirect("Profile"))
        res.set_cookie('account_id', new_account(con, form.email.data, form.username.data, form.password.data),
                       max_age=60 * 60 * 24 * 365 * 2)
        con.close()
        theme_master(res)
        return res

    res = make_response(render_template('registration.html', title='Registration',
                                        autorization='Registration', form=form))
    res.set_cookie('account_id', '-1', max_age=60 * 60 * 24 * 365 * 2)
    theme_master(res)
    con.close()
    return res


@app.route('/Profile')
def profile():
    account_id = request.cookies.get('account_id')
    con = sqlite3.connect(f'static/sqLite3/{TABLE}.db')
    account_data = get_account_info(con, account_id)
    res = make_response(render_template('profile.html', title='My profile',
                                        autorization='Profile', username=account_data['username'],
                                        email=account_data['email'], created_routes=account_data['routes_id']))
    theme_master(res)
    con.close()
    return res


@app.route('/Login', methods=['GET', 'POST'])
def login():
    con = sqlite3.connect(f'static/sqLite3/{TABLE}.db')

    form = AutoForm()
    if form.validate_on_submit():
        res = make_response(redirect("Profile"))
        res.set_cookie('account_id', get_account_id(con, form.username.data), max_age=60 * 60 * 24 * 365 * 2)
        con.close()
        theme_master(res)
        return res

    res = make_response(render_template('login.html', title='Login',
                                        autorization='Registration', form=form))
    res.set_cookie('account_id', '-1', max_age=60 * 60 * 24 * 365 * 2)
    theme_master(res)
    con.close()
    return res


@app.route('/Route/<route_id>')
def route(route_id):
    temp_route = Route(route_id=int(route_id))
    route_data = temp_route.get_info()
    account_id = request.cookies.get('account_id')
    if not account_id or account_id == '-1':
        temp = 'Registration'
    else:
        temp = 'Profile'
    res = make_response(render_template('route_window.html', title='Route',
                                        autorization=temp, route_id=route_id, route_name=route_data['name']))
    theme_master(res)
    return res


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
