from flask import Blueprint, render_template, request, redirect, url_for
from services.task_service import *

task_bp = Blueprint('tasks', __name__)

@task_bp.route('/')
def index():
    query = request.args.get('q')
    tasks = get_tasks(query)
    return render_template('index.html', tasks=tasks)

@task_bp.route('/add', methods=['POST'])
def add():
    add_task(request.form['title'], request.form['description'])
    return redirect(url_for('tasks.index'))

@task_bp.route('/delete/<task_id>')
def delete(task_id):
    delete_task(task_id)
    return redirect(url_for('tasks.index'))

@task_bp.route('/edit/<task_id>', methods=['GET', 'POST'])
def edit(task_id):
    task = get_task(task_id)

    if request.method == 'POST':
        update_task(
            task_id,
            request.form['title'],
            request.form['description'],
            request.form['status']
        )
        return redirect(url_for('tasks.index'))

    return render_template('edit.html', task=task)
