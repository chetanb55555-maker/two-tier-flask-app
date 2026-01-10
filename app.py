import os
import time
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL config
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'default_user')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'default_password')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'default_db')

mysql = MySQL(app)

@app.route('/health')
def health():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT 1')
        cur.close()
        return jsonify(status="ok", db="connected"), 200
    except Exception as e:
        return jsonify(status="error", db=str(e)), 500

def init_db(retries=5):
    while retries:
        try:
            with app.app_context():
                cur = mysql.connection.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        message TEXT
                    );
                """)
                mysql.connection.commit()
                cur.close()
            break
        except Exception:
            retries -= 1
            time.sleep(3)

@app.route('/')
def hello():
    cur = mysql.connection.cursor()
    cur.execute('SELECT message FROM messages')
    messages = cur.fetchall()
    cur.close()
    return render_template('index.html', messages=messages)

@app.route('/submit', methods=['POST'])
def submit():
    new_message = request.form.get('new_message')
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO messages (message) VALUES (%s)', [new_message])
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': new_message})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
