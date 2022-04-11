from flask import redirect, url_for, render_template, request, session, send_from_directory, flash
import os
import sqlalchemy
import datetime
from database import *
from Google_Api import gmail_api
#------------------------------------FLASK APPLICATION-------------------------------------------------

@app.route('/login/forgotten_password', methods=['POST', 'GET'])
def handle_forgotten_passwords():
    if request.method == 'POST':
        email  = request.form['email']
        code = gmail_api.send_code_to_recipient(email)
        print(code)
        return render_template('signup.html')
    elif request.method == 'GET':
        return render_template('forgotten_password.html')
    else:
        return render_template('forgotten_password.html')

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if 'username' in session:
        flash('You have been logged out!!')
        reset()
    else:
        pass
    return render_template('index.html')

@app.route('/profile/projects', methods=['POST', 'GET'])
def profile():
    if request.method == 'POST':
        concerns_to_raise = create_project()
        print(concerns_to_raise) if type(concerns_to_raise) == int else flash(concerns_to_raise)
        return render_template('project_view.html')
    else:
        return render_template('projects.html')

@app.route('/profile/edit_profile_page', methods=['POST', 'GET'])
def edit_picture():
    if request.method == 'POST':
        print(request.form['profile-picture'])
        return render_template('edit_profile_page.html')
    else:
        return render_template('edit_profile_page.html')

@app.route('/login/feed', methods=['POST', 'GET'])
def feed():
    # create a function create_post(feed information) -> HTML lines for the post to append to the feed 
    # HTML file
    pass

@app.route('/login/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':

        db.create_all()
        session.permanent = True

        try:
            users = db.session.query(UserAccount).all()
            user = users[get_all_users_id()[request.form['username']]]
            print(user)
            session['username'] = user.username
        
            get_info_from_forms_to_session('username', 'password')
            retirve_info_from_database_to_session(session['username'])
            flash(f'{user.username} you have been successfully logged in !!')
            return render_template('profile.html')
        except AttributeError as err:
            print(err)
            flash('Please enter a valid email and password or use the alternative links above')
            return render_template('login.html')
    # in the event the request method is a get request
    else:
        if 'username' in session:
            get_info_from_forms_to_session('username', 'password')
            retirve_info_from_database_to_session(session['username'])
            flash(f"Hello {session['username']}!!")
            return render_template('profile.html')
        else:
            flash(f'Hello please enter your details!!')
            return render_template('login.html')

@app.route('/login/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        get_info_from_forms_to_session('username', 'email', 'city', 'name','password','postcode','last-name')
        print('creating new account.. for')
        print(f"{session['username']}")
        create_user_account()
    return render_template('signup.html')

@app.route("/<page>/", methods=['POST', 'GET'])
def render_page(page):
    print(page)
    if page == '/':
        return render_template('home.html')
    elif page == 'favicon.ico':
        pass
    else:
        return render_template(r'{}.html'.format(page))
      
if __name__ == '__main__':
    app.run(debug=True, port=5500)
    db.create_all()
    ts = threading.Thread(target=initialize_web_app)
    ts.start() 