from flask import Blueprint, Response, request, jsonify
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt
from models import User
from models import session
from validation_schemas import UserSchema, LoginSchema
from flask_jwt_extended import create_access_token
import datetime

login = Blueprint("login", __name__)
bcrypt = Bcrypt()

session = session()


@login.route("/login", methods=["GET"])
def logIn():
    data = request.get_json(force=True)
    try:
        LoginSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 405
    exist = session.query(User).filter_by(username=data["username"]).first()
    access_token = create_access_token(
        identity=data["username"], expires_delta=datetime.timedelta(days=365)
    )
    if exist and bcrypt.check_password_hash(exist.password, data["password"]):
        return jsonify({"access_token": access_token})
    else:
        return Response(status=404, response="Invalid username or password.")
