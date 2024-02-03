from api import api_bp
from flask_principal import Permission, RoleNeed
from flask_socketio import emit
from extensions import app, login_manager, socketio
from models import User

app.register_blueprint(api_bp)

admin_permission = Permission(RoleNeed('admin'))
project_manager_permission = Permission(RoleNeed('project_manager'))
project_member_permission = Permission(RoleNeed('project_member'))


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


if __name__ == '__main__':
    socketio.run(app, debug=True)
