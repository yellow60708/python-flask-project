from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DB_path = r"C:\Users\user\Desktop\fast2\example.db"


# =========================
# Database 初始化
# =========================
def init_db():
    conn = sqlite3.connect(DB_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shoesjohn (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phonenumber TEXT NOT NULL,
            shoe_count INTEGER NOT NULL DEFAULT 0,
            item TEXT NOT NULL,
            fee REAL NOT NULL,
            paid REAL NOT NULL DEFAULT 0,
            is_blacklist INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'pending'
        )
    """)

    conn.commit()
    conn.close()


# =========================
# SQL Logic Functions
# =========================

def get_users(cursor, keyword=None):

    if keyword:
        cursor.execute("""
            SELECT id, name, phonenumber, shoe_count,
                   item, fee, paid,
                   (fee - paid) AS debt,
                   is_blacklist,
                   status
            FROM shoesjohn
            WHERE name LIKE ? OR phonenumber LIKE ?
        """, (f"%{keyword}%", f"%{keyword}%"))

    else:
        cursor.execute("""
            SELECT id, name, phonenumber, shoe_count,
                   item, fee, paid,
                   (fee - paid) AS debt,
                   is_blacklist,
                   status
            FROM shoesjohn
        """)

    return cursor.fetchall()


def add_user(cursor, name, phonenumber, shoe_count, item, fee, paid):

    cursor.execute("""
        INSERT INTO shoesjohn
        (name, phonenumber, shoe_count, item, fee, paid, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending')
    """, (name, phonenumber, shoe_count, item, fee, paid))


def update_user(cursor, id, name, phonenumber,
                shoe_count, item, fee, paid, status):

    cursor.execute("""
        UPDATE shoesjohn
        SET name=?, phonenumber=?, shoe_count=?,
            item=?, fee=?, paid=?, status=?
        WHERE id=?
    """, (name, phonenumber, shoe_count,
          item, fee, paid, status, id))


def delete_user(cursor, id):

    cursor.execute("DELETE FROM shoesjohn WHERE id=?", (id,))


# =========================
# Routes
# =========================

@app.route('/')
def index():

    conn = sqlite3.connect(DB_path)
    cursor = conn.cursor()

    users = get_users(cursor)
    recent_users = sorted(users, key=lambda x: x[0], reverse=True)[:5]

    conn.close()

    return render_template('index.html', users=recent_users)


@app.route('/search')
def search_page():

    keyword = request.args.get('keyword')

    conn = sqlite3.connect(DB_path)
    cursor = conn.cursor()

    users = get_users(cursor, keyword)

    conn.close()

    return render_template('search.html', users=users)


@app.route('/add_user', methods=['POST'])
def add_user_route():

    lastname = request.form['lastname']
    title = request.form['title']

    name = lastname + title

    phonenumber = request.form['phonenumber']
    shoe_count = request.form['shoe_count']
    item = request.form['item']
    fee = request.form['fee']
    paid = request.form['paid']

    conn = sqlite3.connect(DB_path)
    cursor = conn.cursor()

    add_user(cursor, name, phonenumber, shoe_count,
             item, fee, paid)

    conn.commit()
    conn.close()

    return redirect(url_for('index'))


@app.route('/update_user/<int:id>', methods=['GET', 'POST'])
def update_user_route(id):

    conn = sqlite3.connect(DB_path)
    cursor = conn.cursor()

    if request.method == 'POST':

        name = request.form['name']
        phonenumber = request.form['phonenumber']
        shoe_count = request.form['shoe_count']
        item = request.form['item']
        fee = request.form['fee']
        paid = request.form['paid']

        status = request.form.get('status', 'pending')

        update_user(cursor, id, name, phonenumber,
                    shoe_count, item, fee, paid, status)

        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM shoesjohn WHERE id=?", (id,))
    user = cursor.fetchone()

    conn.close()

    return render_template('update_user.html', user=user)


@app.route('/delete_user/<int:id>')
def delete_user_route(id):

    conn = sqlite3.connect(DB_path)
    cursor = conn.cursor()

    delete_user(cursor, id)

    conn.commit()
    conn.close()

    return redirect(url_for('index'))


@app.route('/toggle_blacklist/<int:id>')
def toggle_blacklist(id):

    conn = sqlite3.connect(DB_path)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE shoesjohn
        SET is_blacklist = CASE
            WHEN is_blacklist = 0 THEN 1
            ELSE 0
        END
        WHERE id=?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect(url_for('index'))


# =========================

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)