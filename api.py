from flask import Blueprint, jsonify
from flask_restful import Api, Resource
from flask_login import login_required
from models import Project, Task

api_bp = Blueprint('api', __name__)
api = Api(api_bp)


class ProjectResource(Resource):
    @login_required
    def get(self, project_id):
        project = Project.query.get_or_404(project_id)
        return jsonify({'id': project.id, 'name': project.name, 'description': project.description})


class TaskResource(Resource):
    @login_required
    def get(self, task_id):
        task = Task.query.get_or_404(task_id)
        return jsonify({'id': task.id, 'title': task.title, 'description': task.description})


api.add_resource(ProjectResource, '/api/projects/<int:project_id>')
api.add_resource(TaskResource, '/api/tasks/<int:task_id>')