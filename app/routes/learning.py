"""Add-on learning insights and study planner routes.

This module intentionally reuses the existing LMS models so the upgrade does not
require destructive database changes or a migration of existing student data.
"""
from collections import defaultdict
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Attempt, Enrollment, Lesson, LessonProgress

learning_bp = Blueprint('learning', __name__, url_prefix='/learning')


@learning_bp.route('/insights')
@login_required
def insights():
    if not current_user.is_student():
        flash('Learning insights are available to student accounts.', 'info')
        return redirect(url_for('main.dashboard'))

    attempts = (Attempt.query.filter_by(student_id=current_user.id)
                .order_by(Attempt.completed_at.desc()).all())
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    course_ids = [item.course_id for item in enrollments]

    # Group actual quiz attempts by quiz. A low average is a signal to revise the
    # quiz/course material; it is not presented as a definitive topic diagnosis.
    grouped = defaultdict(list)
    for attempt in attempts:
        grouped[attempt.quiz_id].append(attempt.score)

    quiz_insights = []
    for quiz_id, scores in grouped.items():
        latest = next(a for a in attempts if a.quiz_id == quiz_id)
        average = round(sum(scores) / len(scores), 1)
        quiz_insights.append({
            'title': latest.quiz.title,
            'course': latest.quiz.course.title,
            'average': average,
            'attempts': len(scores),
            'suggestion': ('Revisit the lesson and retry the quiz.' if average < 60
                           else 'Good progress. Try a harder practice set.' if average < 80
                           else 'Strong result. Revise again next week.')
        })
    quiz_insights.sort(key=lambda item: item['average'])

    total_lessons = Lesson.query.filter(Lesson.course_id.in_(course_ids)).count() if course_ids else 0
    completed_lessons = LessonProgress.query.filter_by(
        student_id=current_user.id, completed=True
    ).join(Lesson, LessonProgress.lesson_id == Lesson.id).filter(
        Lesson.course_id.in_(course_ids)
    ).count() if course_ids else 0
    progress_percent = round(completed_lessons * 100 / total_lessons) if total_lessons else 0
    average_score = round(sum(a.score for a in attempts) / len(attempts), 1) if attempts else 0

    return render_template(
        'learning/insights.html',
        quiz_insights=quiz_insights,
        total_lessons=total_lessons,
        completed_lessons=completed_lessons,
        progress_percent=progress_percent,
        average_score=average_score,
        total_attempts=len(attempts),
    )


@learning_bp.route('/study-planner')
@login_required
def study_planner():
    if not current_user.is_student():
        flash('The study planner is available to student accounts.', 'info')
        return redirect(url_for('main.dashboard'))
    return render_template('learning/study_planner.html')
