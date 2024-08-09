from flask import Flask, render_template, url_for, make_response, session
from flask import request, redirect, flash, get_flashed_messages
import json
from ast import literal_eval


app = Flask(__name__)


app.secret_key = "secret_key"


id = 0


@app.route('/users')
def get_users():
    users = json.loads(request.cookies.get('users', json.dumps({})))
    messages = get_flashed_messages(with_categories=False)
    current_user = session.get('user')
    return render_template(
        'users/index.html',
        users=users,
        current_user=current_user,
        messages=messages
    )


@app.route('/users/new')
def users_new():
    user = {'nickname': '', 'email': ''}
    errors = {}
    return render_template(
        'users/new.html',
        user=user,
        errors=errors
    )


def validate(data):
    if data['nickname'] == '' or data['email'] == '':
        return {'name': 'oops!'}


@app.post('/users')
def users_post():
    global id
    id += 1
    data = request.form.to_dict()
    errors = validate(data)
    if errors:
        return render_template(
            'users/new.html',
            user=data,
            errors=errors
            ), 422
    users = request.cookies.get('users')
    users = json.loads(users) if users else {}
    users[id] = data
    response = make_response(redirect(url_for('get_users'), code=302))
    response.set_cookie('users', json.dumps(users))
    flash('User was added successfully', 'success')
    return response


@app.route('/users/<id>')
def get_user(id):
    users = request.cookies.get('users')
    users = literal_eval(users)
    for i, data in users.items():
        if int(i) == int(id):
            user = data
    if not user:
        return 'Page not found', 404
    return render_template(
          'users/show.html',
          user=user,
          )


@app.route('/users/<id>/update', methods=['GET', 'POST'])
def user_update(id):
    users = request.cookies.get('users')
    users = literal_eval(users)
    for i, data in users.items():
        if int(i) == int(id):
            user = data

    if request.method == 'GET':
        return render_template(
            'users/edit.html',
            user=user,
            users=users,
            errors={},
            )

    if request.method == 'POST':
        new = request.form.to_dict()
        errors = validate(new)
        if errors:
            return render_template(
                'users/edit.html',
                user=user,
                users=users,
                errors=errors,
                ), 422
        for i, data in users.items():
            if int(i) == int(id):
                data['nickname'] = new['nickname']
                data['email'] = new['email']
        response = make_response(redirect(url_for('get_users'), code=302))
        response.set_cookie('users', json.dumps(users))
        flash('User has been updated', 'success')
        return response


@app.route('/users/<id>/delete', methods=['POST'])
def delete_user(id):
    users = request.cookies.get('users')
    users = literal_eval(users)
    users.pop(id)
    response = make_response(redirect(url_for('get_users'), code=302))
    response.set_cookie('users', json.dumps(users))
    flash('User has been deleted', 'success')
    return response


@app.route('/session/new', methods=['GET', 'POST'])
def new_session():
    users = request.cookies.get('users')
    users = literal_eval(users)
    user = {'email': ''}

    if request.method == 'GET':
        return render_template(
            'users/new_session.html',
            user=user,
            )

    if request.method == 'POST':
        user = request.form.to_dict()
        for _, data in users.items():
            if data['email'] == user['email']:
                session['user'] = data
                return redirect(url_for('get_users'))
            else:
                flash('Wrong email')
                return redirect(url_for('get_users'))


@app.route('/session/delete', methods=['POST', 'DELETE'])
def delete_session():
    session.pop('user')
    return redirect(url_for('get_users'))
