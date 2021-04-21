from flask import Flask, render_template, request, abort, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import sqlite3
from werkzeug.utils import redirect
from werkzeug.serving import run_simple
from data.loginform import LoginForm
from data.registrform import RegisterForm
from data.records import Records
from data.news import News
from data.newsform import NewsForm
from data.users import User
from data.maps import Maps
from data import db_session
from data import records_api
from data import user_api
from data import maps_api
from data import news_api
from data import alisa

db_session.global_init("db/users.sqlite")

app = Flask(__name__)
#run_with_ngrok(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route("/")
def index():
    session = db_session.create_session()
    news = session.query(News)[::-1]
    return render_template('index.html', news=news, ln=len(news))


@app.route('/download')
def download():
    return render_template('download.html')


@app.route('/game.py', methods=['GET', 'POST'])
def download_py():
    return send_file('static/project.py')


@app.route('/game.rar', methods=['GET', 'POST'])
def download_zip():
    return send_file('static/game.rar')


@app.route('/file.exe', methods=['GET', 'POST'])
def download_file():
    return send_file('static/file.exe')


@app.route('/all_game.rar', methods=['GET', 'POST'])
def download_all():
    return send_file('static/all_game.rar')


@app.route('/downoload_map/<name>', methods=['GET', 'POST'])
def downoload_map(name):
    session = db_session.create_session()
    map = session.query(Maps).filter(Maps.name_map == name).first()
    return app.send_static_file(map.downoload_map)


@app.route('/information')
def information():
    return render_template('information.html')

@app.route('/igalery')
def igalery():
    return render_template('igalery.html')


@app.route("/textures")
def maps():
    session = db_session.create_session()
    maps = session.query(Maps)
    return render_template('textures.html', maps=maps)


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        current_user.news.append(news)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id,
                                          (News.user == current_user) |
                                          (current_user.id == 1)).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id,
                                          (News.user == current_user) |
                                          (current_user.id == 1)).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html', title='Редактирование новости', form=form)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    session = db_session.create_session()
    news = session.query(News).filter(News.id == id,
                                      (News.user == current_user) |
                                      (current_user.id == 1)).first()
    if news:
        session.delete(news)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/records')
@app.route('/records/<name>', methods=['GET', 'POST'])
def records(name=None):
    session = db_session.create_session()
    maps = session.query(Maps)
    if name:
        count = "Все рекорды на карте " + name
        records = [sorted(session.query(Records).filter(Records.map_name == name),
                          key=lambda x: x.points)[::-1]]
    else:
        count = 'Все рекорды'
        records = []
        for i in session.query(Maps):
            lst = session.query(Records)
            if lst:
                records.append(sorted(lst, key=lambda x: x.points, reverse=True)[:10])
            else:
                break
    return render_template('records.html', title='Рекорды', maps=maps,
                           records=records, count=count)


@app.route('/get_one_records', methods=['GET', 'POST'])
def get_one_records():
    records = request.form.get('records')
    session = db_session.create_session()
    maps = session.query(Maps).filter(Maps.name_map == records).first()
    url = f'/records/{maps.name_map}' if maps else '/records'
    return redirect(url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/set_rec/<int:record>/<username>/<password>/<secret_key>', methods=['GET', 'POST'])
def send_record(record, username, password, secret_key):
    record = int(record)
    score = int(record)
    selected = None
    counted_secret_key = int((score ** 5 * len(username + "12223" * len(str(len(username)))) + score ** 2) % 1234567890 + len(
        username + "123" * len(username)) % 2000001 + score ** 40 % 1234567890)
    if (str(counted_secret_key) == secret_key):
        session = db_session.create_session()
        users = session.query(User).all()
        for user in users:
            if user.email == username:
                selected = user
        if selected is not None:
            if selected.check_password(password):
                con = sqlite3.connect("db/users.sqlite")
                cur = con.cursor()
                old_record = cur.execute("SELECT id, points FROM records WHERE user_id = " + str(selected.id) + "").fetchall()
                if len(old_record) == 1:
                    cur.execute("update records set points = "+str(max(int(old_record[1]), record))+" where id = " + str(old_record[0]))
                else:
                    cur.execute("insert into records (points, user_id) values (" + str(record) + ", " + str(selected.id)+ " )")
                con.commit()
                con.close()
                return 'sent'
    return 'not sent'


@app.route('/check_user_data/<username>/<pwd>', methods=['GET', 'POST'])
def check_user_data(username, pwd):
    session = db_session.create_session()
    users = session.query(User).all()
    selected = None
    for user in users:
        if user.email == username:
            selected = user
    if selected is None:
        return "invalid username"
    else:
        if selected.check_password(pwd):
            return selected.name
        return "incorrect password"


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой адрес почты уже занят")
        if session.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такое имя уже занято")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


def main():
    app.register_blueprint(records_api.blueprint)
    app.register_blueprint(user_api.blueprint)
    app.register_blueprint(maps_api.blueprint)
    app.register_blueprint(alisa.blueprint)
    app.register_blueprint(news_api.blueprint)
    run_simple('192.168.88.254', 10000, app, use_reloader=True)


if __name__ == '__main__':
    main()
