from flask import Flask
from flask import render_template, request, make_response
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from http import cookies
from datetime import time, datetime
import scripts


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
    res = make_response(render_template('title.html', title='Welcome', autorization=temp, image="static/img/example.png"))
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
    address_ll = scripts.get_coords("Россия Липецк Свиридова 5")
    route = scripts.Route(["Кинотеатр", "Кафе", "Парк"], "БАзовая прогулка", address_ll)
    image = route.create_img()
    res = make_response(render_template('title.html', title='Welcome', autorization=temp, image=image))
    return res

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)