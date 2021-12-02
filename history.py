from flask import Blueprint, Response, request, jsonify
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt
from models import Edit, Note
from models import session

history = Blueprint('history', __name__)
bcrypt = Bcrypt()

session = session()

@history.route('/api/v1/history/<noteId>', methods=['GET'])
def get_history(noteId):
    noteData = session.query(Note).filter_by(id = noteId).first()
    if not noteData:
        return Response(status=404, response='The note with provided id was not found.')
    if not int(noteId):
        return Response(status=400,response='Is not id')

    editIds = session.query(Edit).filter_by(note=noteData.id)
    note_data = {'id': noteData.id, 'header': noteData.header, 'text': noteData.text}
    if not editIds:
        return jsonify({"note": note_data})
    output = []
    output.append(note_data)
    for i in editIds:
        output.append({"id":i.id,"note":i.note,"old_text":i.old_text,
                       "new_text":i.new_text,"when_created":i.when_created})
    return jsonify({"edits": output})