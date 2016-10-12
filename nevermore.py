from flask import Flask, render_template, redirect, request, jsonify, session
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

app.secret_key = 'dasu23iga@#$kga3168hguk23t(^)3190'


@app.route('/')
def index():
    if session:
        key = session['username']
    else:
        key = ''
    cursor.execute("SELECT poetry3.*, who_voted.vote, who_voted.fave FROM poetry3 LEFT JOIN who_voted ON poetry3.id = who_voted.comment_id AND who_voted.user_name = %s ORDER BY vote_count DESC", key)
    result = cursor.fetchall()
    return render_template('/tweet_content.html', tweet_content = result)


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
        session['username'] = user_name
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
    session['username'] = user_name
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
    user_name = cursor.fetchone()

    cursor.execute("INSERT INTO poetry3 VALUES (DEFAULT, %s, %s, %s)",  (post_content, user_name, 0))
    conn.commit()

    cursor.execute("SELECT id FROM poetry3 WHERE quote = %s", post_content)
    get_ID = cursor.fetchone()

    cursor.execute("INSERT INTO who_voted VALUES (DEFAULT, 'NULL', %s, 'NULL', 'NULL')",  get_ID)
    conn.commit()

    return redirect('/')

@app.route('/user', methods=['POST'])
def user():
    req_user = request.form['user']
    cursor.execute("SELECT poetry3.quote, COUNT(CASE WHEN fave='FAVE' then `fave` END) AS Fave_Count, COUNT(CASE WHEN vote='UP' then `vote` end ) AS UP FROM who_voted INNER JOIN poetry3 ON who_voted.comment_id = poetry3.id WHERE poetry3.user_name = %s GROUP BY poetry3.quote", req_user)
    user_info = cursor.fetchall()
    return jsonify(user_info=user_info)

@app.route('/vote/<vote_type>', methods=['GET', 'POST'])
def vote(vote_type):
    user_token = request.form['token']
    comment_id = request.form['comment_id']
    cursor.execute("SELECT user_name FROM user WHERE token = '%s'" % user_token)
    result = cursor.fetchone()
    user_name = result[0]
    cursor.execute("SELECT vote, fave FROM who_voted WHERE user_name = %s AND comment_id = %s", (user_name, comment_id))
    who_voted = cursor.fetchall()
    cursor.execute('SELECT vote_count FROM poetry3 WHERE id = "%s"' % comment_id)
    vote = cursor.fetchone()
    if vote is None:
        vote_count = 0
    else:
        vote_count = vote[0]
    print vote_type
    if vote_type == 'FAVE':
        print 'HERE'
        if who_voted:
            if str(who_voted[0][1]) == 'FAVE':
                cursor.execute("UPDATE who_voted SET fave = %s WHERE comment_id = %s AND user_name = %s", ('NULL', comment_id, user_name))
                new_fave = 'NULL'
                conn.commit()
            else:
                cursor.execute("UPDATE who_voted SET fave = %s, vote = %s WHERE comment_id = %s AND user_name = %s", ('FAVE', 'UP', comment_id, user_name))
                conn.commit()
                new_fave = 'FAVE'
                if str(who_voted[0][0]) == 'DOWN':
                    vote_count += 1
                    cursor.execute("UPDATE poetry3 SET vote_count = %s WHERE id = %s", (vote_count, comment_id))
                    conn.commit()
        else:
            new_fave = 'FAVE'
            vote_count += 1
            cursor.execute("INSERT INTO who_voted VALUES (DEFAULT, %s, %s, %s, %s)", (user_name, comment_id, 'UP', 'FAVE'))
            conn.commit()
            
            cursor.execute("UPDATE poetry3 SET vote_count = %s WHERE id = %s", (vote_count, comment_id))
            conn.commit()
        return jsonify(status=200, new_vote=new_fave, vote_count=vote_count)
    else:    
        if who_voted:
            if str(who_voted[0][0]) == vote_type:
                return jsonify(message="You Already Voted")
            else:
                if vote_type == 'UP':
                    vote_count += 1
                    cursor.execute("UPDATE who_voted SET VOTE = %s WHERE comment_id = %s AND user_name = %s", (vote_type, comment_id, user_name))
                elif vote_type == 'DOWN':
                    vote_count -= 1
                    cursor.execute("UPDATE who_voted SET VOTE = %s, fave = %s WHERE comment_id = %s AND user_name = %s", (vote_type, 'NULL', comment_id, user_name))
                conn.commit()
                cursor.execute("UPDATE poetry3 SET vote_count = %s WHERE id = %s", (vote_count, comment_id))
                conn.commit()
                return jsonify(status=200, new_vote=vote_type, vote_count=vote_count)
        else:
            if vote_type == 'UP':
                vote_count += 1
            elif vote_type == 'DOWN':
                vote_count -= 1
            cursor.execute("INSERT INTO who_voted VALUES (DEFAULT, %s, %s, %s, %s)", (user_name, comment_id, vote_type, 'NULL'))
            conn.commit()
            cursor.execute("UPDATE poetry3 SET vote_count = %s WHERE id = %s", (vote_count, comment_id))
            conn.commit()
            return jsonify(status=200, new_vote=vote_type, vote_count=vote_count)

