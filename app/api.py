from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from app.models import Task
from app import db

bp = Blueprint('api', __name__)


@bp.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    tasks = Task.query.filter_by(owner=current_user).all()
    return jsonify([t.to_dict() for t in tasks])


@bp.route('/tasks/<int:id>', methods=['GET'])
@login_required
def get_task(id):
    task = Task.query.get_or_404(id)
    if task.owner != current_user:
        abort(403)
    return jsonify(task.to_dict())


@bp.route('/tasks', methods=['POST'])
@login_required
def create_task_api():
    data = request.get_json() or {}
    if 'title' not in data:
        abort(400)
    task = Task(title=data['title'],
                description=data.get('description', ''),
                owner=current_user)
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@bp.route('/tasks/<int:id>', methods=['PUT'])
@login_required
def update_task_api(id):
    task = Task.query.get_or_404(id)
    if task.owner != current_user:
        abort(403)
    data = request.get_json() or {}
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.completed = data.get('completed', task.completed)
    db.session.commit()
    return jsonify(task.to_dict())


@bp.route('/tasks/<int:id>', methods=['DELETE'])
@login_required
def delete_task_api(id):
    task = Task.query.get_or_404(id)
    if task.owner != current_user:
        abort(403)
    db.session.delete(task)
    db.session.commit()
    return '', 204