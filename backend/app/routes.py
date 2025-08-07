from app.user.controllers import users
from app.calendar.controllers import calendar


def register_routes(app):
    app.register_blueprint(calendar)
    app.register_blueprint(users)
