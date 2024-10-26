# routes.py
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import db, UserProfile, QuizScore
from .forms import UserProfileForm

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    if not user_profile:
        user_profile = UserProfile(user_id=current_user.id)
        db.session.add(user_profile)
        db.session.commit()

    form = UserProfileForm(obj=user_profile)
    if form.validate_on_submit():
        user_profile.bio = form.bio.data
        user_profile.location = form.location.data
        db.session.commit()
        flash('Profile updated successfully')
        return redirect(url_for('profile'))

    quiz_scores = QuizScore.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', form=form, quiz_scores=quiz_scores)
