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


@bp.route('/view', methods=['GET'])
@login_required
def view():
    db = get_db()
    categories = db.execute('SELECT * FROM category').fetchall()
    return render_template('quiz/category_user.html', categories=categories)


@bp.route('/view/<int:category_id>', methods=['GET', 'POST'])
@login_required
def view_category(category_id):
    db = get_db()
    category = db.execute(
        'SELECT * FROM category WHERE id = ?', (category_id,)
    ).fetchone()

    questions_data = db.execute(
        'SELECT q.id AS question_id, q.question_text, a.id AS answer_id, a.answer_text '
        'FROM question q '
        'JOIN answer a ON q.id = a.question_id '
        'WHERE q.category_id = ?',
        (category_id,)
    ).fetchall()

    questions = {}
    for row in questions_data:
        q_id = row['question_id']
        if q_id not in questions:
            questions[q_id] = {
                'id': q_id,
                'question_text': row['question_text'],
                'answers': []
            }
        questions[q_id]['answers'].append({
            'id': row['answer_id'],
            'answer_text': row['answer_text']
        })

    questions = list(questions.values())

    if category is None:
        flash('Category not found.', 'error')
        return redirect(url_for('category.view'))

    if request.method == 'POST':
        selected_answers = []
        for question in questions:
            answer_id = request.form.get(f'question_{question["id"]}')
            if answer_id:
                selected_answers.append(answer_id)

        if not selected_answers:
            flash('Please answer all questions.', 'error')
            return redirect(url_for('category.view_category', category_id=category_id))

        correct_answers = db.execute(
            'SELECT a.id FROM answer a '
            'JOIN question q ON a.question_id = q.id '
            'WHERE q.category_id = ? AND a.is_correct = 1',
            (category_id,)
        ).fetchall()

        correct_answer_ids = {str(answer['id']) for answer in correct_answers}
        score = sum(1 for answer_id in selected_answers if answer_id in correct_answer_ids)
        total_questions = len(questions)

        return render_template(
            'quiz/quiz_result.html',
            score=score,
            total_questions=total_questions,
            category=category
        )

    return render_template('quiz/category_detail.html', category=category, questions=questions)


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
                    'INSERT INTO question (category_id, question_text) VALUES (?, ?)',
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
