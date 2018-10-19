# -*- coding: utf-8 -*-
import os
import sqlite3
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, send_from_directory
from werkzeug import secure_filename
import matplotlib.pyplot as plt

DATABASE = 'sample.db'
DEBUG = True
SECRET_KEY = 'my_precious'
USERNAME = 'admin'
PASSWORD = 'admin'

# アプリ生成
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

UPLOAD_FOLDER = 'media'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# DB周り
# DB接続
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


# DBの初期化
def init_db():
    with closing(connect_db()) as db:
        c = db.cursor()
        with app.open_resource('schema.sql') as f:
            c.executescript(f.read())
        db.commit()


# リクエストに対する前処理
@app.before_request
def before_request():
    g.db = connect_db()


# リクエストに対する後処理
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


# View
# エントリーページ
@app.route('/')
def show():
    cur = g.db.execute('select id, title, text from entries order by id asc')
    entries = [dict(id = row[0] ,title=row[1], text=row[2]) for row in cur.fetchall()]
    return render_template('show.html', entries=entries)



# エントリー追加
@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])

    g.db.commit()
    flash(u'投稿が追加されました')
    return redirect(url_for('show'))


@app.route('/delete_entry/<post_id>', methods=['POST'])
def delete_entry(post_id):
    try:
        g.db.execute('delete from entries where id= ' +post_id)
        g.db.commit()
    except Exception:
        print("erro")
    return redirect(url_for('show'))


@app.route('/edit/<post_id>',methods=['GET','POST'])
def edit(post_id):
    if request.method == 'GET':
        cur = g.db.execute('select id,title, text from entries where id=' +post_id)
        entries = [dict(id=row[0],title=row[1], text=row[2]) for row in cur.fetchall()]
        return render_template('edit.html',entries = entries,post_id = post_id)
    if request.method == 'POST':
        g.db.execute('update entries set title= ?,text= ? where id = ?',
                    ([request.form['title'], request.form['text'],post_id]))
        g.db.commit()
        return redirect(url_for('show'))



# 画像アップロード
@app.route('/image_entry', methods=['GET', 'POST'])
def image_entry():
    if request.method == 'POST':
            img_file = request.files['img_file']
            if img_file and allowed_file(img_file.filename):
                filename = secure_filename(img_file.filename)
                img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                img_url = '/uploads/' + filename
                return render_template('show.html', media=img_url)
    elif request.method == 'GET':

        return render_template('photo.html')

    else:
        return redirect(url_for('show'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ログイン
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'ユーザ名が間違っています'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'パスワードが間違っています'
        else:
            session['logged_in'] = True
            flash('ログインしました')
            return redirect(url_for('show'))
    return render_template('login.html', error=error)


# ログアウト
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('ログアウトしました')
    return redirect(url_for('show'))


if __name__ == '__main__':
    app.run()
