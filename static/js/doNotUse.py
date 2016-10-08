@app.route('/upvote', methods=['GET', 'POST'])
def upvote():
    user_token = request.form['token']
    comment_id = request.form['comment_id']
    cursor.execute("SELECT user_name FROM user WHERE token = '%s'" % user_token)
    result = cursor.fetchone()
    user_name = result[0]
    cursor.execute("SELECT user_name, vote, comment_id FROM who_voted WHERE user_name = %s AND comment_id = %s", (user_name, comment_id))
    who_voted = cursor.fetchall()
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
            cursor.execute("UPDATE who_voted SET VOTE = %s WHERE comment_id = %s AND user_name = %s", ('UP', comment_id, user_name))
            conn.commit()
            return jsonify(status=200, vote_count=vote_count)

    else:
        vote_count += 1
        cursor.execute("UPDATE poetry3 SET vote_count = %s WHERE id = %s", (vote_count, comment_id))
        conn.commit()
        cursor.execute("INSERT INTO who_voted VALUES (DEFAULT, %s, %s, %s, %s)", (user_name, comment_id, 'UP', 'NULL'))
        conn.commit()
        return jsonify(status=200, vote_count=vote_count)



@app.route('/downvote', methods=['GET', 'POST'])
def downvote():
    user_token = request.form['token']
    comment_id = request.form['comment_id']
    cursor.execute("SELECT user_name FROM user WHERE token = '%s'" % user_token)
    result = cursor.fetchone()
    user_name = result[0]
    cursor.execute("SELECT user_name, vote, comment_id FROM who_voted WHERE user_name = %s AND comment_id = %s", (user_name, comment_id))
    who_voted = cursor.fetchall()
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
            cursor.execute("UPDATE who_voted SET VOTE = %s, fave = %s WHERE comment_id = %s AND user_name = %s", ('DOWN', 'NULL', comment_id, user_name))
            conn.commit()
            return jsonify(status=200, vote_count=vote_count)

    else:
        vote_count -= 1
        cursor.execute("UPDATE poetry3 SET vote_count = %s WHERE id = %s", (vote_count, comment_id))
        conn.commit()
        cursor.execute("INSERT INTO who_voted VALUES (DEFAULT, %s, %s, %s, %s)", (user_name, comment_id, 'DOWN', 'NULL'))
        conn.commit()
        return jsonify(status=200, vote_count=vote_count)

@app.route('/favorite', methods=['GET', 'POST'])
def favorite():
    user_token = request.form['token']
    comment_id = request.form['comment_id']
    cursor.execute("SELECT user_name FROM user WHERE token = '%s'" % user_token)
    result = cursor.fetchone()
    user_name = result[0]

    cursor.execute("SELECT fave, vote FROM who_voted WHERE user_name = %s AND comment_id = %s", (user_name, comment_id))
    fave = cursor.fetchall()

    cursor.execute('SELECT vote_count FROM poetry3 WHERE id = "%s"' % comment_id)
    vote = cursor.fetchone()
    vote_count = vote[0]

    if fave:
        if str(fave[0][0]) == 'FAVE':
            cursor.execute("UPDATE who_voted SET fave = %s WHERE comment_id = %s AND user_name = %s", ('NULL', comment_id, user_name))
            new_fave = 'NULL'
            conn.commit()
        else:
            cursor.execute("UPDATE who_voted SET fave = %s, vote = %s WHERE comment_id = %s AND user_name = %s", ('FAVE', 'UP', comment_id, user_name))
            conn.commit()
            new_fave = 'FAVE'
            if str(fave[0][1]) == 'DOWN':
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
    return jsonify(status=200, new_fave=new_fave, vote_count=vote_count)
