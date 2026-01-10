import os
import time
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL config from environment variables
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'default_user')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'default_password')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'default_db')

mysql = MySQL(app)

def init_db(retries=10, delay=5):
    """Initialize DB and create messages table; retry until MySQL is ready"""
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
            print("DB initialized ✅")
            break
        except Exception as e:
            print(f"DB init failed: {e}, retrying...")
            retries -= 1
            time.sleep(delay)
    else:
        print("Could not initialize DB ❌")

@app.route('/health')
def health():
    """Health endpoint checks DB connectivity"""
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT 1')
        cur.close()
        return jsonify(status="ok", db="connected"), 200
    except Exception as e:
        return jsonify(status="error", db=str(e)), 500

@app.route('/')
def hello():
    """Render all messages"""
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT message FROM messages')
        messages = cur.fetchall()
        cur.close()
        return render_template('index.html', messages=messages)
    except Exception as e:
        return f"DB Error: {e}", 500

@app.route('/submit', methods=['POST'])
def submit():
    """Insert new message"""
    new_message = request.form.get('new_message')
    if not new_message:
        return jsonify({'error': 'No message provided'}), 400
    try:
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO messages (message) VALUES (%s)', [new_message])
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': new_message}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
