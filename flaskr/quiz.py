from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, g, session
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

    if g.user['is_admin']:
        return redirect(url_for('category.manage_categories'))

    return render_template('quiz/category_user.html', categories=categories)


@bp.route('/manage_categories', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_categories():
    db = get_db()

    if request.method == 'POST':
        category_name = request.form['name']

        if not category_name:
            flash("Category name is required.", "error")
        else:
            try:
                db.execute('INSERT INTO category (name) VALUES (?)', (category_name,))
                db.commit()
                flash('Category added successfully!', 'success')
            except db.IntegrityError:
                flash("An error occurred. Please try again.", "error")

        return redirect(url_for('category.manage_categories'))

    categories = db.execute('SELECT * FROM category').fetchall()
    return render_template('quiz/category_admin.html', categories=categories)


@bp.route('/manage_category/<int:category_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_category(category_id):
    db = get_db()
    category = db.execute('SELECT * FROM category WHERE id = ?', (category_id,)).fetchone()

    questions_data = db.execute(
        'SELECT q.id AS question_id, q.question_text, a.id AS answer_id, a.answer_text, a.is_correct '
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
            'answer_text': row['answer_text'],
            'is_correct': row['is_correct']
        })
    questions = list(questions.values())

    if request.method == 'POST':
        question_text = request.form['question']
        answers = [
            request.form['answer1'],
            request.form['answer2'],
            request.form['answer3'],
            request.form['answer4']
        ]
        correct_answer = int(request.form['correct_answer']) - 1

        try:
            cursor = db.execute(
                'INSERT INTO question (category_id, question_text) VALUES (?, ?)',
                (category_id, question_text)
            )
            question_id = cursor.lastrowid

            for i, answer_text in enumerate(answers):
                db.execute(
                    'INSERT INTO answer (question_id, answer_text, is_correct) VALUES (?, ?, ?)',
                    (question_id, answer_text, 1 if i == correct_answer else 0)
                )

            db.commit()
            flash('New question added successfully!', 'success')

        except db.IntegrityError:
            flash("This question already exists in this category. Please enter a unique question.", "error")

        return redirect(url_for('category.manage_category', category_id=category_id))

    return render_template('quiz/manage_category.html', category=category, questions=questions)


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
        selected_answers = [request.form.get(f'question_{question["id"]}') for question in questions]
        correct_answers = db.execute(
            'SELECT a.id FROM answer a '
            'JOIN question q ON a.question_id = q.id '
            'WHERE q.category_id = ? AND a.is_correct = 1',
            (category_id,)
        ).fetchall()

        correct_answer_ids = {str(answer['id']) for answer in correct_answers}
        score = sum(1 for answer_id in selected_answers if answer_id in correct_answer_ids)
        total_questions = len(questions)

        db.execute(
            'INSERT INTO results (user_id, category_id, score, total_questions) VALUES (?, ?, ?, ?)',
            (g.user['id'], category_id, score, total_questions)
        )
        db.commit()

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


@bp.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_question(question_id):
    db = get_db()

    question = db.execute(
        'SELECT * FROM question WHERE id = ?', (question_id,)
    ).fetchone()

    answers = db.execute(
        'SELECT * FROM answer WHERE question_id = ?', (question_id,)
    ).fetchall()

    if request.method == 'POST':
        question_text = request.form['question']
        answer_texts = [
            request.form['answer1'],
            request.form['answer2'],
            request.form['answer3'],
            request.form['answer4']
        ]
        correct_answer = int(request.form['correct_answer']) - 1

        db.execute(
            'UPDATE question SET question_text = ? WHERE id = ?',
            (question_text, question_id)
        )

        for i, answer in enumerate(answers):
            db.execute(
                'UPDATE answer SET answer_text = ?, is_correct = ? WHERE id = ?',
                (answer_texts[i], 1 if i == correct_answer else 0, answer['id'])
            )

        db.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('category.manage_category', category_id=question['category_id']))

    return render_template(
        'quiz/edit_question.html',
        question=question,
        answers=answers
    )


