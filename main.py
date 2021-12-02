from flask import Flask, Response

from user import user
from note import note
from history import history

app = Flask(__name__)
app.register_blueprint(user)
app.register_blueprint(note)
app.register_blueprint(history)

@app.route('/api/v1/hello-world-2')
def hello_world():
    return 'Hello World 2'