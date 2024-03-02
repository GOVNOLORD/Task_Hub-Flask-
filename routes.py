from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from extensions import db, app
from models import Project, Task, User
from permissions import project_manager_permission, admin_permission

progress = Blueprint('progress', __name__)


@progress.route('/task/<int:task_id>')
@login_required
@project_manager_permission.require(http_exception=403)
def view_task(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template('view_task.html', task=task)


@app.route('/create_project', methods=['GET', 'POST'])
@login_required
def create_project():
    if request.method == 'POST':
        project_name = request.form['project_name']
        new_project = Project(name=project_name, manager=current_user)
        db.session.add(new_project)
        db.session.commit()
        flash('New project created successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('create_project.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        new_user = User(username=username, password=password, role=role)
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
        user = User.query.filter_by(username=username).first()
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
    projects = Project.query.all()
    return render_template('dashboard.html', projects=projects)


@app.route('/admin')
@admin_permission.require(http_exception=403)
@login_required
def admin():
    return render_template('admin.html')


@app.route('/project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def project_page(project_id):
    project = Project.query.get_or_404(project_id)
    tasks = Task.query.filter_by(project_id=project_id).all()
    if request.method == 'POST':
        new_description = request.form['description']
        project.description = new_description
        db.session.commit()
        flash('Project description has been updated', 'success')
        return redirect(url_for('project_page', project_id=project_id))
    return render_template('project_page.html', project=project, project_id=project_id, tasks=tasks)


@app.route('/create_task/<int:project_id>', methods=['GET', 'POST'])
@login_required
def create_task(project_id):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        deadline = request.form['deadline']

        new_task = Task(title=title, description=description, deadline=deadline, project_id=project_id)

        db.session.add(new_task)
        db.session.commit()

        flash('Task created successfully!', 'success')

        return redirect(url_for('project_page', project_id=project_id))
    else:
        return render_template('create_task.html', project_id=project_id)


@app.route('/view_task/<int:task_id>')
@login_required
def view_task(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template('view_task.html', task=task)
