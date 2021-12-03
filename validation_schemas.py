from marshmallow import Schema, fields
from marshmallow.validate import Length, Range


class UserSchema(Schema):
    username = fields.String(validate=Length(min=5))
    first_name = fields.String(validate=Length(min=3))
    last_name = fields.String(validate=Length(min=3))
    password = fields.String(validate=Length(min=8))
    email = fields.Email()
    phone = fields.Number()


class TagSchema(Schema):
    name = fields.String(validate=Length(min=3))

class NoteSchema(Schema):
    header = fields.String(validate=Length(min=3))
    text = fields.String(validate=Length(min=30))
    tag = fields.Integer()
    editor = fields.Integer()

class EditSchema(Schema):
    editor = fields.Integer()
    new_text = fields.String(validate=Length(min=30))

class StatsSchema(Schema):
    notes_created = fields.Integer()

class EditorsSchema(Schema):
    editors = fields.List(fields.Integer(),validate=Length(max=4))



