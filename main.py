from flask import Flask, Response

from login import login
from user import user
from note import note
from history import history
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:password@localhost/notes_db"
app.config["JWT_SECRET_KEY"] = "lvive"
jwt = JWTManager(app)
app.register_blueprint(login)
app.register_blueprint(user)
app.register_blueprint(note)
app.register_blueprint(history)


@app.route("/api/v1/hello-world-2")
def hello_world():
    return "Hello World 2"
