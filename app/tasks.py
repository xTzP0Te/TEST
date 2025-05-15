import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Task
from app.forms import TaskForm, EmptyForm
import requests

bp = Blueprint('tasks', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png','jpg','jpeg','gif','pdf','txt','doc','docx'}


@bp.route('/joke')
def joke():
    response = requests.get('https://official-joke-api.appspot.com/random_joke')
    if response.status_code == 200:
        data = response.json()
        setup = data.get('setup')
        punchline = data.get('punchline')
    else:
        setup = "Не удалось получить шутку"
        punchline = ""
    return render_template('joke.html', setup=setup, punchline=punchline)


@bp.route('/dashboard')
@login_required
def dashboard():
    tasks = Task.query.filter_by(owner=current_user).order_by(Task.timestamp.desc()).all()
    delete_form = EmptyForm()
    return render_template('dashboard.html', tasks=tasks, delete_form=delete_form)

@bp.route('/task/new', methods=['GET','POST'])
@login_required
def new_task():
    form = TaskForm()
    if form.validate_on_submit():
        filename = None
        if form.attachment.data:
            file = form.attachment.data
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
            else:
                flash('File type not allowed.')
                return redirect(request.url)
        task = Task(title=form.title.data,
                    description=form.description.data,
                    owner=current_user,
                    attachment=filename)
        db.session.add(task)
        db.session.commit()
        flash('Task created!')
        return redirect(url_for('tasks.dashboard'))
    return render_template('tasks.html', form=form)

@bp.route('/task/<int:id>', methods=['GET','POST'])
@login_required
def task_detail(id):
    task = Task.query.get_or_404(id)
    if task.owner != current_user:
        flash('Access denied.')
        return redirect(url_for('tasks.dashboard'))
    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        if form.attachment.data:
            file = form.attachment.data
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
                task.attachment = filename
        db.session.commit()
        flash('Task updated!')
        return redirect(url_for('tasks.task_detail', id=task.id))
    return render_template('task_detail.html', task=task, form=form)

@bp.route('/task/<int:id>/delete', methods=['POST'])
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    if task.owner != current_user:
        flash('Access denied.')
        return redirect(url_for('tasks.dashboard'))
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted')
    return redirect(url_for('tasks.dashboard'))

@bp.route('/task/<int:id>/complete', methods=['POST'])
@login_required
def complete_task(id):
    task = Task.query.get_or_404(id)
    if task.owner != current_user:
        flash('Access denied.')
        return redirect(url_for('tasks.dashboard'))
    task.completed = True
    db.session.commit()
    flash('Task marked as completed!')
    return redirect(url_for('tasks.dashboard'))

@bp.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
