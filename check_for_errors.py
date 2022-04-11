# remember to [put the check for error.py on the test folder 



from flask import redirect, url_for, render_template, request, session, send_from_directory, flash
import os
import sqlalchemy
import datetime
from database import *

#------------------------------------FLASK APPLICATION-------------------------------------------------
@app.route('/static/<path:filename>')
def serve_static(filename):
    global ROOT_DIR

    return send_from_directory(os.path.join(ROOT_DIR, 'static', 'js'),   filename)    
@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if 'username' in session:
        flash('You have been logged out!!')
        reset()
    else:
        pass
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':

        db.create_all()
        session.permanent = True

        date = request.form['date']
        node = request.form['Node']
        participant_username = request.form['participants']

        #store it in the database if new
        try:
            found_user = UserAccount.query.filter_by(username=participant_username).first()    
        except sqlalchemy.exc.OperationalError:
            found_user = False
        if found_user:
            session['username'] = found_user.username 
            session['Node'] = request.form['Node']
            session['date'] = date
            session['participants'] = participant_username
        else:
            user = UserAccount(username=participant_username, participant_id=increment_id())
            print(user)
            post = Post(content=node, user_id=user.participant_id)#since the id is our primary key it will be assigned automatically
            print(post)
            db.session.add(user)
            db.session.add(post)
            db.session.commit()
            
        #store it on the session 
        if 'username' in session:
            pass
        else:
            session['date'] = request.form['date']
            session['username'] = request.form['participants']
            session['Node'] = request.form['Node']

        return render_template('login.html',todays_date=date, participants=participant_username)
    # in the event the request method is a get request
    else:
        if 'username' in session:
            date = session['date']
            participant_username = session['username']
            flash(f'Hello {participant_username}!!')
            return render_template('login.html', todays_date=date, participants=participant_username)
        else:
            flash(f'Hello please enter your details!!')
            return render_template('login.html', todays_date=datetime.datetime.now())

@app.route("/")
def render_home_page():
    return render_template('index.html')

@app.route("/<page>/")
def render_page(page):
    if page == 'home':
        return render_template('index.html')

    elif page == 'index.html':
        print('start------------------------------')
        return render_template('index.html')

    else:
        return render_template(r'{}.html'.format(page))

        
    

