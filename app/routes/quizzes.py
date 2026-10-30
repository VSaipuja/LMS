import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import Course, Quiz, Question, Attempt, Enrollment

quizzes_bp = Blueprint('quizzes', __name__, url_prefix='/quizzes')


def student_enrolled(course_id):
    return Enrollment.query.filter_by(
        student_id=current_user.id, course_id=course_id
    ).first() is not None


@quizzes_bp.route('/course/<int:course_id>/create', methods=['GET', 'POST'])
@login_required
def create(course_id):
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id and not current_user.is_admin():
        abort(403)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        time_limit = int(request.form.get('time_limit', 30) or 30)
        passing_score = int(request.form.get('passing_score', 60) or 60)

        if not title:
            flash('Title is required.', 'danger')
            return render_template('quizzes/form.html', course=course, quiz=None)

        quiz = Quiz(
            title=title,
            description=description,
            course_id=course.id,
            time_limit_minutes=time_limit,
            passing_score=passing_score
        )
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz created. Now add questions.', 'success')
        return redirect(url_for('quizzes.manage_questions', quiz_id=quiz.id))

    return render_template('quizzes/form.html', course=course, quiz=None)


@quizzes_bp.route('/<int:quiz_id>/questions', methods=['GET', 'POST'])
@login_required
def manage_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.course.instructor_id != current_user.id and not current_user.is_admin():
        abort(403)

    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        option_a = request.form.get('option_a', '').strip()
        option_b = request.form.get('option_b', '').strip()
        option_c = request.form.get('option_c', '').strip()
        option_d = request.form.get('option_d', '').strip()
        correct = request.form.get('correct_option', 'A').upper()

        if not all([text, option_a, option_b, option_c, option_d]) or correct not in 'ABCD':
            flash('All fields required and correct option must be A/B/C/D.', 'danger')
        else:
            order = quiz.questions.count()
            q = Question(
                quiz_id=quiz.id,
                text=text,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_option=correct,
                order=order
            )
            db.session.add(q)
            db.session.commit()
            flash('Question added.', 'success')

        return redirect(url_for('quizzes.manage_questions', quiz_id=quiz.id))

    questions = quiz.questions.all()
    return render_template('quizzes/questions.html', quiz=quiz, questions=questions)


@quizzes_bp.route('/question/<int:question_id>/delete', methods=['POST'])
@login_required
def delete_question(question_id):
    q = Question.query.get_or_404(question_id)
    quiz = q.quiz
    if quiz.course.instructor_id != current_user.id and not current_user.is_admin():
        abort(403)
    db.session.delete(q)
    db.session.commit()
    flash('Question deleted.', 'info')
    return redirect(url_for('quizzes.manage_questions', quiz_id=quiz.id))


@quizzes_bp.route('/<int:quiz_id>/take', methods=['GET', 'POST'])
@login_required
def take(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if not current_user.is_student():
        flash('Only students can take quizzes.', 'danger')
        return redirect(url_for('courses.detail', course_id=quiz.course_id))

    if not student_enrolled(quiz.course_id):
        flash('You must enroll in the course first.', 'danger')
        return redirect(url_for('courses.detail', course_id=quiz.course_id))

    questions = quiz.questions.all()
    if not questions:
        flash('This quiz has no questions yet.', 'warning')
        return redirect(url_for('courses.detail', course_id=quiz.course_id))

    if request.method == 'POST':
        answers = {}
        correct = 0
        for q in questions:
            selected = request.form.get(f'q_{q.id}', '').upper()
            answers[str(q.id)] = selected
            if selected == q.correct_option:
                correct += 1

        total = len(questions)
        score = round((correct / total) * 100, 1) if total else 0
        passed = score >= quiz.passing_score

        attempt = Attempt(
            student_id=current_user.id,
            quiz_id=quiz.id,
            score=score,
            correct_count=correct,
            total_questions=total,
            answers_json=json.dumps(answers),
            passed=passed
        )
        db.session.add(attempt)
        db.session.commit()

        flash(f'Quiz submitted! Score: {score}% {"(Passed)" if passed else "(Failed)"}', 
              'success' if passed else 'warning')
        return redirect(url_for('quizzes.result', attempt_id=attempt.id))

    return render_template('quizzes/take.html', quiz=quiz, questions=questions)


@quizzes_bp.route('/result/<int:attempt_id>')
@login_required
def result(attempt_id):
    attempt = Attempt.query.get_or_404(attempt_id)
    if attempt.student_id != current_user.id and not current_user.is_instructor():
        abort(403)

    quiz = attempt.quiz
    questions = quiz.questions.all()
    answers = json.loads(attempt.answers_json or '{}')

    return render_template('quizzes/result.html',
                           attempt=attempt,
                           quiz=quiz,
                           questions=questions,
                           answers=answers)


@quizzes_bp.route('/<int:quiz_id>/attempts')
@login_required
def attempts_list(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.course.instructor_id != current_user.id and not current_user.is_admin():
        abort(403)

    attempts = (Attempt.query
                .filter_by(quiz_id=quiz.id)
                .order_by(Attempt.completed_at.desc())
                .all())
    return render_template('quizzes/attempts.html', quiz=quiz, attempts=attempts)
