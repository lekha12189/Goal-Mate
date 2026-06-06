from flask import request, jsonify
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import TimelineEntry, Goal
from . import api

timeline_bp = Blueprint('timeline', __name__)


@timeline_bp.route('/goals/<int:goal_id>/timeline', methods=['POST'])
@jwt_required()
def add_timeline_entry(goal_id):
	user_id = get_jwt_identity()
	goal = Goal.query.filter_by(id=goal_id, user_id=user_id).first()
	if not goal:
		return jsonify({'message': 'goal not found'}), 404
	data = request.get_json() or {}
	content = data.get('content')
	if not content:
		return jsonify({'message': 'content required'}), 400
	entry = TimelineEntry(goal_id=goal_id, content=content)
	db.session.add(entry)
	db.session.commit()
	return jsonify({'id': entry.id, 'content': entry.content, 'created_at': entry.created_at.isoformat()}), 201




@timeline_bp.route('/goals/<int:goal_id>/timeline', methods=['GET'])
@jwt_required()
def list_timeline(goal_id):
	user_id = get_jwt_identity()
	goal = Goal.query.filter_by(id=goal_id, user_id=user_id).first()
	if not goal:
		return jsonify({'message': 'goal not found'}), 404
	entries = TimelineEntry.query.filter_by(goal_id=goal_id).order_by(TimelineEntry.created_at.desc()).all()
	return jsonify([{'id': e.id, 'content': e.content, 'created_at': e.created_at.isoformat()} for e in entries])