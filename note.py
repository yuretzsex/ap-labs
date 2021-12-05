from flask import Blueprint, Response, request, jsonify
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt
from datetime import datetime
from models import Note, NoteEditorRelaiton, NoteTagRelation, Tag, User, Edit, Stats
from models import session
from validation_schemas import NoteSchema, EditSchema, EditorsSchema
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

note = Blueprint("note", __name__)
bcrypt = Bcrypt()

session = session()


@note.route("/api/v1/note", methods=["POST"])
@jwt_required()
def create_note():
    logged = get_jwt_identity()
    user = session.query(User).filter_by(username=logged).first()
    if not user:
        return Response(status=401, response="You are not allowed to do that")
    data = request.get_json(force=True)
    try:
        NoteSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 405
    exists = session.query(Tag).filter_by(id=data["tag"]).first()
    if not exists:
        return Response(status=404, response="Tag with that Id does not exist")
    exists = session.query(User).filter_by(id=user.id).first()
    if not exists:
        return Response(status=404, response="User with that Id does not exist")
    newNote = Note(header=data["header"], text=data["text"])
    session.add(newNote)
    session.commit()
    newNTR = NoteTagRelation(tag=data["tag"], note=newNote.id)
    session.add(newNTR)
    newNER = NoteEditorRelaiton(editor=user.id, note=newNote.id)
    userStat = session.query(Stats).filter_by(id=user.id).first()
    if not userStat:
        newStat = Stats(id=user.id, notes_created=1)
        session.add(newStat)
    else:
        userStat.notes_created += 1
    session.add(newNER)
    session.commit()
    session.close()

    return Response(response="New note was successfully created!")


@note.route("/api/v1/note/<noteId>", methods=["GET"])
def get_note(noteId):
    noteData = session.query(Note).filter_by(id=noteId).first()
    if not noteData:
        return Response(status=404, response="A note with provided id was not found.")
    if not int(noteId):
        return Response(status=400, response="Is not int")
    note_data = {"id": noteData.id, "header": noteData.header, "text": noteData.text}
    return jsonify({"note": note_data})


@note.route("/api/v1/note/<noteId>", methods=["PUT"])
@jwt_required()
def updateNote(noteId):
    logged = get_jwt_identity()
    user = session.query(User).filter_by(username=logged).first()
    if not user:
        return Response(status=401, response="You are not allowed to do that")
    data = request.get_json(force=True)

    try:
        EditSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 405

    noteData = session.query(Note).filter_by(id=noteId).first()
    if not noteData:
        return Response(status=404, response="The note with provided ID was not found.")
    editors = session.query(NoteEditorRelaiton).filter_by(note=noteId)
    if not user.id in [e.editor for e in editors]:
        return Response(status=403, response="You can't edit this note.")
    newEdit = Edit(
        note=noteId,
        editor=user.id,
        old_text=noteData.text,
        new_text=data["new_text"],
        when_created=datetime.now(),
    )
    if "new_text" in data.keys():
        noteData.text = data["new_text"]
    session.add(newEdit)
    session.commit()
    session.close()

    return Response(response="The note was updated.")


@note.route("/api/v1/note/<noteId>", methods=["DELETE"])
@jwt_required()
def deleteNote(noteId):
    logged = get_jwt_identity()
    user = session.query(User).filter_by(username=logged).first()
    if not user:
        return Response(status=401, response="You are not allowed to do that")
    editors = session.query(NoteEditorRelaiton).filter_by(note=noteId)
    if not user.id in [e.editor for e in editors]:
        return Response(status=403, response="You can't delete this note.")
    noteData = session.query(Note).filter_by(id=noteId).first()
    if not noteData:
        return Response(status=404, response="The note with provided ID was not found.")
    session.delete(noteData)
    session.commit()
    session.close()
    return Response(response="The note was deleted.")


@note.route("/api/v1/note/acces/<noteId>", methods=["PUT"])
@jwt_required()
def giveAcces(noteId):
    logged = get_jwt_identity()
    user = session.query(User).filter_by(username=logged).first()
    if not user:
        return Response(status=401, response="You are not allowed to do that")
    data = request.get_json(force=True)
    try:
        EditorsSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    note = session.query(Note).filter_by(id=noteId).first()
    if not note:
        return Response(status=404, response="Note was not found")
    existedEditors = session.query(NoteEditorRelaiton).filter_by(note=noteId)
    if not user.id in [e.editor for e in existedEditors]:
        return Response(status=403, response="You can't add editors to this note.")
    if existedEditors.count() + len(data["editors"]) > 5:
        return Response(status=400, response="Cannot add more than 5 editors")

    if "editors" in data.keys():
        for editor in data["editors"]:
            ed = session.query(User).filter_by(id=editor).first()
            if not ed:
                return Response(status=404, response="Provided user data was not found")
            for i in existedEditors:
                if i.editor == ed.id:
                    return Response(status=400, response="User alredy has access")
            session.add(NoteEditorRelaiton(note=noteId, editor=ed.id))
            session.commit()
    session.close()
    return Response(response="Editors has been updated")
