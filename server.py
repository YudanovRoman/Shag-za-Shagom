from flask import Flask
from flask import render_template, request, make_response
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from http import cookies
from datetime import time, datetime
import scripts
import sqlite3


class LoginForm(FlaskForm):
    email = StringField('Адрес ел. Почты', validators=[DataRequired()])
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
@app.route('/Home')
def title():
    account_id = request.cookies.get('account_id')
    if not account_id or account_id == '-1':
        temp = 'Register'
    else:
        temp = 'Profile'
    res = make_response(render_template('title.html', title='Welcome', autorization=temp))
    res.set_cookie('theme', 'light', max_age=60*60*24)
    return res

@app.route('/Info')
def get_info():
    account_id = request.cookies.get('account_id')
    if not account_id or account_id == '-1':
        temp = 'Register'
    else:
        temp = 'Profile'
    return render_template('information.html', title='Information', autorization=temp)

@app.route('/Create Route Button')
def create_route_menu():
    account_id = request.cookies.get('account_id')
    if not account_id or account_id == '-1':
        temp = 'Register'
    else:
        temp = 'Profile'
    return render_template('create_route.html', title='Information', autorization=temp, image="static/img/example.png", num=0, textes=[])

@app.route('/Account', methods=['GET', 'POST'])
def register():
    account_id = request.cookies.get('account_id')
    if not account_id or account_id == '-1':
        form = LoginForm()
        if form.validate_on_submit():
            temp_id = 228
            res = make_response(render_template('profile.html', title='My profile',
                                autorization='Profile', account_id=str(temp_id)))
            res.set_cookie('account_id', '228', max_age=60 * 60 * 24 * 365 * 2)
            print(form.username)
            # тут данные на баазу
            return res
        print(0)
        res = make_response(render_template('register.html', title='Register',
                                            autorization='Register', form=form))
        res.set_cookie('account_id', '-1', max_age=60 * 60 * 24 * 365 * 2)
        return res
    else:
        pass
        res = make_response(render_template('profile.html', title='My profile',
              autorization='Profile', account_id=account_id))
        return res

@app.route('/Create_Route', methods=['GET', 'POST'])
def create_route():
    account_id = request.cookies.get('account_id')
    if not account_id or account_id == '-1':
        temp = 'Register'
    else:
        temp = 'Profile'
    address_ll = request.form["address"]
    address_ll = scripts.get_coords(address_ll)
    description = request.form["route"]
    date, time = request.form["date-time"].split("T")
    date = datetime.strptime(date, "%Y-%m-%d").date()
    route = scripts.Route(description.split(","), "Бaзовая прогулка", address_ll, date.weekday(), time)
    textes = []
    for i in range(len(route.names_org)):
        org = route.names_org[i]
        print(org)
        text = [f"{i + 1} {org[0]}",
f"Адрес: {org[-1]["properties"]["description"]}",
f"Время работы: {org[-1]["properties"]["CompanyMetaData"]["Hours"]["text"]}"]
        textes.append(text)
    print()
    image = route.create_img()
    con = sqlite3.connect("static/sqLite3/Thumbs.db")
    cur = con.cursor()
    id_sql = cur.execute("SELECT * FROM routes").fetchall()[-1][0] + 1
    image.save(f"static/routes/{id_sql}.png")
    with open(f"static/routes/{id_sql}.png", 'rb') as file:
        blob_data = file.read()
    sqlite_insert_blob_query = """INSERT INTO routes
                                      (id, creator_id, map, places_list, description) VALUES (?, ?, ?, ?, ?)"""
    # Преобразование данных в формат кортежа
    data_tuple = (id_sql, account_id, blob_data, "->".join([i[0] for i in route.names_org]), "->".join(description.split(",")))
    cur.execute(sqlite_insert_blob_query, data_tuple)
    con.commit()
    con.close()
    res = make_response(render_template('create_route.html', title='Welcome', autorization=temp, image=f"static/routes/{id_sql}.png", num=3, textes=textes))
    return res

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)