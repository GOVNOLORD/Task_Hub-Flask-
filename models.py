from flask_login import UserMixin
from extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    manager = db.relationship('User', backref='projects', lazy=True)
    participants = db.relationship('User', secondary='project_participants', backref='participant_project',
                                   lazy='dynamic')


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user_id'))
    assigned_user = db.relationship('User', backref='task_assigned', lazy=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project_id'), nullable=False)
    project = db.relationship('Project', backref='tasks', lazy=True)
    comments = db.relationship('Comment', backref='task', lazy=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task_id'), nullable=False)


project_participants = db.Table('project_participants',
                                db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                                db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True)
                                )
