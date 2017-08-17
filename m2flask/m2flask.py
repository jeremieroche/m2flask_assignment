import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash,make_response
import time
from datetime import datetime

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'm2flask.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/report')
def show_entries():
    db = get_db()
    cur = db.execute('select delay,time,client_ip,id,user_agent from entries order by id desc')
    entries = cur.fetchall()


    db = get_db()
    cur = db.execute('SELECT count FROM download_summary ORDER BY id DESC')
    download_summary = cur.fetchall()[0]
    return render_template('report.html', entries=entries,download_summary=download_summary)

@app.route('/add', methods=['POST'])
def add_entry():
    # if not session.get('logged_in'):
    #     abort(401)
    db = get_db()

    time_delay = int(request.form['delay'])


    time.sleep(time_delay)
    timestamp = datetime.now()

    client_ip = request.remote_addr

    user_agent = request.headers.get('User-Agent')


    db.execute('insert into entries (delay,time,client_ip,user_agent) values (?,?,?,?)',
                 [request.form['delay'],timestamp,client_ip,user_agent])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('csv_test'))


@app.route('/csv_test')
def csv_test():
    return render_template('csv_test.html')


@app.route('/csv')
def download_csv():

    db = get_db()
    cur = db.execute('SELECT file_name FROM download_summary ORDER BY id DESC')
    download_summary = cur.fetchall()[0]

    with open(download_summary['file_name']) as fp:
        csv = fp.read()


    db.execute("UPDATE download_summary SET count = count + 1 WHERE id = 1")
    db.commit()

    response = make_response(csv)
    cd = 'attachment; filename=mycsv.csv'
    response.headers['Content-Disposition'] = cd
    response.mimetype='text/csv'

    return response



@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run(threaded=True)
