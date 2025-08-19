from app.user.controllers import users
from app.calender.controllers import calendar
from app.chat.controllers import chat


def register_routes(app):
    app.register_blueprint(users)
    app.register_blueprint(calendar)
    app.register_blueprint(chat, url_prefix="/api/chat")
