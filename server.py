from flask import Flask
from flask import render_template, request, make_response, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Length
import sqlite3
from pprint import pprint
from security import Security
from routes import Route, get_coords
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
        print(field.data)
        print(usernames)
        if field.data not in usernames:
            raise ValidationError('this username is not exists')

    def validate_password(form, field):
        username = form.username.data
        if not security.check_password_by_username(field.data, username):
            raise ValidationError('username or password is wrong')


class CommentForm(FlaskForm):
    comment = TextAreaField(validators=[DataRequired(), Length(min=2, max=300)])
    submit = SubmitField("Отправить")

    def validate_comment(form, field):
        account_id = request.cookies.get('account_id')
        if account_id == '-1':
            raise ValidationError('Войдите или зарегистрируйтесь, чтобы войти в аккаунт')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

TABLE = 'data'
DYNAMIC_SOLT_TABLE = 'security_data'


def theme_master(response):
    if 'theme' not in request.cookies:
        response.set_cookie('theme', 'light', max_age=60*60*24*2)


def add_comment(con, account_id, route_id, text):
    cur = con.cursor()
    max_id = cur.execute('''SELECT MAX(id) FROM coments''').fetchone()[0]
    if max_id is None:
        new_id = 1
    else:
        new_id = max_id + 1
    cur.execute(f'INSERT INTO coments(id,text,user_id,route_id)'
                f' VALUES(?, ?, ?, ?)', (new_id, text, account_id, route_id))
    con.commit()


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
    routes_id = [i[0] for i in cur.execute('''SELECT id FROM routes WHERE creator_id=?''', (account_id,)).fetchall()]
    res = {
        'username': username,
        'email': email,
        'routes_id': routes_id
    }
    pprint(res)
    return res


def get_comments_by_route_id(con, route_id):
    cur = con.cursor()
    data = cur.execute('''SELECT text, user_id FROM coments WHERE route_id=?''', (route_id,)).fetchall()
    usernames = [cur.execute('''SELECT username FROM accounts WHERE id=?''', (i[1],)).fetchone()[0] for i in data]
    data = [
        {
            'account_name': usernames[i],
            'account_id': data[i][1],
            'text': data[i][0]
        } for i in range(len(data))
    ]
    pprint(data)
    return data


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
    created_routes = []

    for i in account_data['routes_id']:
        temp_route = Route(route_id=i)
        route_data = temp_route.get_info()
        created_routes.append(
            {
                'route_name': route_data['name'],
                'route_id': i,
                'description': route_data['description'] if len(route_data['description']) < 750
                else route_data['description'][:750]
            }
        )

    pprint(account_data['routes_id'])

    res = make_response(render_template('profile.html', title='My profile',
                                        autorization='Profile', username=account_data['username'],
                                        email=account_data['email'], created_routes=created_routes))
    theme_master(res)
    con.close()
    return res


@app.route('/Account/<user_id>')
def user_window(user_id):
    account_id = request.cookies.get('account_id')

    if account_id == user_id:
        return make_response(redirect('/Profile'))

    if not account_id or account_id == '-1':
        temp = 'Registration'
    else:
        temp = 'Profile'

    con = sqlite3.connect(f'static/sqLite3/{TABLE}.db')
    user_account_data = get_account_info(con, user_id)
    created_routes = []
    for i in user_account_data['routes_id']:
        temp_route = Route(route_id=i)
        route_data = temp_route.get_info()
        created_routes.append(
            {
                'route_name': route_data['name'],
                'route_id': i,
                'description': route_data['description'] if len(route_data['description']) < 750
                else route_data['description'][:750]
            }
        )

    res = make_response(render_template('user_profile.html', title='User profile',
                                        autorization=temp, username=user_account_data['username'],
                                        created_routes=created_routes))
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


@app.route('/Route/<route_id>', methods=['GET', 'POST'])
def route(route_id):
    form = CommentForm()

    temp_route = Route(route_id=int(route_id))
    route_data = temp_route.get_info()
    account_id = request.cookies.get('account_id')
    if not account_id or account_id == '-1':
        temp = 'Registration'
    else:
        temp = 'Profile'
    con = sqlite3.connect(f'static/sqLite3/{TABLE}.db')

    if form.validate_on_submit():
        text = form.comment.data # запрос к данным формы
        print(text)
        add_comment(con, account_id, route_id, text)

    creator_data = get_account_info(con, route_data['creator_id'])
    comments_data = get_comments_by_route_id(con, route_id)
    con.close()
    pprint(route_data['places_list'])
    res = make_response(render_template('route_window.html', title='Route',
                                        autorization=temp, route_id=route_id, route_name=route_data['name'],
                                        creator_id=route_data['creator_id'], creator_name=creator_data['username'],
                                        comments=comments_data, description=route_data['description'],
                                        places=route_data['places_list'], form=form))
    theme_master(res)
    return res


@app.route('/Log_out')
def log_out():
    res = make_response(redirect("/Registration"))
    res.set_cookie('account_id', '-1')
    return res

@app.route('/Create_Route', methods=['GET', 'POST'])
def create_route():
    account_id = request.cookies.get('account_id')
    if not account_id or account_id == '-1':
        temp = 'Register'
    else:
        temp = 'Profile'
    address_ll = request.form["address"]
    address_ll = get_coords(address_ll)
    description = request.form["route"]
    date, time = request.form["date-time"].split("T")
    date = datetime.strptime(date, "%Y-%m-%d").date()
    temp_route = Route(description.split(","), address_ll, date.weekday(), time)
    textes = []
    print(len(temp_route.names_org))
    for i in range(len(route.names_org)):
        org = temp_route.names_org[i]
        print(org[-1]["properties"]["description"])
        text = [f"{i + 1} {org[0]}",
                f"Адрес: {org[-1]["properties"]["description"]}",
                f"Время работы: {org[-1]["properties"]["CompanyMetaData"]["Hours"]["text"]}"]
        textes.append(text)
    # вот тут
    image = temp_route.create_img()
    con = sqlite3.connect("static/sqLite3/Thumbs.db")
    cur = con.cursor()
    image.save(f"static/routes_images/{new_id}.png")
    con.commit()
    con.close()
    res = make_response(render_template('create_route.html', title='Welcome', autorization=temp,
                                        image=f"static/routes_images/{new_id}.png", num=len(temp_route.names_org),
                                        textes=textes))
    return res


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
