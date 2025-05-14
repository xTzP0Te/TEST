from flask import render_template, redirect, url_for, flash
from app import db
from app.projects import bp
from flask_login import login_required, current_user
from app.forms import ProjectForm
from app.models import Project


@bp.route('/projects')
@login_required
def index():
    projects = Project.query.filter_by(owner_id=current_user.id).all()
    return render_template('projects/index.html', projects=projects)


@bp.route('/projects/create', methods=['GET', 'POST'])
@login_required
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(name=form.name.data,
                          description=form.description.data,
                          owner_id=current_user.id)
        db.session.add(project)
        db.session.commit()
        flash('Проект успешно создан!', 'success')
        return redirect(url_for('projects.index'))
    return render_template('projects/create.html', form=form)


@bp.route('/projects/<int:project_id>')
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    if project.owner_id != current_user.id:
        flash('Вы не имеете доступа к этому проекту.', 'danger')
        return redirect(url_for('projects.index'))
    return render_template('projects/project_detail.html', project=project)


@bp.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.owner_id != current_user.id:
        flash('Вы не имеете доступа к этому проекту.', 'danger')
        return redirect(url_for('projects.index'))

    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        project.name = form.name.data
        project.description = form.description.data
        db.session.commit()
        flash('Проект обновлён!', 'success')
        return redirect(url_for('projects.project_detail', project_id=project.id))

    return render_template('projects/edit.html', form=form, project=project)
