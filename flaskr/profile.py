from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, g
)

from flaskr.auth import login_required
from flaskr.db import get_db


bp = Blueprint('profile', __name__, url_prefix='/profile')


@bp.route('/view', methods=['GET', 'POST'])
@login_required
def view_profile():
    db = get_db()

    if request.method == 'POST':
        email = request.form['email']
        last_name = request.form['last_name']
        username = request.form['username']

        error = None
        if not email:
            error = 'Email is required.'
        elif not username:
            error = 'Username is required.'

        user_with_username = db.execute(
            'SELECT id FROM user WHERE username = ? AND id != ?', (username, g.user['id'])
        ).fetchone()
        if user_with_username:
            error = 'Username is already taken.'

        if error:
            flash(error)
        else:
            db.execute(
                'UPDATE user SET email = ?, last_name = ?, username = ? WHERE id = ?',
                (email, last_name, username, g.user['id'])
            )
            db.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile.view_profile'))

    user = db.execute(
        'SELECT username, email, last_name FROM user WHERE id = ?', (g.user['id'],)
    ).fetchone()

    return render_template('profile/profile.html', user=user)


@bp.route('/feedback')
@login_required
def feedback():
    db = get_db()
    results = db.execute(
        'SELECT * FROM results WHERE user_id = ? ORDER BY completed_at DESC',
        (g.user['id'],)
    ).fetchall()

    return render_template('profile/feedback.html', results=results)