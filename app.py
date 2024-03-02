from api import api_bp
from flask_socketio import emit
from extensions import app, socketio, db
from models import User
from routes import progress
from flask_login import LoginManager

app.register_blueprint(api_bp)
app.register_blueprint(progress)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@socketio.on('new_task_notification')
def handle_new_task_notification(data):
    project_id = data['project_id']
    project_name = data['project_name']
    emit('new_task_notification', {'project_id': project_id, 'project_name': project_name}, broadcast=True)


@socketio.on('new_comment_notification')
def handle_new_comment_notification(data):
    task_id = data['task_id']
    task_title = data['task_title']
    emit('new_comment_notification', {'task_id': task_id, 'task_title': task_title}, broadcast=True)


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    socketio.run(app, debug=True)