@app.route('/portal')
def portal():
    if session:
        key = session['username']
    else:
        return redirect('/')

    query = "SELECT JK.ID, JK.QUOTE, SUM(JK.UP) AS UP, SUM(JK.DOWN) AS DOWN, JK.Fave_Count FROM (SELECT poetry3.quote as QUOTE, poetry3.id as ID, poetry3.user_name as NAME, COUNT(CASE WHEN vote='DOWN' then `vote` end) AS DOWN, COUNT(CASE WHEN vote='UP' then `vote` end ) AS UP, COUNT(CASE WHEN fave='FAVE' then `fave` END) AS Fave_Count FROM who_voted INNER JOIN poetry3 ON who_voted.comment_id = poetry3.id GROUP BY QUOTE, NAME, ID) AS JK WHERE JK.NAME = %s GROUP BY JK.QUOTE, JK.NAME, JK.ID ORDER BY UP DESC"
    cursor.execute(query, key)
    user_content = cursor.fetchall()

    cursor.execute("SELECT COUNT(CASE WHEN fave='FAVE' then `fave` END) AS Fave_Count, COUNT(CASE WHEN vote='DOWN' then `vote` end) AS DOWN, COUNT(CASE WHEN vote='UP' then `vote` end ) AS UP FROM who_voted INNER JOIN poetry3 ON who_voted.comment_id = poetry3.id WHERE poetry3.user_name = %s GROUP BY poetry3.user_name", key)
    fave_total = cursor.fetchone()

    cursor.execute("SELECT * FROM user WHERE user_name = %s", key)
    user_info = cursor.fetchall()

    return render_template('/portal.html', user_info = user_info[0], user_content = user_content, fave_total = fave_total)

@app.route('/edit', methods=['POST'])
def edit():
    oldPW = request.form['oldPW'].encode('utf-8')
    check_pw = "SELECT * FROM user WHERE user_name = %s"
    cursor.execute(check_pw, session['username'])
    result = cursor.fetchone()
    if result is None:
        return jsonify(status=401, message='No Match for User Name Found.  Please Log In Again.')
    elif bcrypt.checkpw(oldPW, result[3].encode('utf-8')):
        if session['username'] != request.form['userName']:
            check_username = "SELECT * FROM user WHERE user_name = %s"
            cursor.execute(check_username, request.form['userName'])
            result2 = cursor.fetchone()
            if result2 is None:
                if request.form['password']:
                    password = request.form['password'].encode('utf-8')
                else:
                    password = request.form['oldPW'].encode('utf-8')   

                real_name = request.form['fullName']
                hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
                user_name = request.form['userName']
                email = request.form['email']
                session['username'] = user_name
                cursor.execute("UPDATE user SET email = %s, user_name = %s, password = %s, full_name = %s WHERE user_name = %s", (email, user_name, hashed_password, real_name, session['username']))
                conn.commit()
                return jsonify(status=200, message='Successfully Updated!!')
            else:
                return jsonify(status=401, message='User Name Already Taken.  Please Try Another.')
        else:
            password = request.form['password'].encode('utf-8')
            real_name = request.form['fullName']
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
            email = request.form['email']
            cursor.execute("UPDATE user SET email = %s, password = %s, full_name = %s WHERE user_name = %s", (email, hashed_password, real_name, session['username']))
            conn.commit()
            return jsonify(status=200, message='Successfully Updated!!')
    else:
        return jsonify(status=401, message='Current Password Invalid.  Please Try Again.')    

@app.route('/delete/<id>')
def delete(id):
    cursor.execute("DELETE FROM poetry3 WHERE id = %s", id)
    conn.commit()
    cursor.execute("DELETE FROM who_voted WHERE comment_id = %s", id)
    conn.commit()
    return redirect('/portal')       

if __name__ == '__main__':
    app.run(debug=True)

