from flask import Blueprint


api = Blueprint('api', __name__)


from . import auth, goals, timeline, rooms, streaks # noqa: F401