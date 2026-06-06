from flask import Blueprint, request, jsonify, session, redirect
from extensions import db
from models import User, Streak
from datetime import date, timedelta

auth_bp = Blueprint('auth', __name__)

# JSON API: signup
@auth_bp.route('/signup', methods=['POST'])
def signup_api():
    data = request.get_json() or {}
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if not (name and email and password):
        return jsonify({'message': 'name, email and password required'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'email already registered'}), 400
    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    # create empty streak record
    streak = Streak(user_id=user.id, current_count=0, last_date=None)
    db.session.add(streak)
    db.session.commit()
    return jsonify({'message': 'user created'}), 201

# form-based signup (redirects to login page on success)
@auth_bp.route('/signup_form', methods=['POST'])
def signup_form():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    if not (name and email and password):
        return redirect('/signup.html?error=missing')
    if User.query.filter_by(email=email).first():
        return redirect('/signup.html?error=exists')
    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    streak = Streak(user_id=user.id, current_count=0, last_date=None)
    db.session.add(streak)
    db.session.commit()
    # after signup, redirect to login page
    return redirect('/login.html?msg=created')

# form-based login (sets session and redirects)
@auth_bp.route('/login_form', methods=['POST'])
def login_form():
    email = request.form.get('email')
    password = request.form.get('password')
    print(f"Login attempt: email={email}, password={'***' if password else None}")
    if not (email and password):
        print("Missing credentials")
        return redirect('/login.html?error=missing')
    user = User.query.filter_by(email=email).first()
    if not user:
        print("User not found")
        return redirect('/signup.html?error=no_user')
    if not user.check_password(password):
        print("Bad credentials")
        return redirect('/login.html?error=bad_credentials')
    session['user_id'] = user.id
    session['user_name'] = user.name
    print(f"User {user.email} logged in successfully")

    # update streak logic
    streak = Streak.query.filter_by(user_id=user.id).first()
    today = date.today()
    if not streak:
        streak = Streak(user_id=user.id, current_count=1, last_date=today)
        db.session.add(streak)
        db.session.commit()
    else:
        if streak.last_date == today:
            pass
        elif streak.last_date == (today - timedelta(days=1)):
            streak.current_count += 1
            streak.last_date = today
            db.session.commit()
        else:
            streak.current_count = 1
            streak.last_date = today
            db.session.commit()

    return redirect('/')

# logout route
@auth_bp.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect('/login.html')