@bp.route('/view_profile', methods=['GET', 'POST'])
@login_required
def view_profile():
    db = get_db()

    if request.method == 'POST':
        email = request.form['email']
        error = None

        if not email:
            error = 'Email is required.'

        if error is None:
            db.execute(
                'UPDATE user SET email = ? WHERE id = ?',
                (email, g.user['id'])
            )
            db.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile.view_profile'))

        flash(error, 'error')

    user = db.execute(
        'SELECT username, email FROM user WHERE id = ?',
        (g.user['id'],)
    ).fetchone()

    return render_template('profile/profile.html', user=user)


@bp.route('/select_num_questions/<int:category_id>', methods=['GET', 'POST'])
@login_required
def select_num_questions(category_id):
    if request.method == 'POST':
        num_questions = request.form.get('num_questions', type=int)
        return redirect(url_for('category.start_quiz', category_id=category_id, num_questions=num_questions))

    return render_template('quiz/question_select.html', category_id=category_id)


@bp.route('/start_quiz', methods=['GET'])
@login_required
def start_quiz():
    category_id = request.args.get('category_id', type=int)
    num_questions = request.args.get('num_questions', type=int)

    session['category_id'] = category_id

    db = get_db()
    questions = db.execute(
        'SELECT id, question_text FROM question '
        'WHERE category_id = ? '
        'ORDER BY RANDOM() '
        'LIMIT ?',
        (category_id, num_questions)
    ).fetchall()

    question_ids = [q['id'] for q in questions]

    answers_data = db.execute(
        'SELECT question_id, id AS answer_id, answer_text, is_correct FROM answer '
        'WHERE question_id IN ({})'.format(','.join(['?'] * len(question_ids))),
        question_ids
    ).fetchall()

    quiz_questions = {q['id']: {'id': q['id'], 'question_text': q['question_text'], 'answers': []} for q in questions}
    for answer in answers_data:
        question_id = answer['question_id']
        if question_id in quiz_questions:
            quiz_questions[question_id]['answers'].append({
                'id': answer['answer_id'],
                'answer_text': answer['answer_text']
            })

    session['quiz_questions'] = list(quiz_questions.values())

    return render_template('quiz/quiz_display.html', category_id=category_id, questions=session['quiz_questions'])


@bp.route('/display_quiz', methods=['GET', 'POST'])
@login_required
def display_quiz():
    if request.method == 'POST':
        return redirect(url_for('category.result'))

    quiz_questions = session.get('quiz_questions')
    return render_template('quiz/quiz_display.html', questions=quiz_questions)


@bp.route('/result', methods=['POST'])
@login_required
def quiz_result():
    db = get_db()
    quiz_questions = session.get('quiz_questions')
    score = 0
    total_questions = len(quiz_questions)

    for question in quiz_questions:
        question_id = question['id']
        user_answer = request.form.get(f'answer_{question_id}')
        correct_answer = db.execute(
            'SELECT id FROM answer WHERE question_id = ? AND is_correct = 1',
            (question_id,)
        ).fetchone()

        if correct_answer and user_answer and int(user_answer) == correct_answer['id']:
            score += 1

    db.execute(
        'INSERT INTO results (user_id, category_id, score, total_questions) VALUES (?, ?, ?, ?)',
        (g.user['id'], session['category_id'], score, total_questions)
    )
    db.commit()

    return render_template('quiz/quiz_result.html', score=score, total_questions=total_questions)


@bp.route('/delete_question/<int:category_id>/<int:question_id>', methods=['POST'])
@login_required
@admin_required
def delete_question(category_id, question_id):
    db = get_db()
    db.execute('DELETE FROM question WHERE id = ?', (question_id,))
    db.execute('DELETE FROM answer WHERE question_id = ?', (question_id,))
    db.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('category.manage_category', category_id=category_id))
