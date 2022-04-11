#this will contain the database for the application 
from datetime import timedelta
from flask import Flask, request, session
import os
from os import path as ps
import threading
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
import datetime
import selenium
from selenium import webdriver as wb
import time 

#create_engine("mysql+pymysql://user:pw@host/db", pool_pre_ping=True)
ROOT_DIR = os.path.dirname(os.getcwd())
app = Flask(
    __name__, 
    template_folder=ps.join(ROOT_DIR, 'IskNetwork','test_templates','templates'),
    static_folder=ps.join(ROOT_DIR, 'IskNetwork','static')
)

print('template folder',ps.join(ROOT_DIR, 'templates'))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'top secret!'
app.secret_key = 'password'
app.permanent_session_lifetime = timedelta(minutes=50)
db = SQLAlchemy(app)

# -------------------------------- DATABASE MODEL OBJECTS----------------------------------------------
class UserAccount(db.Model):
    __tablename__ = 'user_account'
    participant_id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(80), nullable=False, default=f'username{participant_id}', unique=True)
    email = Column(String(80), nullable=False, unique=True)
    password = Column(String(80), nullable=False, unique=True)
    post = relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f'''
        UserAccount(
                username : {self.username},
                participant id : {self.participant_id},
                session activity: {self.post}
            )
        '''
    
class Post(db.Model):

    session_id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String(80), nullable=False, default='Default Title')
    visual_display = Column(String(80), nullable=True)
    desciption = Column(String(80), nullable=False, default='default post')
    user_id = Column(Integer, ForeignKey('user_account.participant_id'), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.datetime.utcnow())
    username = Column(String(80), nullable=False, default=f'username{user_id}', unique=True)

    def __repr__(self):
        return f'''
            Post(
                date : {self.date},
                session id : {self.session_id},
                content: {self.content},
                author : {self.user_id}
            )
        '''

class Project(db.Model):

    session_id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String(80), nullable=False, default='Default Title')
    desciption = Column(String(80), nullable=False, default='default post')
    user_id = Column(Integer, ForeignKey('user_account.participant_id'), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.datetime.utcnow())
    description_file = Column(String(80), nullable=False, default='This is the description file of the following post')
    files = Column(String(80), nullable=False)

    def __repr__(self):
        return f'''
            Post(
                date : {self.date},
                session id : {self.session_id},
                content: {self.content},
                author : {self.user_id}
            )
        '''

#------------------------------ BACKEND FUNCTIONALITY-----------------------------------------------

def get_all_users_id():
    db.create_all()
    users = db.session.query(UserAccount).all()
    users_usernames_id = {}
    for i in range(len(users)):
        users_usernames_id[users[i].username] = i
    print(users_usernames_id)
    return users_usernames_id

def reset(reset_all_users=False, reset_all_posts=False):
    if 'username' in session:
        print('          loading reset .....')
        db.create_all()
        all_users = db.session.query(UserAccount).all()
        all_posts = db.session.query(Post).all()
        if reset_all_users:
            for user in all_users:
                users_to_delete = UserAccount.query.filter_by(name=user.participant_id).first()
                db.session.delete(users_to_delete)
                db.session.commit()
        else:
            pass
        if reset_all_posts:
            for post in all_posts:
                posts_to_delete = users_to_delete = Post.query.filter_by(session_id=post.session_id).first()
                db.session.delete(posts_to_delete)
                db.session.commit()
        else:
            pass
        print(all_users)
        session.pop('username', None) 
        session.pop('Node', None) 
        session.pop('date', None) 
    else:
        pass  
    
def increment_id(user_object):
    db.create_all()
    users = db.session.query(user_object).all()
    return len(users) + 1

def initialize_web_app():
    try:
        x = ps.abspath('msedgedriver.exe')
        driver = wb.Edge(x)
        time.sleep(7)
        driver.get('http://127.0.0.1:5500/')
    except selenium.common.exceptions.WebDriverException:
        print(threading.active_count())
        time.sleep(200000)

# when initiialising the thread you can also use: t1 = threading.Timer(5,initialize_web_app)
        
def get_info_from_forms_to_session(*form_key_value_pairs):
    for key in form_key_value_pairs:
        session[key] = request.form[key]     

# the first argument has to be what type of column you want
def retirve_info_from_database_to_session(username):
    db.create_all()
    user_id = get_all_users_id()[username]
    users = db.session.query(UserAccount).all()
    user = users[user_id]
    session['email'] = user.email
    session['password'] = user.password 
    session['username'] = username

    try:
        posts = db.session.query(Post).all()
        for post in posts:
            if post.user_id == user_id:
                mypost = post
            else:
                pass

        post = mypost
        session['post title'] = post.title
        session['post image/video'] = post.visual_display
        session['description'] = post.description
    except:
        print('there might not be no posts')
        
    try:
        projects = db.session.query(Project).all()
        for project in projects:
            if project.user_id == user_id:
                myproject = project
        project = myproject
        session['project title'] = project.title
        session['project description'] = project.desciption
        session['description_file'] = project.description_file
        session['project files'] = project.files         
    except:
        print('there might not be no projects')

def create_user_account():
    user = UserAccount(
        email=session['email'], 
        password=session['password'], 
        username=session['username'], 
        participant_id=increment_id(UserAccount)
    )

    print(user)
    db.session.add(user)
    db.session.commit()

def create_post():
    db.create_all()
    post = Post(
        user_id=get_all_users_id()[session['username']], 
        session_id=increment_id(Post), 
        username=session['username'], 
        title=request.form['title'], 
        visual_display=request.form['visual display'].read(),
        description=request.form['description'],
    )
    print(post)
    db.sesson.add(post)
    db.session.commit()

def create_project():
    print(request.form['description_file'])
    print(request.form['project files'])
    try:
        project = Project(
            session_id=increment_id(Project),
            title=request.form['project title'],
            desciption=request.form['project description'],
            user_id=get_all_users_id()[session['username']],
            description_file=request.form['description_file'],
            files=request.form['project files']         
        )
        print(project)
        db.sesson.add(project)
        db.session.commit()
        return 0
    except KeyError as kerr:
        print(kerr)
        return 'Please complete sign in'


