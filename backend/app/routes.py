from app.user.controllers import users
from app.calender.controllers import calendar


def register_routes(app):
    app.register_blueprint(users)
    app.register_blueprint(calendar)
