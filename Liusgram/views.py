#-*- encoding=UTF-8 -*-

from Liusgram import app
from models import Image, User, Comment
from flask import render_template, redirect, request


@app.route('/')
def index():
    images = Image.query.order_by('id desc').limit(10).all()
    return render_template('index.html', images = images)

@app.route('/image/<int:image_id>/')
def image(image_id):
    image = Image.query.get(image_id)
    if image == None :
        return redirect('/')
    else:
        return render_template('pageDetail.html', image = image)

@app.route('/profile/<int:user_id>')
def user(user_id):
    user = User.query.get(user_id)
    if user == None :
        return redirect('/')
    else :
        return render_template('profile.html', user = user)

@app.route('/loginpage/')
def login():
    return render_template('login.html')

@app.route('/register/')
def register():
    #request.args
    #request.form
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()