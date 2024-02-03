from flask import render_template, redirect, url_for, flash, request
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
from app import project_manager_permission, admin_permission, project_member_permission
from extensions import db, app, socketio


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
