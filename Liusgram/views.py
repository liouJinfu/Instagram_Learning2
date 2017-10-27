#-*- encoding=UTF-8 -*-

from Liusgram import app
from models import Image, User, Comment
from flask import render_template, redirect
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