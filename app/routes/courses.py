from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import Course, Enrollment, User, DEPARTMENTS, Lesson, LessonProgress

courses_bp = Blueprint('courses', __name__, url_prefix='/courses')


@courses_bp.route('/')
def list_courses():
    dept_filter = request.args.get('dept', '').strip().upper()
    query = Course.query.filter_by(is_published=True)

    if current_user.is_authenticated and current_user.is_student():
        query = query.filter(Course.department.in_([current_user.department, 'GENERAL']))
    elif dept_filter and dept_filter != 'ALL':
        query = query.filter_by(department=dept_filter)

    courses = query.order_by(Course.department, Course.created_at.desc()).all()

    enrolled_ids = set()
    if current_user.is_authenticated and current_user.is_student():
        enrolled_ids = {e.course_id for e in current_user.enrollments}

    return render_template('courses/list.html',
                           courses=courses,
                           enrolled_ids=enrolled_ids,
                           departments=DEPARTMENTS,
                           current_dept=dept_filter or 'ALL')


@courses_bp.route('/<int:course_id>')
def detail(course_id):
    course = Course.query.get_or_404(course_id)

    if current_user.is_authenticated and current_user.is_student():
        if not current_user.can_access_course(course):
            flash('This course is not available for your department.', 'danger')
            return redirect(url_for('courses.list_courses'))

    is_enrolled = False
    if current_user.is_authenticated and current_user.is_student():
        is_enrolled = Enrollment.query.filter_by(
            student_id=current_user.id, course_id=course.id
        ).first() is not None

    lessons = course.lessons.order_by(Lesson.order).all()
    lesson_status = []
    for lesson in lessons:
        unlocked = False
        passed_quiz = False
        if current_user.is_authenticated:
            if current_user.is_instructor() or current_user.is_admin():
                unlocked = True
            elif is_enrolled:
                unlocked = lesson.is_unlocked_for(current_user)
            if lesson.quiz_id and current_user.is_authenticated:
                passed_quiz = current_user.has_passed_quiz(lesson.quiz_id)
        lesson_status.append({
            'lesson': lesson,
            'unlocked': unlocked,
            'passed_quiz': passed_quiz,
        })

    return render_template('courses/detail.html',
                           course=course,
                           is_enrolled=is_enrolled,
                           lesson_status=lesson_status)


@courses_bp.route('/<int:course_id>/lesson/<int:lesson_id>')
@login_required
def watch_lesson(course_id, lesson_id):
    course = Course.query.get_or_404(course_id)
    lesson = Lesson.query.filter_by(id=lesson_id, course_id=course_id).first_or_404()

    if current_user.is_student():
        if not current_user.can_access_course(course):
            flash('This course is not available for your department.', 'danger')
            return redirect(url_for('courses.list_courses'))
        enrolled = Enrollment.query.filter_by(
            student_id=current_user.id, course_id=course.id
        ).first()
        if not enrolled:
            flash('Enroll in the course first.', 'danger')
            return redirect(url_for('courses.detail', course_id=course.id))
        if not lesson.is_unlocked_for(current_user):
            flash('Pass the previous lesson quiz to unlock this video.', 'warning')
            return redirect(url_for('courses.detail', course_id=course.id))

    progress = LessonProgress.query.filter_by(student_id=current_user.id, lesson_id=lesson.id).first() if current_user.is_student() else None
    return render_template('courses/lesson.html', course=course, lesson=lesson, progress=progress)


@courses_bp.route('/<int:course_id>/lesson/<int:lesson_id>/complete', methods=['POST'])
@login_required
def complete_lesson(course_id, lesson_id):
    course = Course.query.get_or_404(course_id)
    lesson = Lesson.query.filter_by(id=lesson_id, course_id=course_id).first_or_404()
    if not current_user.is_student():
        abort(403)
    if not current_user.can_access_course(course):
        abort(403)
    enrolled = Enrollment.query.filter_by(student_id=current_user.id, course_id=course.id).first()
    if not enrolled or not lesson.is_unlocked_for(current_user):
        abort(403)

    progress = LessonProgress.query.filter_by(student_id=current_user.id, lesson_id=lesson.id).first()
    if not progress:
        progress = LessonProgress(student_id=current_user.id, lesson_id=lesson.id)
        db.session.add(progress)
    if not progress.completed:
        from datetime import datetime
        progress.completed = True
        progress.completed_at = datetime.utcnow()
        db.session.commit()
        flash('Lesson marked as completed. Keep going!', 'success')
    else:
        flash('This lesson is already marked as completed.', 'info')
    return redirect(url_for('courses.watch_lesson', course_id=course.id, lesson_id=lesson.id))


@courses_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_instructor():
        flash('Only instructors can create courses.', 'danger')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        department = request.form.get('department', 'GENERAL')
        valid_depts = [d[0] for d in DEPARTMENTS]
        if department not in valid_depts:
            department = 'GENERAL'
        if not title:
            flash('Title is required.', 'danger')
            return render_template('courses/form.html', course=None, departments=DEPARTMENTS)
        course = Course(
            title=title,
            description=description,
            department=department,
            instructor_id=current_user.id
        )
        db.session.add(course)
        db.session.commit()
        flash('Course created. Add lessons with videos next.', 'success')
        return redirect(url_for('courses.detail', course_id=course.id))

    return render_template('courses/form.html', course=None, departments=DEPARTMENTS)


@courses_bp.route('/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(course_id):
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id and not current_user.is_admin():
        abort(403)

    if request.method == 'POST':
        course.title = request.form.get('title', '').strip()
        course.description = request.form.get('description', '').strip()
        course.department = request.form.get('department', course.department)
        course.is_published = bool(request.form.get('is_published'))
        valid_depts = [d[0] for d in DEPARTMENTS]
        if course.department not in valid_depts:
            course.department = 'GENERAL'
        if not course.title:
            flash('Title is required.', 'danger')
            return render_template('courses/form.html', course=course, departments=DEPARTMENTS)
        db.session.commit()
        flash('Course updated.', 'success')
        return redirect(url_for('courses.detail', course_id=course.id))

    return render_template('courses/form.html', course=course, departments=DEPARTMENTS)


@courses_bp.route('/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll(course_id):
    if not current_user.is_student():
        flash('Only students can enroll in courses.', 'danger')
        return redirect(url_for('courses.detail', course_id=course_id))

    course = Course.query.get_or_404(course_id)
    if not current_user.can_access_course(course):
        flash('This course is not available for your department.', 'danger')
        return redirect(url_for('courses.list_courses'))

    existing = Enrollment.query.filter_by(student_id=current_user.id, course_id=course.id).first()
    if existing:
        flash('You are already enrolled.', 'info')
    else:
        enrollment = Enrollment(student_id=current_user.id, course_id=course.id)
        db.session.add(enrollment)
        db.session.commit()
        flash(f'Successfully enrolled in "{course.title}"! Start with Lesson 1.', 'success')

    return redirect(url_for('courses.detail', course_id=course.id))


@courses_bp.route('/<int:course_id>/delete', methods=['POST'])
@login_required
def delete(course_id):
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id and not current_user.is_admin():
        abort(403)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted.', 'info')
    return redirect(url_for('main.dashboard'))
