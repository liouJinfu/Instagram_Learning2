#-*- encoding=UTF-8 -*-

from Liusgram import app

@app.route('/')
def index():
    return 'hello'