from flask import Flask, render_template, redirect, request, jsonify
from flaskext.mysql import MySQL
import bcrypt

mysql =  MySQL()
app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'x'
app.config['MYSQL_DATABASE_PASSWORD'] = 'x'
app.config['MYSQL_DATABASE_DB'] = 'nevermore'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

@app.route('/')
def index():
    cursor.execute("SELECT poetry3.*, who_voted.vote FROM poetry3 LEFT JOIN who_voted ON poetry3.id = who_voted.comment_id ORDER BY vote_count DESC")
    result = cursor.fetchall()
    return render_template('/tweet_content.html', tweet_content = result)

# @app.route('/register')
# def register():
#     if request.args.get('username'):
#         return render_template('register.html', message = "That Username is already taken.")
#     else:
#         return render_template('/register.html')

@app.route('/register', methods=['POST'])
def register():
    # Check to See if the Username is already taken
    check_username = "SELECT * FROM user WHERE user_name = %s"
    cursor.execute(check_username, request.form['userName'])
    result=cursor.fetchone()
    if result is None:
        real_name = request.form['fullName']
        password = request.form['password'].encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        user_name = request.form['userName']
        email = request.form['email']
        token = bcrypt.gensalt()
        cursor.execute("INSERT INTO user VALUES (DEFAULT, %s, %s, %s, %s, %s)", (email, user_name, hashed_password, real_name, token))
        conn.commit()
        return jsonify(status=200, token=token)
    else:
        return redirect(status=401)

@app.route('/login', methods=['POST'])
def login():
    req_pass = request.form['password'].encode('utf-8')
    user_name = request.form['userName'].encode('utf-8')
    check_username = "SELECT password FROM user WHERE user_name = %s"
    cursor.execute(check_username, user_name)
    result = cursor.fetchone()
    if result is None:
        return jsonify(status=401)
    if bcrypt.checkpw(req_pass, result[0].encode('utf-8')):
        token = bcrypt.gensalt()
        cursor.execute("UPDATE user SET token = %s WHERE user_name = %s", (token, user_name))
        conn.commit()
        return jsonify(status=200, token=token)
    else:
        return jsonify(status=401)


@app.route('/auth', methods=['POST'])
def auth():
    req_token = request.form['token']
    cursor.execute('SELECT token FROM user WHERE token= %s', req_token)

    if cursor.fetchone() is not None:
        return jsonify(status=200)
    else:
        return jsonify(status=401)


@app.route('/get_user', methods=['POST'])
def get_user():
    req_token = request.form['token']
    cursor.execute('SELECT user_name FROM user WHERE token= %s', req_token)
    result = cursor.fetchone()
    if result is not None:
        return jsonify(status=200, username=result[0])
    else:
        return jsonify(status=401)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/post_submit', methods=['POST'])
def post_submit():
    post_content = request.form['post_content']
    user_token = request.form['hidID']
    get_user_name = "SELECT user_name FROM user WHERE token = %s"
    cursor.execute(get_user_name, user_token)
    user_name_result = cursor.fetchall()
    user_name = user_name_result[0]

    cursor.execute("INSERT INTO poetry3 VALUES (DEFAULT, %s, %s, %s)",  (post_content, user_name, 0))
    conn.commit()

    return redirect('/')

@app.route('/upvote', methods=['GET', 'POST'])
def upvote():
    user_token = request.form['token']
    comment_id = request.form['comment_id']
    cursor.execute("SELECT user_name FROM user WHERE token = '%s'" % user_token)
    result = cursor.fetchone()
    user_name = result[0]
    cursor.execute("SELECT user_name, vote FROM who_voted WHERE id = '%s'" % comment_id)
    who_voted = cursor.fetchall()
    print who_voted
    cursor.execute('SELECT vote_count FROM poetry3 WHERE id = "%s"' % comment_id)
    vote = cursor.fetchone()
    if vote is None:
        vote_count = 0
    else:
        vote_count = vote[0]

    if who_voted:
        if str(who_voted[0][1]) == 'UP':
            return jsonify(message="You Already Voted")
        else:
            vote_count += 1
            cursor.execute("UPDATE poetry3 SET vote_count = %s WHERE id = %s", (vote_count, comment_id))
            conn.commit()
            cursor.execute("UPDATE who_voted SET VOTE = %s WHERE id = %s", ('UP', comment_id))
            conn.commit()
            return jsonify(status=200, vote_count=vote_count)

    else:
        vote_count += 1
        cursor.execute("UPDATE poetry3 SET vote_count = %s WHERE id = %s", (vote_count, comment_id))
        conn.commit()
        cursor.execute("INSERT INTO who_voted VALUES (DEFAULT, %s, %s, %s)", (user_name, comment_id, 'UP'))
        conn.commit()
        return jsonify(status=200, vote_count=vote_count)



@app.route('/downvote', methods=['GET', 'POST'])
def downvote():
    user_token = request.form['token']
    comment_id = request.form['comment_id']
    cursor.execute("SELECT user_name FROM user WHERE token = '%s'" % user_token)
    result = cursor.fetchone()
    user_name = result[0]
    cursor.execute("SELECT user_name, vote FROM who_voted WHERE id = '%s'" % comment_id)
    who_voted = cursor.fetchall()
    print who_voted
    cursor.execute('SELECT vote_count FROM poetry3 WHERE id = "%s"' % comment_id)
    vote = cursor.fetchone()
    if vote is None:
        vote_count = 0
    else:
        vote_count = vote[0]

    if who_voted:
        if str(who_voted[0][1]) == 'DOWN':
            return jsonify(message="You Already Voted")
        else:
            vote_count -= 1
            cursor.execute("UPDATE poetry3 SET vote_count = %s WHERE id = %s", (vote_count, comment_id))
            conn.commit()
            cursor.execute("UPDATE who_voted SET VOTE = %s WHERE id = %s", ('DOWN', comment_id))
            conn.commit()
            return jsonify(status=200, vote_count=vote_count)

    else:
        vote_count -= 1
        cursor.execute("UPDATE poetry3 SET vote_count = %s WHERE id = %s", (vote_count, comment_id))
        conn.commit()
        cursor.execute("INSERT INTO who_voted VALUES (DEFAULT, %s, %s, %s)", (user_name, comment_id, 'DOWN'))
        conn.commit()
        return jsonify(status=200, vote_count=vote_count)




if __name__ == '__main__':
    app.run(debug=True)

