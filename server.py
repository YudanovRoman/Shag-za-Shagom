from flask import Flask
from flask import render_template, request, make_response
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError
import sqlite3
from pprint import pprint
from security import generate_hash, check_password_by_username
from http import cookies
from datetime import time, datetime


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
        usernames = cur.execute('''SELECT username FROM accounts''').fetchall()
        print(field.data)
        if field.data in usernames:
            print('fuck ebat')
            raise ValidationError('this username is already exists')
        con.close()

    def validate_email(form, field):
        con = sqlite3.connect(f'static/sqLite3/{TABLE}.db')
        cur = con.cursor()
        emails = cur.execute('''SELECT email FROM accounts''').fetchall()
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
        usernames = cur.execute('''SELECT username FROM accounts''').fetchall()
        con.close()
        if field.data not in usernames:
            raise ValidationError('this username is not exists')

    def validate_password(form, field):
        username = form.username.data
        if not check_password_by_username(field.data, username):
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
    hash_data = generate_hash(password, new_id)
    cur.execute(f'INSERT INTO accounts(email,username,password_hash)'
                f' VALUES(\'{email}\',\'{username}\',\'{hash_data}\')')
    con.commit()
    return str(new_id)


def answer_format(ans: str):
    res = ans[ans.rfind('=') + 1:ans.rfind('"') + 1]
    return res


def get_account_info(con, account_id):
    print(account_id)
    cur = con.cursor()
    username, email = cur.execute('''SELECT username,email FROM accounts WHERE id=?''', account_id).fetchone()
    routes_id = cur.execute('''SELECT id FROM routes WHERE creator_id=?''', account_id).fetchall()
    res = {
        'username': username,
        'email': email,
        'routes_id': routes_id
    }
    pprint(res)
    return res


@app.route('/')
@app.route('/Home')
def title():
    account_id = request.cookies.get('account_id')
    if not account_id or account_id == '-1':
        temp = 'Register'
    else:
        temp = 'Profile'
    res = make_response(render_template('title.html', title='Welcome', autorization=temp))
    theme_master(res)
    return res

@app.route('/Info')
def get_info():
    account_id = request.cookies.get('account_id')
    if not account_id or account_id == '-1':
        temp = 'Register'
    else:
        temp = 'Profile'
    res = make_response(render_template('information.html', title='Information', autorization=temp))
    theme_master(res)
    return res

@app.route('/Account', methods=['GET', 'POST'])
def register():
    account_id = request.cookies.get('account_id')
    con = sqlite3.connect(f'static/sqLite3/{TABLE}.db')

    if not account_id or account_id == '-1':
        form = LoginForm()
        if form.validate_on_submit():
            res = make_response(render_template('profile.html',
                                                title='My profile', autorization='Profile',
                                                email=form.email, username=form.username))
            res.set_cookie('account_id', new_account(con, form.email.data, form.username.data, form.password.data),
                           max_age=60 * 60 * 24 * 365 * 2)
            print(form.username)
            con.close()
            theme_master(res)
            return res
        print(0)
        res = make_response(render_template('register.html', title='Register',
                                            autorization='Register', form=form))
        res.set_cookie('account_id', '-1', max_age=60 * 60 * 24 * 365 * 2)
        theme_master(res)
        con.close()
        return res
    else:
        account_data = get_account_info(con, account_id)
        res = make_response(render_template('profile.html', title='My profile',
                                            autorization='Profile', username=account_data['username'],
                                            email=account_data['email'], created_routes=account_data['routes_id']))
        theme_master(res)
        con.close()
        return res

@app.route('/Route/<route_id>')
def route(route_id):
    pass


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)