import logging
from flask import render_template, flash, redirect, url_for, request
from app import app, query_db, login
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm, LoginForm, RegisterForm
from datetime import datetime
from config import User
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
import os
from werkzeug.security import generate_password_hash, check_password_hash

# this file contains all the different routes, and the logic for communicating with the database

# Set up log file
logging.basicConfig(filename='record.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s : %(message)s')

#Broken access control
@login.user_loader
def load_user(user_id):
    user = query_db('SELECT * FROM Users WHERE id="{}";'.format(user_id), one=True)
    if user is None:
        return None
    else:
        return User(user_id, user[1])

@login.unauthorized_handler
def unauthorized_callback():
    flash("Unauthorized")       
    return redirect(url_for('index'))

# home page/login/registration
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = IndexForm()
    if current_user.is_authenticated:
        return redirect(url_for('stream', username=current_user.username))
    if form.login.is_submitted() and form.login.submit.data:
        captcha_login_response = request.form['g-recaptcha-response']
        if len(captcha_login_response) > 1:
            user = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.login.username.data), one=True)
            if user == None:
                flash('Sorry, wrong password or username!')
                app.logger.warning('Failed login attemt with username %s', form.login.username.data)
            elif check_password_hash(user['password'], form.login.password.data):
                login_form = LoginForm()
                Us = load_user(user["id"])
                login_user(Us, remember=login_form.remember_me.data)
                return redirect(url_for('stream', username=form.login.username.data))
            else:
                flash('Sorry, wrong password or username!')
                app.logger.warning('Failed login attemt from %s', form.login.username.data)
        else:
            flash("Please confirm that you are not a robot")
    elif form.register.validate_on_submit() and form.register.submit.data:
        users = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.register.username.data), one=True)
        app.logger.info(users)
        if users != None:
            flash("User already exsists")
        else:
            captcha_reg_response = request.form['g-recaptcha-response']
            if len(captcha_reg_response) > 1:
                app.logger.info("user added to db")
                password_hashed = generate_password_hash(form.register.password.data)
                query_db('INSERT INTO Users (username, first_name, last_name, password) VALUES("{}", "{}", "{}", "{}");'.format(form.register.username.data, form.register.first_name.data,
                form.register.last_name.data, password_hashed))
                return redirect(url_for('index'))
            else:
                flash("Please confirm that you are not a robot")
    return render_template('index.html', title='Welcome', form=form)

@app.route('/logout')
def logout():
    form = IndexForm()
    logout_user()
    return redirect(url_for('index'))

# content stream page
@app.route('/stream/<username>', methods=['GET', 'POST'])
@login_required
def stream(username):
    if username != current_user.get_username():
        return redirect(url_for('stream', username=current_user.get_username()))
    else:
        form = PostForm()
        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
        if form.validate_on_submit():
            file = os.path.splitext(form.image.data.filename)
            type = file[1]
            if type in app.config["ALLOWED_EXTENSIONS"]:
                path = os.path.join(app.config['UPLOAD_PATH'], form.image.data.filename)
                form.image.data.save(path)
                query_db('INSERT INTO Posts (u_id, content, image, creation_time) VALUES({}, "{}", "{}", \'{}\');'.format(user['id'], form.content.data, form.image.data.filename, datetime.now()))
                return redirect(url_for('stream', username=username))
            elif not form.image.data:
                query_db('INSERT INTO Posts (u_id, content, image, creation_time) VALUES({}, "{}", "{}", \'{}\');'.format(user['id'], form.content.data, form.image.data.filename, datetime.now()))
                return redirect(url_for('stream', username=username))
            else:
                flash("Can only accept images of type .jpg or .png")

    posts = query_db('SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id=p.id) AS cc FROM Posts AS p JOIN Users AS u ON u.id=p.u_id WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id={0}) OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id={0}) OR p.u_id={0} ORDER BY p.creation_time DESC;'.format(user['id']))
    return render_template('stream.html', title='Stream', username=username, form=form, posts=posts)

# comment page for a given post and user.
@app.route('/comments/<username>/<int:p_id>', methods=['GET', 'POST'])
@login_required
def comments(username, p_id):
    if username != current_user.get_username():
        return redirect(url_for('comments', username=current_user.get_username(), p_id = p_id))
    else:
        form = CommentsForm()
        if form.validate_on_submit():
            user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
            query_db('INSERT INTO Comments (p_id, u_id, comment, creation_time) VALUES({}, {}, "{}", \'{}\');'.format(p_id, user['id'], form.comment.data, datetime.now()))

        post = query_db('SELECT * FROM Posts WHERE id={};'.format(p_id), one=True)
        all_comments = query_db('SELECT DISTINCT * FROM Comments AS c JOIN Users AS u ON c.u_id=u.id WHERE c.p_id={} ORDER BY c.creation_time DESC;'.format(p_id))
        return render_template('comments.html', title='Comments', username=username, form=form, post=post, comments=all_comments)

# page for seeing and adding friends
@app.route('/friends/<username>', methods=['GET', 'POST'])
@login_required
def friends(username):
    if username != current_user.get_username():
        return redirect(url_for('friends', username=current_user.get_username()))
    else:
        form = FriendsForm()
        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
        if form.validate_on_submit():
            friend = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.username.data), one=True)
            if friend is None:
                flash('User does not exist')
            else:
                query_db('INSERT INTO Friends (u_id, f_id) VALUES({}, {});'.format(user['id'], friend['id']))
        
        all_friends = query_db('SELECT * FROM Friends AS f JOIN Users as u ON f.f_id=u.id WHERE f.u_id={} AND f.f_id!={} ;'.format(user['id'], user['id']))
        return render_template('friends.html', title='Friends', username=username, friends=all_friends, form=form)

# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    form = ProfileForm()
    if username == current_user.get_username():
        if form.validate_on_submit():
            query_db('UPDATE Users SET education="{}", employment="{}", music="{}", movie="{}", nationality="{}", birthday=\'{}\' WHERE username="{}" ;'.format(
                form.education.data, form.employment.data, form.music.data, form.movie.data, form.nationality.data, form.birthday.data, username
            ))
            return redirect(url_for('profile', username=username))
        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
        return render_template('profile.html', title='profile', authenticated = True, username=username, user=user, form=form)
    else:
        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
        return render_template('profile.html', title='profile', authenticated = False, username=username, user=user, form=form)