from flask import Blueprint, Response, request, jsonify
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt
from models import User, Stats, NoteEditorRelaiton as NER, Note
from models import session
from validation_schemas import UserSchema
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

user = Blueprint("user", __name__)
bcrypt = Bcrypt()

session = session()


@user.route("/api/v1/user", methods=["POST"])
def register():
    data = request.get_json(force=True)

    try:
        UserSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 405

    exists = session.query(User).filter_by(username=data["username"]).first()
    if exists:
        return Response(status=400, response="User with such username already exists.")

    exists = session.query(User).filter_by(phone=data["phone"]).first()
    if exists:
        return Response(status=400, response="User with such phone already exists.")

    exists = session.query(User).filter_by(email=data["email"]).first()
    if exists:
        return Response(status=400, response="User with such email already exists.")

    hashed_password = bcrypt.generate_password_hash(data["password"])
    new_user = User(
        username=data["username"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        password=hashed_password,
        email=data["email"],
        phone=data["phone"],
    )

    session.add(new_user)
    session.commit()
    session.close()

    return Response(response="New user was successfully created!")


@user.route("/api/v1/user", methods=["PUT"])
@jwt_required()
def update_user():
    logged = get_jwt_identity()
    user = session.query(User).filter_by(username=logged).first()
    if not user:
        return Response(status=401, response="You are not allowed to do that")
    data = request.get_json(force=True)
    try:
        UserSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 405
    userData = session.query(User).filter_by(id=user.id).first()
    if not userData:
        return Response(status=404, response="A user with provided ID was not found.")
    if "username" in data.keys():
        exists = session.query(User).filter_by(username=data["username"]).first()
        if exists:
            return Response(status=400, response="User with such username already exists.")
        userData.username = data["username"]
    if "firstName" in data.keys():
        userData.first_name = data["firstName"]
    if "lastName" in data.keys():
        userData.last_name = data["lastName"]
    if "password" in data.keys():
        hashed_password = bcrypt.generate_password_hash(data["password"])
        userData.password = hashed_password
    if "email" in data.keys():
        exists = session.query(User).filter_by(email=data["email"]).first()
        if exists:
            return Response(status=400, response="User with such email already exists.")
        userData.email = data["email"]
    if "phone" in data.keys():
        exists = session.query(User).filter_by(phone=data["phone"]).first()
        if exists:
            return Response(status=400, response="User with such phone already exists.")
        userData.phone = data["phone"]

    session.commit()
    session.close()
    return Response(response="User has been updated")


@user.route("/api/v1/user", methods=["DELETE"])
@jwt_required()
def delete_user():
    logged = get_jwt_identity()
    user = session.query(User).filter_by(username=logged).first()
    if not user:
        return Response(status=401, response="You are not allowed to do that")
    userData = session.query(User).filter_by(id=user.id).first()
    existSt = session.query(Stats).filter_by(id=user.id).first()
    existNER = session.query(NER).filter_by(editor=user.id).first()
    if not userData:
        return Response(status=404, response="A user with provided ID was not found.")
    session.delete(userData)
    session.commit()
    session.close()
    return Response(response="User was deleted.")


@user.route("/api/v1/user/<username>", methods=["GET"])
def get_user(username):
    userData = session.query(User).filter_by(username=username).first()
    if not userData:
        return Response(status=404, response="A user with provided username was not found.")
    if not str(username):
        return Response(status=400, response="Is not string")
    user_data = {
        "id": userData.id,
        "username": userData.username,
        "firstName": userData.first_name,
        "lastName": userData.last_name,
        "email": userData.email,
        "phone": userData.phone,
    }
    return jsonify({"user": user_data})


@user.route("/api/v1/user/<username>/stats", methods=["GET"])
@jwt_required()
def get_user_stats(username):
    logged = get_jwt_identity()
    user = session.query(User).filter_by(username=logged).first()
    if not user:
        return Response(status=401, response="You are not allowed to do that")
    userData = session.query(User).filter_by(username=username).first()
    if not userData:
        return Response(status=404, response="A user with provided username was not found.")
    if not str(username):
        return Response(status=400, response="Is not string")
    userStats = session.query(Stats).filter_by(id=userData.id).first()
    if not userStats:
        stats = {"notes_created": 0}
    else:
        stats = {"notes_created": userStats.notes_created}
    return jsonify({"stats": stats})


@user.route("/api/v1/user/<username>/notes", methods=["GET"])
@jwt_required()
def get_user_notes(username):
    logged = get_jwt_identity()
    user = session.query(User).filter_by(username=logged).first()
    if not user:
        return Response(status=401, response="You are not allowed to do that")
    userData = session.query(User).filter_by(username=username).first()
    if not userData:
        return Response(status=404, response="A user with provided username was not found.")
    if not str(username):
        return Response(status=400, response="Is not string")
    noteIds = session.query(NER).filter_by(editor=userData.id)
    if not noteIds:
        return Response(response="This user has not created a single note yet")
    output = []
    for i in noteIds:
        temp = session.query(Note).filter_by(id=i.note).first()
        output.append({"id": temp.id, "header": temp.header, "text": temp.text})
    return jsonify({"notes": output})