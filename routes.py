from flask import Blueprint, render_template
from flask_login import login_required
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from models import Project, Task
from app import project_member_permission

progress = Blueprint('progress', __name__)


@progress.route('/project_progress/<int:project_id>')
@login_required
@project_member_permission.require(http_exception=403)
def project_progress(project_id):
    project = Project.query.get_or_404(project_id)
    tasks = Task.query.filter_by(project=project).all()

    total_tasks = len(tasks)
    completed_tasks = len([task for task in tasks if task.is_completed])
    progress_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

    fig = make_subplots(rows=1, cols=1, specs=[[{'type': 'indicator'}]])
    fig.add_trace(go.Indicator(
        mode="number+gauge",
        value=progress_percentage,
        domain={'row': 0, 'col': 0},
        title={'text': f'Progress ({completed_tasks}/{total_tasks})'},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 25], 'color': "red"},
                {'range': [25, 50], 'color': "orange"},
                {'range': [50, 75], 'color': "yellow"},
                {'range': [75, 100], 'color': "green"},
            ],
        }
    ))

    graph_html = fig.to_html(full_html=False)
    return render_template('project_progress.html', project=project, graph_html=graph_html)
