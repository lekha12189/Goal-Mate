from flask import Blueprint, request, jsonify, session, redirect
from extensions import db
from models import Room, RoomMembership

rooms_bp = Blueprint('rooms', __name__)

@rooms_bp.route('/create_form', methods=['POST'])
def create_room_form():
    if not session.get('user_id'):
        return redirect('/login.html')
    user_id = session['user_id']
    name = request.form.get('name')
    description = request.form.get('description')
    if not name:
        return redirect('/create_room.html?error=missing_name')
    existing = Room.query.filter_by(name=name).first()
    if existing:
        room = existing
    else:
        room = Room(name=name, description=description, created_by=user_id)
        db.session.add(room)
        db.session.commit()
    if not RoomMembership.query.filter_by(room_id=room.id, user_id=user_id).first():
        membership = RoomMembership(room_id=room.id, user_id=user_id)
        db.session.add(membership)
        db.session.commit()
    return redirect(f'/meet.html?room_id={room.id}&room_name={room.name}')

@rooms_bp.route('/join_form', methods=['POST'])
def join_room_form():
    if not session.get('user_id'):
        return redirect('/login.html')
    user_id = session['user_id']
    name = request.form.get('name')
    if not name:
        return redirect('/join.html?error=missing')
    room = Room.query.filter_by(name=name).first()
    if not room:
        return redirect('/join.html?error=notfound')
    if not RoomMembership.query.filter_by(room_id=room.id, user_id=user_id).first():
        membership = RoomMembership(room_id=room.id, user_id=user_id)
        db.session.add(membership)
        db.session.commit()
    return redirect(f'/meet.html?room_id={room.id}&room_name={room.name}')

@rooms_bp.route('/', methods=['GET'])
def list_rooms():
    rooms = Room.query.order_by(Room.created_at.desc()).all()
    return jsonify([{'id': r.id, 'name': r.name, 'description': r.description} for r in rooms])

@rooms_bp.route('/<int:room_id>', methods=['GET'])
def get_room(room_id):
    room = Room.query.get(room_id)
    if not room:
        return jsonify({'error': 'Room not found'}), 404
    return jsonify({
        'id': room.id,
        'name': room.name,
        'description': room.description,
        'created_by': room.created_by
    })

@rooms_bp.route('/close/<int:room_id>', methods=['POST'])
def close_room(room_id):
    user_id = session.get('user_id')
    room = Room.query.get(room_id)
    if not room:
        return jsonify({'error': 'Room not found'}), 404
    if room.created_by != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    # Delete memberships and room
    RoomMembership.query.filter_by(room_id=room_id).delete()
    db.session.delete(room)
    db.session.commit()
    return jsonify({'message': 'Room closed successfully'})
