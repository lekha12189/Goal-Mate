from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, send_from_directory, redirect, session
from config import Config
from extensions import db, migrate, jwt, cors

from blueprints.auth import auth_bp
from blueprints.goals import goals_bp
from blueprints.timeline import timeline_bp
from blueprints.rooms import rooms_bp
from blueprints.streaks import streaks_bp

from flask_socketio import SocketIO, join_room, leave_room, emit

def create_app():
    app = Flask(__name__, static_folder='frontend', static_url_path='')
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(goals_bp, url_prefix="/api/goals")
    app.register_blueprint(timeline_bp, url_prefix="/api/timeline")
    app.register_blueprint(rooms_bp, url_prefix="/api/rooms")
    app.register_blueprint(streaks_bp, url_prefix="/api/streaks")

    socketio = SocketIO(app, cors_allowed_origins="*")

    @app.route('/')
    def home():
        if session.get('user_id'):
            return send_from_directory(app.static_folder, 'index.html')
        else:
            return redirect('/login.html')

    @app.route('/<path:path>')
    def static_proxy(path):
        if path.startswith('socket.io/'):
            # Let Flask-SocketIO serve this
            return '', 404
        file_path = os.path.join(app.static_folder, path)
        if os.path.exists(file_path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')


    # Socket.IO events

    @socketio.on('join_room')
    def handle_join(data):
        room = data['room']
        join_room(room)
        emit('user_joined', {'msg': f"{session.get('user_name')} joined the room."}, room=room)

    @socketio.on('leave_room')
    def handle_leave(data):
        room = data['room']
        leave_room(room)
        emit('user_left', {'msg': f"{session.get('user_name')} left the room."}, room=room)

    @socketio.on('send_message')
    def handle_message(data):
        room = data['room']
        msg = data['message']
        user = session.get('user_name') or 'Anonymous'
        emit('receive_message', {'user': user, 'message': msg}, room=room)

    @socketio.on('send_code')
    def handle_code(data):
        room = data['room']
        code = data['code']
        emit('receive_code', {'code': code}, room=room)

    @socketio.on('send_output')
    def handle_output(data):
        room = data['room']
        output = data['output']
        emit('receive_output', {'output': output}, room=room)

    @socketio.on('close_room')
    def handle_close_room(data):
        room_id = data['room_id']
        user_id = session.get('user_id')
        # Assuming you have access to app context and db here - you may move this to a blueprint route instead
        from models import Room, RoomMembership
        room = Room.query.get(room_id)
        if room and room.created_by == user_id:
            RoomMembership.query.filter_by(room_id=room.id).delete()
            db.session.delete(room)
            db.session.commit()
            emit('room_closed', {'room_id': room_id}, room=str(room_id))
        else:
            emit('error', {'msg': 'Unauthorized to close this room'})

    # Attach socketio to app for external usage
    app.socketio = socketio
    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    # Use socketio run here to enable websockets
    socketio = app.socketio
    socketio.run(app, debug=True)
