from dc import app, db
from werkzeug.utils import secure_filename
import joblib
from dc.models import User, FlipkartQuery
from flask import request, render_template, session, flash, redirect, url_for, current_app
import os
import skops.io as sio
from training.train import *


@app.before_request
def create_tables():
    db.create_all()

def storeInDb(filepath):
    with open(filepath, 'r') as file:
        r = file.readlines()[1:]
        for data in r:
            trim = data.strip()
            s = trim.split('\t')
            feature, label = s
            fkq = FlipkartQuery(feature=feature, label=label)
            db.session.add(fkq)
            db.session.commit()
            print('INFO: successfully sent to db')

            # features.append(feature)
            # labels.append(label)


def index():
    if 'email' in session:
        email = session['email']

        if request.method == 'POST':
            uploaded_file = request.files['file']
            if uploaded_file.filename != '':
                filepath = os.path.join(app.instance_path, 'files')
                if not os.path.exists(filepath):
                    os.makedirs(os.path.join(app.instance_path, 'files'), exist_ok=True)
                # set the file path
                uploaded_file.save(os.path.join(app.instance_path, 'files', secure_filename(uploaded_file.filename)))
                storeInDb(os.path.join(app.instance_path, 'files', secure_filename(uploaded_file.filename)))
                all = FlipkartQuery.query.all()
                #path = '../training/query_model1.sav'
                return render_template('index.html', email=email, all=all[:10])
        else:
            return render_template('index.html', email=email)
app.add_url_rule('/', 'index', index, methods=['GET','POST'])

def login():
    if request.method == 'POST':
        session.permanent = True
        email = request.form['email']
        pword = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(pword):
            session['email'] = email
            flash('You have login successfully', 'success')
            return redirect(url_for('index'))
    else:
        return render_template('login.html')
app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])

def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        pword = request.form['password']
        rpass = request.form['r_pass']

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', 'info')
            return redirect(url_for('register'))
        else:
            if pword != rpass:
                flash('Repeated password not equal to password', 'error')
                return redirect(url_for('register'))
            user = User(name=name, email=email)
            user.set_password(pword)
            db.session.add(user)
            db.session.commit()
            flash('Added User successfully', 'success')
            return redirect(url_for('login'))
    else:
        return render_template('register.html')
app.add_url_rule('/register', 'register', register, methods=['GET', 'POST'])

def logout():
    if 'email' in session:
        email = session['email']
    flash(f'You have been logged out successfully, {email}', 'success')
    session.pop('email', None)
    return redirect(url_for('login'))
app.add_url_rule('/logout', 'logout', logout, methods=['GET', 'POST'])

def testtrimming(filepath):
    trim_list = []
    with open(filepath, 'r') as file:
        r = file.readlines()[1:]
        for data in r:
            trim = data.strip()
            trim_list.append(trim)
    return trim_list

def predict():
    if 'email' in session:
        email = session['email']
        if request.method == 'POST':
            uploaded_file = request.files['file']
            if uploaded_file.filename != '':
                filepath = os.path.join(app.instance_path, 'files')
                if not os.path.exists(filepath):
                    os.makedirs(os.path.join(app.instance_path, 'files'), exist_ok=True)
                uploaded_file.save(os.path.join(app.instance_path, 'files', secure_filename(uploaded_file.filename)))
                trimmed_list = testtrimming(os.path.join(app.instance_path, 'files', secure_filename(uploaded_file.filename)))
                preprocessed_list = preprocess_text(trimmed_list)
                grammed_text = make_grams(preprocessed_list)
                vector_text = vectorizer.transform(grammed_text).toarray()
                check_model_location = os.path.join(app.instance_path,'model_files')
                if not os.path.exists(check_model_location):
                    os.makedirs(check_model_location, exist_ok=True)
                model_location = os.path.join(app.instance_path,'model_files','mymodel.sav')
                loaded_model = pickle.load(open(model_location, 'rb'))
                #loaded_model = sio.load(open(model_location), trusted=True)
                ypredictions = loaded_model.predict(vector_text)
                ypredictions = list(ypredictions)
                data_preds = list(zip(trimmed_list, ypredictions))
                return render_template('predict.html', data=data_preds)
        else:
            return render_template('predict.html')
app.add_url_rule('/predict', 'predict', predict, methods=['GET','POST'])


def login_required(func):

    def wrapper(*args, **kwargs):

        if session != {}:

           return func(*args,**kwargs)
        else:
            flash('Please sign in first', 'info')
            return render_template('login.html')

    return wrapper