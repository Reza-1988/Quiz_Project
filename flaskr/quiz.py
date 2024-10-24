from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)

from flaskr.auth import login_required, admin_required
from flaskr.db import get_db


bp = Blueprint('category', __name__)


@bp.route('/')
@login_required
def index():
    db = get_db()
    categories = db.execute(
        'SELECT id, name FROM category'
    ).fetchall()
    return render_template('quiz/index.html', categories=categories)


@bp.route('/add', methods=('GET', 'POST'))
@login_required
@admin_required
def add():
    if request.method == 'POST':
        name = request.form['name']
        error = None

        if not name:
            error = 'Category name is required.'

        if error is None:
            db = get_db()
            try:
                db.execute(
                    'INSERT INTO category (name) VALUES (?)',
                    (name,)
                )
                db.commit()
                flash('Category added successfully!', 'success')
                return redirect(url_for('category.add'))
            except db.IntegrityError:
                error = 'An error occurred while adding the category.'

        flash(error)

    return render_template('quiz/category_admin.html')


@bp.route('/view', methods=('GET', 'POST'))
@login_required
def view():
    if request.method == 'GET':
        db = get_db()
        categories = db.execute(
            'SELECT * FROM category'
        ).fetchall()

        return render_template('quiz/category_user.html', categories=categories)


@bp.route('/<int:category_id>/add_question', methods=('GET', 'POST'))
@login_required
@admin_required
def add_question(category_id):
    db = get_db()

    if request.method == 'POST':
        question_text = request.form['question']
        answers = [
            request.form['answer1'],
            request.form['answer2'],
            request.form['answer3'],
            request.form['answer4']
        ]
        correct_answer = request.form['correct_answer']
        error = None

        if not question_text:
            error = 'Question text is required.'
        elif not all(answers):
            error = 'All four answers are required.'
        elif correct_answer not in ['1', '2', '3', '4']:
            error = 'A valid correct answer must be selected.'

        if error is None:
            try:
                cursor = db.execute(
                    'INSERT INTO question (category_id, question) VALUES (?, ?)',
                    (category_id, question_text)
                )
                question_id = cursor.lastrowid

                for idx, answer in enumerate(answers, start=1):
                    db.execute(
                        'INSERT INTO answer (question_id, answer_text, is_correct) VALUES (?, ?, ?)',
                        (question_id, answer, 1 if str(idx) == correct_answer else 0)
                    )

                db.commit()
                flash('Question and answers added successfully!', 'success')
                return redirect(url_for('category.view'))
            except db.IntegrityError:
                error = 'An error occurred while adding the question.'

        flash(error)

    category = db.execute(
        'SELECT * FROM category WHERE id = ?',
        (category_id,)
    ).fetchone()

    return render_template('quiz/add_question.html', category=category)
