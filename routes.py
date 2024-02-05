from flask import Blueprint
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from models import Project, Task, User, Comment
from permissions import project_manager_permission, admin_permission, project_member_permission
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from extensions import db, app, socketio

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


@app.route('/create_task/<int:project_id>', methods=['GET', 'POST'])
@login_required
@project_member_permission.require(http_exception=403)
def create_task(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        deadline = request.form['deadline']
        assigned_to = request.form['assigned_to']

        new_task = Task(title=title, description=description, deadline=deadline, assigned_to=assigned_to,
                        project=project)
        db.session.add(new_task)
        db.session.commit()
        flash('New task created!', 'success')
        return redirect(url_for('project', project_id=project.id))

    socketio.emit('new_task_notification', {'project_id': project_id, 'project_name': project.name}, namespace='/')

    return redirect(url_for('project', project_id=project.id))


@app.route('/task/<int:task_id>')
@login_required
@project_manager_permission.require(http_exception=403)
def view_task(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template('view_task.html', task=task)


@app.route('/add_comment/<int:task_id>', methods=['POST'])
@login_required
@project_manager_permission.require(http_exception=403)
def add_comment(task_id):
    task = Task.query.get_or_404(task_id)
    text = request.form['comment_text']

    new_comment = Comment(text=text, task=task)
    db.session.add(new_comment)
    db.session.commit()

    flash('Comment added!', 'success')
    socketio.emit('new_task_notification', {'project_id': task.project.id, 'project_name': task.project.name},
                  namespace='/')
    return redirect(url_for('view_task', task_id=task.id))


@app.route('/create_project', methods=['GET', 'POST'])
@login_required
@project_manager_permission.require(http_exception=403)
def create_project():
    if request.method == 'POST':
        project_name = request.form['project_name']
        new_project = Project(name=project_name, manager=current_user)
        db.session.add(new_project)
        db.session.commit()
        flash('New project created successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('create_project.html')


@app.route('/manage_participants/<int:project_id>', methods=['GET', 'POST'])
@login_required
@project_manager_permission.require(http_exception=403)
def manage_participants(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        participant_username = request.form['participant_username']
        participant = User.query.filter_by(username=participant_username).first()

        if participant:
            project.participants.append(participant)
            db.session.commit()
            flash(f'Participant {participant_username} added to the project!', 'success')
        else:
            flash(f'User {participant_username} not found!', 'danger')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User.query.fillter_by(username=username, password=password).first()
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.fillter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check your username and password', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/admin')
@admin_permission.require(http_exception=403)
@login_required
def admin():
    return render_template('admin.html')
