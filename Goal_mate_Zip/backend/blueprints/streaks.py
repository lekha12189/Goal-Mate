# backend/blueprints/streaks.py
from flask import Blueprint, session, jsonify, redirect
from extensions import db
from models import Streak

streaks_bp = Blueprint('streaks', __name__)

@streaks_bp.route('/', methods=['GET'])
def get_streak():
    user_id = session.get('user_id')
    if not user_id:
        # not logged in - return default zeros
        return jsonify({'current_count': 0, 'last_date': None})
    streak = Streak.query.filter_by(user_id=user_id).first()
    if not streak:
        return jsonify({'current_count': 0, 'last_date': None})
    return jsonify({'current_count': streak.current_count, 'last_date': streak.last_date.isoformat() if streak.last_date else None})
