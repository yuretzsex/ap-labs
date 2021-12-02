from flask import Blueprint, Response, request, jsonify
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt
from datetime import datetime
from models import Note, NoteEditorRelaiton, NoteTagRelation, Tag, User, Edit, Stats
from models import session
from validation_schemas import NoteSchema, EditSchema

note = Blueprint('note', __name__)
bcrypt = Bcrypt()

session = session()


@note.route('/api/v1/note', methods=['POST'])
def create_note():
    data = request.get_json(force=True)
    try:
        NoteSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 405
    exists = session.query(Tag).filter_by(id=data['tag']).first()
    if not exists:
        return Response(status=404, response='Tag with that Id does not exist')
    exists = session.query(User).filter_by(id=data['editor']).first()
    if not exists:
        return Response(status=404, response='User with that Id does not exist')
    newNote = Note(header=data['header'], text=data['text'])
    session.add(newNote)
    session.commit()
    newNTR =NoteTagRelation(tag=data['tag'], note=newNote.id)
    session.add(newNTR)
    newNER = NoteEditorRelaiton(editor=data['tag'], note=newNote.id)
    userStat = session.query(Stats).filter_by(id=data['editor']).first()
    if not userStat:
        newStat = Stats(id=data['editor'],notes_created=1)
        session.add(newStat)
    else:
        userStat.notes_created +=1
    session.add(newNER)
    session.commit()
    session.close()

    return Response(response='New note was successfully created!')

@note.route('/api/v1/note/<noteId>', methods=['GET'])
def get_note(noteId):
    noteData = session.query(Note).filter_by(id=noteId).first()
    if not noteData:
        return Response(status=404, response='A note with provided id was not found.')
    if not int(noteId):
        return Response(status=400, response='Is not int')
    note_data = {'id': noteData.id, 'header': noteData.header, 'text': noteData.text}
    return jsonify({"note": note_data})

@note.route('/api/v1/note/<noteId>', methods=['PUT'])
def updateNote(noteId):
    data = request.get_json(force=True)

    try:
        EditSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 405

    noteData = session.query(Note).filter_by(id=noteId).first()
    if not noteData:
        return Response(status=404, response='The note with provided ID was not found.')
    exist = session.query(User).filter_by(id=data['editor']).first()
    if not exist:
        return Response(status=404, response='Editor does not exist.')
    newEdit = Edit(note=noteId, editor=data['editor'], old_text=noteData.text, new_text=data['new_text'],when_created = datetime.now())
    if 'new_text' in data.keys():
        noteData.text = data['new_text']
    session.add(newEdit)
    session.commit()
    session.close()

    return Response(response='The note was updated.')

@note.route('/api/v1/note/<noteId>', methods=['DELETE'])
def deleteNote(noteId):
    noteData = session.query(Note).filter_by(id=noteId).first()
    if not noteData:
        return Response(status=404, response='The note with provided ID was not found.')
    session.delete(noteData)
    session.commit()
    session.close()
    return Response(response='The note was deleted.')