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
