from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Task
from app.forms import TaskForm
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
import os
from flask import current_app
from werkzeug.utils import secure_filename

bp = Blueprint('tasks', __name__)
upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')

if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'doc', 'docx'}


@bp.route('/dashboard')
@login_required
def dashboard():
    tasks = Task.query.filter_by(owner=current_user).order_by(Task.timestamp.desc()).all()
    from app.forms import EmptyForm
    delete_form = EmptyForm()
    return render_template('dashboard.html', tasks=tasks, delete_form=delete_form)


@bp.route('/task/new', methods=['GET', 'POST'])
@login_required
def new_task():
    form = TaskForm()
    if form.validate_on_submit():
        filename = None
        if form.attachment.data:
            file = form.attachment.data
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Определяем путь к папке загрузки внутри функции
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                # Создаем папку, если она не существует
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
            else:
                flash('Недопустимый тип файла.')
                return redirect(request.url)
        task = Task(title=form.title.data,
                    description=form.description.data,
                    owner=current_user,
                    attachment=filename)
        db.session.add(task)
        db.session.commit()
        flash('Задача создана!')
        return redirect(url_for('tasks.dashboard'))
    return render_template('tasks.html', form=form)


@bp.route('/task/<int:id>', methods=['GET', 'POST'])
@login_required
def task_detail(id):
    task = Task.query.get_or_404(id)
    if task.owner != current_user:
        flash('Access denied.')
        return redirect(url_for('tasks.dashboard'))
    form = TaskForm(obj=task)
    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        if form.attachment.data:
            file = form.attachment.data
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
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


@bp.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

