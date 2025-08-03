from flask import Blueprint, jsonify, request
from app.user.models import User
from app.extensions import db, bcrypt
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt,
    get_jwt_identity,
)
from app.extensions import blacklist
from sqlalchemy.exc import IntegrityError

users = Blueprint("users", __name__)


@users.route("/", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify(
        [{"id": user.id, "name": user.name, "email": user.email} for user in users]
    )


@users.route("/", methods=["POST"])
def create_user():
    data = request.get_json()
    user = User(name=data["name"], email=data["email"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"id": user.id, "name": user.name, "email": user.email}), 201


@users.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({"id": user.id, "name": user.name, "email": user.email})


@users.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "username taken"}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email taken"}), 409
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "database error"}), 500
    return jsonify({"msg": "signup succesful"}), 201


@users.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "invalid username or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify(
        {
            "message": "Login successful",
            "access_token": access_token,
            "user": {"id": user.id, "username": user.username},
        }
    ), 200


@users.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  # get the token ID
    blacklist.add(jti)  # mark it as revoked
    return jsonify({"msg": "Successfully logged out"}), 200


@users.route("/profile/<int:user_id>", methods=["GET"])
@jwt_required()
def get_profile(user_id):
    current_user_id = get_jwt_identity()
    if user_id != int(current_user_id):  # convert to int for correct comparison
        return jsonify({"msg": "unauthorized access"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify({"id": user.id, "username": user.username, "email": user.email}), 200
