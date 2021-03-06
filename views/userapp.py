#!/usr/bin/python
#-*-coding:utf-8-*-

from flask import Module, request, session, url_for, redirect, render_template, abort
from database import db_session
from forms import *
from models import *
from functions import *
import hashlib

userapp = Module(__name__)
d = {}

@userapp.route('/login/', methods=['GET', 'POST'])
def login():
    errors = False
    form = LoginForm(request.form, csrf_enabled=False)
    if request.method == 'POST' and form.validate_on_submit() and form.captcha.data.lower() == session['captcha'].lower():
        try:
            user = db_session.query(User).filter_by(email=form.email.data,
                password=hashlib.md5(form.password.data).hexdigest()).one()
        except:
            user = None
        if user:
            session['user'] = {'id':user.id, 'nickname':user.nickname, 'email':user.email}
            return redirect('/')
        else:
            errors = True
    d['form'] = form
    d['errors'] = errors
    return render_template('userapp/login.html', **d)

@userapp.route('/logout/', methods=['GET'])
def logout():
    if 'user' in session:
        session['user'] = None
        del(session['user'])
    return redirect('/')

@userapp.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form, csrf_enabled=False)
    if request.method == 'POST' and form.validate_on_submit() and form.captcha.data.lower() == session['captcha'].lower():
        user = User(form.nickname.data, form.email.data, form.password.data)
        db_session.add(user)
        try:
            db_session.commit()
        except:
            abort(500)
        return redirect(url_for('login'))
    d['form'] = form
    return render_template('userapp/register.html', **d)

@userapp.route('/view/<user_id>', methods=['GET'])
def view(user_id):
    try:
        user_id = int(user_id)
    except:
        abort(404)
    user = db_session.query(User).get(user_id)
    if user:
        d['user'] = user
        d['pastes'] = db_session.query(Paste).filter_by(user_id=user.id).all()[:10]
        return render_template('userapp/view.html', **d)
    abort(404)
