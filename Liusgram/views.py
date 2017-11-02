#-*- encoding=UTF-8 -*-

from Liusgram import app, db
from models import Image, User, Comment
from flask import render_template, redirect, request, flash, get_flashed_messages, send_from_directory
import random, hashlib, json
from flask_login import login_user, logout_user, login_required, current_user
import os, uuid
from Liusgram.QiniuYun import upload_file_from_path, upload_file_from_stream

@app.route('/')
def index():
    # images = Image.query.order_by(db.desc(Image.id)).limit(10).all()
    paginate = Image.query.order_by(db.desc(Image.id)).paginate(page=1, per_page=10)
    return render_template('index.html', has_next = paginate.has_next, images = paginate.items)

@app.route('/image/<int:image_id>/')
@login_required
def image(image_id):
    image = Image.query.get(image_id)

    if image == None :
        return redirect('/')
    else:
        return render_template('pageDetail.html', image = image)

@app.route('/profiles/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get(user_id)
    if user == None :
        return redirect('/')
    # paginate = Image.query.filter_by(user_id = user_id).paginate(page = 1, per_page = 3, error_out = False)
    paginate = Image.query.paginate(page=1, per_page=3)
    return render_template('profile.html', user = user, has_next = paginate.has_next, images = paginate.items)

@app.route('/profiles/images/<int:user_id>/<int:page>/<int:per_page>/')
def user_images(user_id, page, per_page):
    # 参数检查
    paginate = Image.query.filter_by(user_id = user_id).paginate(page=page, per_page=per_page)

    map = {'has_next':paginate.has_next}
    images = []
    for image in paginate.items:
        imgvo = {'id':image.id, 'url':image.image_url, 'comment_count': len(image.comments)}
        images.append(imgvo)
    map['images'] = images
    return json.dumps(map)


@app.route('/regloginpage/')
def regloginpage():
    msg = ''
    for m in get_flashed_messages(with_categories=False, category_filter=['register','reglogin']):
        msg += m
    return render_template('login.html', msg = msg, next = request.values.get('next'))

@app.route('/login/', methods={'post', 'get'})
def login():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()
    next = request.values.get('next')
    # 校验
    if username == '' or password == '':
        return redirect_with_msg('/regloginpage/'+ '?next=' + next, u'用户名和密码不能为空', 'reglogin')

    user = User.query.filter_by(username=username).first()
    if user == None:
        return redirect_with_msg('/regloginpage/'+ '?next=' + next, u'用户名不存在', 'reglogin')

    m = hashlib.md5()
    m.update(password + user.salt)
    if m.hexdigest() != user.password:
        return redirect_with_msg('/regloginpage/' + '?next=' + next, u'密码错误', 'reglogin')

    login_user(user)
    if next != None and next.startswith('/') > 0:
        return redirect(next)
    return redirect('/')
def redirect_with_msg(target, msg, category):
    if msg != None:
        flash(msg, category = category)
    return redirect(target)

@app.route('/register/', methods={'post', 'get'})
def register():
    #request.args
    #request.form
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    if username == '':
        return redirect_with_msg('/regloginpage/', u'用户名不能为空', category='register')
    if password == '':
        return redirect_with_msg('/regloginpage/', u'密码不能为空', category='register')

    user = User.query.filter_by(username = username).first()
    if user != None:
        return redirect_with_msg('/regloginpage/', u'用户名已经存在', category='register')
    ##写更多的判断
    salt = '.'.join(random.sample('0123456789abcdefghigklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 10))
    m = hashlib.md5()
    m.update(password + salt)
    password = m.hexdigest()
    user = User(username, password, salt)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect('/')
@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/')

##
def save_to_Yun(file, filename):
    save_dir = app.config['UPLOAD_DIR']
    file.save(os.path.join(save_dir, filename))
    filePath = os.path.join(save_dir, filename)
    url = upload_file_from_path(filename, filePath)
    try :
        os.remove(os.path.join(save_dir, filename))
    except Exception,e:
        print e ## 暂时没有开启log 模式等待开启
    return url

@app.route('/image/<image_name>')
def show_image(image_name):
    return send_from_directory(app.config['UPLOAD_DIR'], image_name)

@app.route('/upload/', methods=['post'])
def upload():
    # print type(request.files), request.files
    file = request.files['file']
    # dir(file)
    file_ext = ''
    if file.filename.find('.') > 0:
        file_ext = file.filename.rsplit('.', 1)[1].strip().lower()
    if file_ext in app.config['ALLOWED_EXT']:
        file_name  = str(uuid.uuid1()).replace('-', '') + '.' + file_ext
        url = save_to_Yun(file, file_name)
        if url != None:
            db.session.add(Image(url, current_user.id))
            db.session.commit()
    return redirect('/profiles/%d' % current_user.id)

@app.route('/addcomment/', methods=['post'])
@login_required
def add_comment():
    image_id = int(request.values.get('image_id'))
    content = request.values.get('content')
    comment = Comment(content, image_id, current_user.id)
    db.session.add(comment)
    db.session.commit()
    return json.dumps({"code" : 0, "id" : comment.id,
                       "content" : content, "username" : comment.user.username,
                       "user_id" : comment.user.id })

@app.route('/index/image/<int:page>/<int:per_page>/')
def index_images(page, per_page):
    paginate = Image.query.order_by(db.desc(Image.id)).paginate(page = page, per_page=per_page)
    images = []
    map = {'has_next':paginate.has_next}
    for image in paginate.items:
        comment_content = []
        comment_username = []
        comment_userid = []
        for i in range(0, min(2, len(image.comments))):
            comment = image.comments[i]
            comment_username.append(comment.user.username)
            comment_content.append(comment.comment)
            comment_userid.append(comment.user_id)
        imgvo = {'id':image.id,
                 'head_url':image.user.head_url,
                 'url':image.image_url,
                 'user_name':image.user.username,
                 'comment_count':len(image.comments),
                 'user_id':image.user_id,
                 'created_date':str(image.create_date),
                 'comment_content':comment_content,
                 'comment_username':comment_username,
                 'comment_userid': comment_userid}
        images.append(imgvo)
    map['images'] = images
    return json.dumps(map)