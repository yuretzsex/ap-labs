from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Table, MetaData, create_engine, insert

base = declarative_base()
engine = create_engine('mysql://root:54E678w123E@localhost/notes_db', echo=False)
session = sessionmaker(bind=engine)
s = session()



class NoteEditorRelaiton(base):
    __tablename__ = 'note_editor'
    note = Column(Integer, ForeignKey('notes.id',ondelete='CASCADE'), primary_key=True)
    editor = Column(Integer, ForeignKey('users.id',ondelete='CASCADE'), primary_key=True)

class NoteTagRelation(base):
    __tablename__ = 'note_tag'
    note = Column(Integer, ForeignKey('notes.id',ondelete='CASCADE'), primary_key=True)
    tag = Column(Integer, ForeignKey('tags.id',ondelete='CASCADE'), primary_key=True)

class Edit(base):
    __tablename__ = 'edits'
    id = Column(Integer, primary_key = True)
    note = Column(Integer, ForeignKey('notes.id', ondelete='CASCADE'))
    editor = Column(Integer, ForeignKey('users.id',ondelete='CASCADE'))
    old_text = Column(String(150))
    new_text = Column(String(150))
    when_created = Column(DateTime)

    def __repr__(self):
        return f"<edits {self.id}>"

class User(base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    first_name = Column(String(30))
    last_name = Column(String(30))
    email = Column(String(30), unique=True)
    password = Column(String(15))
    phone = Column(String(15), unique=True)

    def __str__(self):
        return f"fName = {self.first_name}\n" \
               f"lName = {self.last_name}\n" \
               f"email = {self.email}\n " \
               f"phone = {self.phone}"

    def __repr__(self):
        return f"<users {self.id}>"

class Note(base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key = True)
    header = Column(String(30))
    text = Column(String(30))

    def __repr__(self):
        return f"<notes {self.id}>"

class Stats(base):
    __tablename__ = 'stats'
    id = Column(Integer, ForeignKey('users.id',ondelete='CASCADE'), primary_key=True)
    notes_created = Column(Integer)

class Tag(base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key = True)
    name = Column(String(30))

    def __repr__(self):
        return f"<tags {self.id}>"


user = User(id=1, first_name="Ivan", last_name="Franko",
           email="plfdfde@ex.com", password="7548Rfd8f3", phone="+380682312364")
note = Note(id=1,header='Header',text='A note')
tag = Tag(id=1, name='homework')
edit = Edit(id=1,note=1,editor=1,old_text="An old text",new_text="A new text",when_created=datetime.utcnow())
note2 = Note(id=2,header='fdfd',text='fdkfdkl')
user2 = User(id=2, first_name="Ivan", last_name="Franko",
           email="plfdfasdffde@ex.com", password="7548Rfd8f3", phone="+380681292364")



s.add(user)
s.add(user2)
s.add(note)
s.add(note2)
s.add(tag)
s.commit()

stats = Stats(id=1,notes_created=3)
note_editor = NoteEditorRelaiton(note=1,editor=1)
note_editor2 = NoteEditorRelaiton(note=1,editor=2)
note_editor3 = NoteEditorRelaiton(note=2,editor=2)
note_tag = NoteTagRelation(note=1,tag=1)

s.add(edit)
s.add(stats)
s.add(note_editor)
s.add(note_editor2)
s.add(note_editor3)
s.add(note_tag)


s.commit()

#print(s.query(User).all()[0])

