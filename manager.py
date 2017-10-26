#-*- encoding=UTF-8 -*-

from Liusgram import app, db
from flask_script import Manager
from Liusgram.models import User, Image, Comment
import random
from sqlalchemy import or_, and_
manager = Manager(app)

def getImageUrl():
    return 'http://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 't.png'
@manager.command
def init_database():
    db.drop_all()
    db.create_all()
    for i in range(0, 100):
        db.session.add(User('user'+ str(i+1), 'a' + str(i+1)))
        for j in range(0, 3):
            db.session.add(Image(getImageUrl(), str(i+1)))
            for k in range(0, 3):
                db.session.add(Comment('comments'+str(k),  1+3*i+j, i+1))
    db.session.commit()
    print 1, User.query.all()
    print 2, User.query.get(3)
    print 3, User.query.filter_by(id = 5).first()
    print 4, User.query.order_by(User.id.desc()).offset(1).limit(2).all()
    print 5, User.query.filter(User.username.endswith('0')).limit(3).all()
    print 6, User.query.filter(and_(User.id > 88, User.id < 99)).limit(3).all()
    print 7, User.query.order_by(User.id.desc()).paginate(page=2, per_page=10).items
    user = User.query.get(1)
    print 8, user.images.all()

    image = Image.query.get(1)
    print 11, image.user



if __name__ == '__main__':
    manager.run()