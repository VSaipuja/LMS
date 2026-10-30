from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Course, Enrollment, Attempt, Quiz

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    courses = Course.query.filter_by(is_published=True).order_by(Course.created_at.desc()).limit(6).all()
    return render_template('index.html', courses=courses)


@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin():
        total_users = __import__('app.models', fromlist=['User']).User.query.count()
        total_courses = Course.query.count()
        total_quizzes = Quiz.query.count()
        return render_template('dashboard_admin.html',
                               total_users=total_users,
                               total_courses=total_courses,
                               total_quizzes=total_quizzes)

    if current_user.is_instructor():
        my_courses = Course.query.filter_by(instructor_id=current_user.id).all()
        return render_template('dashboard_instructor.html', courses=my_courses)

    # Student dashboard
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    enrolled_courses = [e.course for e in enrollments]
    recent_attempts = (Attempt.query
                       .filter_by(student_id=current_user.id)
                       .order_by(Attempt.completed_at.desc())
                       .limit(5)
                       .all())
    return render_template('dashboard_student.html',
                           courses=enrolled_courses,
                           attempts=recent_attempts)
