# backend/blueprints/goals.py
from flask import Blueprint, request, jsonify, session, redirect
from extensions import db
from models import Goal, User

goals_bp = Blueprint('goals', __name__)

def require_user_redirect():
    if not session.get('user_id'):
        return redirect('/login.html')

# Create a goal (form)
@goals_bp.route('/create_form', methods=['POST'])
def create_goal_form():
    if not session.get('user_id'):
        return redirect('/login.html')
    user_id = session['user_id']
    title = request.form.get('title')
    description = request.form.get('description')
    if not title:
        return redirect('/goals.html?error=title')
    goal = Goal(title=title, description=description, user_id=user_id)
    db.session.add(goal)
    db.session.commit()
    return redirect('/goals.html?msg=created')

# JSON API: Create (requires session)
@goals_bp.route('/', methods=['POST'])
def create_goal_api():
    if not session.get('user_id'):
        return jsonify({'message': 'not authenticated'}), 401
    user_id = session['user_id']
    data = request.get_json() or {}
    title = data.get('title')
    description = data.get('description')
    if not title:
        return jsonify({'message': 'title required'}), 400
    goal = Goal(title=title, description=description, user_id=user_id)
    db.session.add(goal)
    db.session.commit()
    return jsonify({'id': goal.id, 'title': goal.title, 'description': goal.description}), 201

# List goals (JSON)
@goals_bp.route('/', methods=['GET'])
def list_goals():
    if not session.get('user_id'):
        return jsonify([]), 200
    user_id = session['user_id']
    goals = Goal.query.filter_by(user_id=user_id).all()
    return jsonify([{'id': g.id, 'title': g.title, 'description': g.description} for g in goals])

# Get single goal
@goals_bp.route('/<int:goal_id>', methods=['GET'])
def get_goal(goal_id):
    if not session.get('user_id'):
        return jsonify({'message': 'not authenticated'}), 401
    user_id = session['user_id']
    goal = Goal.query.filter_by(id=goal_id, user_id=user_id).first()
    if not goal:
        return jsonify({'message': 'not found'}), 404
    return jsonify({'id': goal.id, 'title': goal.title, 'description': goal.description})

# Update goal (form)
@goals_bp.route('/<int:goal_id>/update_form', methods=['POST'])
def update_goal_form(goal_id):
    if not session.get('user_id'):
        return redirect('/login.html')
    user_id = session['user_id']
    goal = Goal.query.filter_by(id=goal_id, user_id=user_id).first()
    if not goal:
        return redirect('/goals.html?error=notfound')
    goal.title = request.form.get('title', goal.title)
    goal.description = request.form.get('description', goal.description)
    db.session.commit()
    return redirect('/goals.html?msg=updated')

# Delete (form)
@goals_bp.route('/<int:goal_id>/delete', methods=['POST'])
def delete_goal_form(goal_id):
    if not session.get('user_id'):
        return redirect('/login.html')
    user_id = session['user_id']
    goal = Goal.query.filter_by(id=goal_id, user_id=user_id).first()
    if not goal:
        return redirect('/goals.html?error=notfound')
    db.session.delete(goal)
    db.session.commit()
    return redirect('/goals.html?msg=deleted')
